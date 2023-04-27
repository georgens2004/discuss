from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.filters import Filter
from aiogram.types import Message
from loguru import logger

from sql.base import db_create_pool
from objects.user import User, users
from config import ADMIN_TG_ID

class InDiscussionFilter(Filter):
    async def __call__(self, message: Message):
        return users[message.from_user.id].active_topic != -1
    
class NotInDiscussionFilter(Filter):
    async def __call__(self, message: Message):
        return users[message.from_user.id].active_topic == -1

'''
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
'''


   
