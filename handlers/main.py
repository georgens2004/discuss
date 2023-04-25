import asyncio
import asyncpg
from aiogram import Router, types, html
from aiogram.filters.base import Filter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from loguru import logger
from emoji import emojize

from middlewares.basic import LoadUserMiddleware, NotInDiscussionMiddleware

router = Router()
router.message.middleware(LoadUserMiddleware())
router.message.middleware(NotInDiscussionMiddleware())

# Home page

@router.message(Command(commands=["start", "main", "home"]))
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
            "Создай тему для обсуждения, открой его, жди собеседника. \n"+
            "Либо ищи подходящую для тебя тему и начинай общаться"
        )
    )

@router.message(Command(commands=["stop"]))
async def stop_discussion_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} stopped discussion")
    await state.clear()
    topic_rating_kb = InlineKeyboardBuilder()
    topic_rating_kb.add(types.InlineKeyboardButton(
        text = emojize(":thumbs_up"),
        callback_data = "like"
    ))
    topic_rating_kb.add(types.InlineKeyboardButton(
        text = emojize("thumbs_down"),
        callback_data = "dislike"
    ))
    await message.answer(
        (
            "Вы остановили общение. Можете оценить разговор"
        ),
        reply_markup=topic_rating_kb.as_markup()
    )

