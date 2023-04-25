from aiogram import Router, types

from aiogram.filters import Command
from loguru import logger

from objects.user import users
from sql.base import db_create
from middlewares.basic import UserIsAdminMiddleware

router = Router()
router.message.middleware(UserIsAdminMiddleware())

@router.message(Command(commands=["db_init"]))
async def init_db(message: types.Message):
    id = message.from_user.id
    logger.warning(f"{id} is creating the database")
    users.clear()
    await db_create()
