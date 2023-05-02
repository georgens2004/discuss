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

