import asyncio
import asyncpg
from aiogram import Router, types, html

from aiogram.filters.base import Filter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from loguru import logger

router = Router()
router.message.filter(content_types = "text")

# Home page

@router.message(Command(commands=["start", "main"]))
async def home_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} --> home page")
    await state.clear()
    await message.answer(
        (
            "Я снова живу!"
        )
    )


# Help page

@router.message(Command(commands=["help"]))
async def help_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} --> start page")
    await state.clear()
    await message.answer(
        (
            "Создай тему для обсуждения, открой его, жди собеседника, \n"+
            "либо ищи подходящую для тебя тему и начинай общаться"
        )
    )

@router.message(Command(commands=["stop"]))
async def stop_discussion_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} stopped discussion")
    await state.clear()
    await message.answer(
        (
            ""
        )
    )
