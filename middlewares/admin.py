from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from loguru import logger

from config import ADMIN_TG_ID


class UserIsAdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        id = data["event_from_user"].id
        if str(data["event_from_user"].id) != str(ADMIN_TG_ID):
            #logger.warning(f"{id} tried to access admin functional")
            #await event.answer(
            #    "Вам недоступен этот функционал"
            #)
            return None
        return await handler(event, data)
 