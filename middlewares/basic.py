from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from loguru import logger

from sql.base import db_create_pool
from objects.user import User, users
from config import ADMIN_TG_ID

class InDiscussionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        id = data["event_from_user"].id
        if users[id].active_topic == -1:
            return None
        return await handler(event, data)


class NotInDiscussionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        id = data["event_from_user"].id
        if users[id].active_topic != -1:
            return None
        return await handler(event, data)


class LoadUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = data["event_from_user"].id
        if user_id not in users:
            db = await db_create_pool()
            user = await db.fetchrow(f"SELECT * FROM users WHERE id = {user_id}")
            if user is None:
                await db.execute(f"INSERT INTO users (id) VALUES ({user_id})")
                user = await db.fetchrow(f"SELECT * FROM users WHERE id = {user_id}")
            
            users[user_id] = User(user)
            await db.close()

        return await handler(event, data)


class UserIsAdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if str(data["event_from_user"].id) == str(ADMIN_TG_ID):
            return await handler(event, data)
        
        return None
