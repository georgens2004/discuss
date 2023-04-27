from aiogram import Router, types
from aiogram.filters.base import Filter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from loguru import logger
from emoji import emojize

from init import bot
from middlewares.basic import NotInDiscussionMiddleware
from middlewares.loaders import LoadUsersMiddleware, LoadTopicsMiddleware
from handlers.states import HomeState, SurfingTopicsState
from objects.user import users
from objects.topic import topics

router = Router()
router.message.middleware(LoadUsersMiddleware())
router.message.middleware(LoadTopicsMiddleware())
router.message.middleware(NotInDiscussionMiddleware())


async def send_home_page(id, state):
    logger.info(f"{id} --> home page")
    await state.clear()
    home_page_kb = ReplyKeyboardBuilder()
    home_page_kb.add(types.KeyboardButton(text = "Мои темы"))
    await bot.send_message(id,
        (
            "Я снова живу!\n"+
            "/home - главная страница\n"+
            "/start - поиск тем для обсуждения\n"+
            "/help - помощь по использованию"
        ), 
        reply_markup=home_page_kb.as_markup()
    )
    await state.set_state(HomeState.main)


async def send_surfing_topics_page(id, state):
    await state.clear()
    await state.set_state(SurfingTopicsState.choosing)
    topic_id = await users[id].get_random_topic()
    if topic_id == -1:
        await bot.send_message(id,
            (
                "Нет открытых тем для разговора :("    
            )
        )
        return

    reports_kb = InlineKeyboardBuilder()
    reports_kb.add(types.InlineKeyboardButton(
        text = "Report",
        callback_data = "report"
    ))
    await bot.send_message(id, 
        (
            "Случайно подобранная тема:\n\n"+
            topics[topic_id].text
        ),
        reply_markup=reports_kb.as_markup()
    )

# Home page

@router.message(Command(commands=["home"]))
async def home_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_home_page(id, state)


# Topic surfing page

@router.message(Command(commands=["start"]))
async def start_surfing_topics_page(message: types.Message, state: FSMContext):
    await state.clear()
    id = message.from_user.id
    topic_choosing_kb = ReplyKeyboardBuilder()
    topic_choosing_kb.add(types.KeyboardButton(text = "Начать общение"))
    topic_choosing_kb.add(types.KeyboardButton(text = "Некст"))
    topic_choosing_kb.add(types.KeyboardButton(text = "На главную"))
    await message.answer(
        (
            "Поиск тем для обсуждения:"
        ),
        reply_markup=topic_choosing_kb.as_markup()
    )
    await send_surfing_topics_page(id, state)


@router.message(SurfingTopicsState.choosing, 
                lambda message: message.text == "Некст")
async def surfing_topics_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_surfing_topics_page(id, state)


@router.message(SurfingTopicsState.choosing,
                lambda message: message.text == "На главную")
async def from_surfing_topics_to_main_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_home_page(id, state)

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

