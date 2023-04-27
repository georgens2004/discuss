import asyncio
import asyncpg
from aiogram import Router, types
from aiogram.filters.base import Filter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove
from loguru import logger
import config

from init import bot
from middlewares.basic import NotInDiscussionMiddleware
from middlewares.loaders import LoadUsersMiddleware, LoadTopicsMiddleware
from handlers.states import HomeState, MyTopicsState, SurfingTopicsState
from objects.user import users
from objects.topic import topics

router = Router()
router.message.middleware(LoadUsersMiddleware())
router.message.middleware(LoadTopicsMiddleware())
router.message.middleware(NotInDiscussionMiddleware())


async def send_my_topics_page(id, state):
    await state.clear()
    topics_kb = ReplyKeyboardBuilder()
    user = users[id]
    msg = "Ваши темы для обсуждения:\n\n"
    for i in range(len(user.topics)):
        topics_kb.add(types.KeyboardButton(text = f"{i + 1}"))
        topic = topics[user.topics[i]]
        status = "opened" if topic.opened else "closed"
        msg += (
            f"{i + 1}: {topic.text}\n"+
            f"Rating: {topic.rating}\n"+
            f"Discussed: {topic.discussed_times}"+
            f"Reports: {topic.reports}\n"+
            f"Status: {status}\n\n"
        )
    topics_kb.add(types.KeyboardButton(text = "Создать новую"))
    await bot.send_message(id, msg, reply_markup=topics_kb.as_markup())
    await state.set_state(MyTopicsState.main)


async def send_topic_page(id, state, topic_id):
    await state.clear()
    topic_kb = ReplyKeyboardBuilder()
    topic_kb.add(types.KeyboardButton(text = "Открыть"))
    topic_kb.add(types.KeyboardButton(text = "Закрыть"))
    topic_kb.add(types.KeyboardButton(text = "Удалить тему"))
    topic = topics[topic_id]
    status = "opened" if topic.opened else "closed"
    msg = (
        f"{topic.text}\n"+
        f"Rating: {topic.rating}\n"+
        f"Discussed: {topic.discussed_times}"+
        f"Reports: {topic.reports}\n"+
        f"Status: {status}\n\n"
    )
    await bot.send_message(id, msg, reply_markup=topic_kb.as_markup())
    await state.set_state(MyTopicsState.topic)
    await state.update_data(topic_id = topic_id)


@router.message(HomeState.main,
                lambda message: message.text == "Мои темы")
async def my_topics_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_my_topics_page(id, state)

@router.message(MyTopicsState.main,
                lambda message: message.text == "Создать новую")
async def create_topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await message.answer(
        (
            "Придумайте тему для обсуждения\n"+
            f"Число символов должно быть от {config.TOPIC_MIN_LENGTH} до {config.TOPIC_MAX_LENGTH}"
        ),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(MyTopicsState.creating)

@router.message(MyTopicsState.creating)
async def handle_topic_text_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    text_satisfies_conditions = config.TOPIC_MIN_LENGTH <= len(message.text) and len(message.text) <= config.TOPIC_MAX_LENGTH
    if text_satisfies_conditions:
        await users[id].create_topic(message.text)
        await message.answer(
            (
                "Вы создали новую тему для разговора.\n"+
                "Откройте её, чтобы люди смогли начать общение с вами по ней"
            )
        )
        await send_my_topics_page(id, state)
    else:
        await message.answer(
            (
                "Текст не подходит под требования. Попробуйте ещё раз"
            )
        )

@router.message(MyTopicsState.main, 
                lambda message: message.text != "Создать новую")
async def topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    topic_id = users[id].topics[int(message.text)]
    await send_topic_page(id, state, topic_id)

@router.message(MyTopicsState.topic,
                lambda message: message.text == "Открыть")
async def open_topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    topic_id = state.get_data()["topic_id"]
    await users[id].open_topic(topic_id)
    await message.answer(
        (
            "Тема открыта. Теперь другие люди будут находить её в поиске"
        )
    )
    await send_topic_page(id, state, topic_id)

@router.message(MyTopicsState.topic,
                lambda message: message.text == "Закрыть")
async def close_topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    topic_id = state.get_data()["topic_id"]
    await users[id].close_topic(topic_id)
    await message.answer(
        (
            "Тема закрыта. Больше никто не будет получать её в поиске"
        )
    )
    await send_topic_page(id, state, topic_id)

@router.message(MyTopicsState.topic,
                lambda message: message.text == "Удалить тему")
async def delete_topic_page(message:types.Message, state: FSMContext):
    id = message.from_user.id
    topic_id = state.get_data(topic_id)
