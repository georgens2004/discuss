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
            await event.answer(
                "Вы находитесь в разговоре. Завершите его, чтобы можно было далее пользоваться ботом.\n"+
                "/stop для завершения диалога"
            )
            return None
        return await handler(event, data)



class UserIsAdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if str(data["event_from_user"].id) != str(ADMIN_TG_ID):
            await event.answer(
                "Вам недоступен этот функционал"
            )
            return None
        return await handler(event, data)
