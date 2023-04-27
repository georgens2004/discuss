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
from filters.basic import NotInDiscussionFilter
from middlewares.loaders import LoadUsersMiddleware, LoadTopicsMiddleware
from handlers.states import HomeState, MyTopicsState, SurfingTopicsState
from handlers.main import send_home_page
from objects.user import users
from objects.topic import topics

router = Router()
router.message.outer_middleware(LoadUsersMiddleware())
router.message.outer_middleware(LoadTopicsMiddleware())
router.message.filter(NotInDiscussionFilter())


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
            f"Discussed: {topic.discussed_times}\n"+
            f"Status: {status}\n\n"
        )
    topics_kb.add(types.KeyboardButton(text = "Создать новую"))
    topics_kb.add(types.KeyboardButton(text = "Назад"))
    await bot.send_message(id, msg, reply_markup=topics_kb.as_markup(resize_keyboard=True))
    await state.set_state(MyTopicsState.main)


async def send_topic_page(id, state, topic_id):
    await state.clear()
    topic_kb = ReplyKeyboardBuilder()
    topic_kb.add(types.KeyboardButton(text = "Открыть"))
    topic_kb.add(types.KeyboardButton(text = "Закрыть"))
    topic_kb.add(types.KeyboardButton(text = "Удалить тему"))
    topic_kb.add(types.KeyboardButton(text = "Назад"))
    topic_kb.adjust(2, 2)
    topic = topics[topic_id]
    status = "opened" if topic.opened else "closed"
    msg = (
        f"{topic.text}\n"+
        f"Rating: {topic.rating}\n"+
        f"Discussed: {topic.discussed_times}\n"+
        f"Status: {status}\n\n"
    )
    await bot.send_message(id, msg, reply_markup=topic_kb.as_markup(resize_keyboard=True))
    await state.set_state(MyTopicsState.topic)
    await state.update_data(topic_id = topic_id)


@router.message(HomeState.main,
                lambda message: message.text == "Мои темы")
async def my_topics_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_my_topics_page(id, state)


@router.message(MyTopicsState.main, 
                lambda message: message.text.isdigit())
async def topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    idx = int(message.text) - 1
    if not (0 <= idx and idx < len(users[id].topics)):
        return
    topic_id = users[id].topics[int(message.text) - 1]
    await send_topic_page(id, state, topic_id)


@router.message(MyTopicsState.main,
                lambda message: message.text == "Создать новую")
async def create_topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if len(users[id].topics) == config.USER_MAX_TOPICS:
        await message.answer(
            (
                "У вас максимально доступное число созданных тем"
            )
        )
        return
    await message.answer(
        (
            "Придумайте тему для обсуждения\n"+
            f"Число символов должно быть от {config.TOPIC_MIN_LENGTH} до {config.TOPIC_MAX_LENGTH}"
        ),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(MyTopicsState.creating)


@router.message(MyTopicsState.main,
                lambda message: message.text == "Назад")
async def back_from_my_topics_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_home_page(id, state)


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


@router.message(MyTopicsState.topic,
                lambda message: message.text == "Открыть")
async def open_topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    topic_id = (await state.get_data())["topic_id"]
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
    topic_id = (await state.get_data())["topic_id"]
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
    topic_id = (await state.get_data())["topic_id"]
    if topic_id not in topics:
        return
    await users[id].delete_topic(topic_id)
    await message.answer(
        (
            "Вы удалили тему"
        )
    )
    await send_my_topics_page(id, state)


@router.message(MyTopicsState.topic,
                lambda message: message.text == "Назад")
async def back_from_topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_my_topics_page(id, state)
