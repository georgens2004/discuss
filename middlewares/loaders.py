from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from sql.base import db_create_pool, db_load_all_topics
from objects.user import User, users
from config import ADMIN_TG_ID
from objects.topic import topics


class LoadUsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if len(users) == 0:
            db = await db_create_pool()
            all_users = await db.fetch("SELECT * FROM users")
            for user in all_users:
                users[user["id"]] = User(user)
            await db.close()
        user_id = data["event_from_user"].id
        if user_id not in users:
            db = await db_create_pool()
            await db.execute(f"INSERT INTO users (id) VALUES ({user_id})")
            user = await db.fetchrow(f"SELECT * FROM users WHERE id = {user_id}")
            users[user_id] = User(user)
            await db.close()

        return await handler(event, data)

class LoadTopicsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if len(topics) == 0:
            await db_load_all_topics()
        return await handler(event, data)
