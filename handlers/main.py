from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove
from loguru import logger
from emoji import emojize

from init import bot
from filters.basic import NotInDiscussionFilter
from middlewares.loaders import LoadUsersMiddleware, LoadTopicsMiddleware
from handlers.states import HomeState, SurfingTopicsState
from objects.user import users
from objects.topic import topics

router = Router()
router.message.outer_middleware(LoadUsersMiddleware())
router.message.outer_middleware(LoadTopicsMiddleware())
router.message.filter(NotInDiscussionFilter())


async def send_home_page(id, state):
    logger.info(f"{id} --> home page")
    await state.clear()
    home_page_kb = ReplyKeyboardBuilder()
    home_page_kb.add(types.KeyboardButton(text = "Мои темы"))
    await bot.send_message(id,
        (
            "Привет!\n"+
            "/home - главная страница (вот эта)\n"+
            "/start - поиск тем для обсуждения\n"+
            "/help - руководство по использованию\n"
            "/ready - стать готовым к обсуждению своих тем (с вами можно будет начать диалог)\n"+
            "/busy - с вами нельзя будет обсудить ваши темы"
        ), 
        reply_markup=home_page_kb.as_markup(resize_keyboard=True)
    )
    await state.set_state(HomeState.main)


async def send_surfing_topics_page(id, state):
    await state.clear()
    await state.set_state(SurfingTopicsState.choosing)
    topic_id = users[id].get_random_topic()
    await state.update_data(topic_id = topic_id)
    if topic_id == -1:
        await bot.send_message(id,
            (
                "Нет открытых тем для разговора :("
            )
        )
        return
    msg = await bot.send_message(id, 
        (
            "Случайно подобранная тема:\n\n"+
            topics[topic_id].text
        )
    )
    reports_kb = InlineKeyboardBuilder()
    reports_kb.add(types.InlineKeyboardButton(
        text = "Report",
        callback_data = str(topic_id) + "report" + str(msg.message_id)
    ))
    await bot.edit_message_reply_markup(id, msg.message_id, reply_markup=reports_kb.as_markup())

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
        reply_markup=topic_choosing_kb.as_markup(resize_keyboard=True)
    )
    await send_surfing_topics_page(id, state)


@router.callback_query(SurfingTopicsState.choosing, 
                       lambda callback: "report" in callback.data)
async def report_topic_callback(callback: types.CallbackQuery, state: FSMContext):
    id = callback.from_user.id
    idx1 = 0
    while callback.data[idx1] != "r":
        idx1 += 1
    idx2 = 0
    while callback.data[idx2] != "t":
        idx2 += 1
    idx2 += 1

    topic_id = int(callback.data[:idx1])
    msg_id = int(callback.data[idx2:])

    await bot.edit_message_reply_markup(id, msg_id, reply_markup=None)
    if topic_id not in topics:
        await callback.answer()
        return
    logger.info(f"{id} has reported topic {topic_id}")
    await topics[topic_id].report()
    await callback.answer("Жалоба отправлена")


@router.message(SurfingTopicsState.choosing,
                lambda message: message.text == "Начать общение")
async def start_discussion_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    topic_id = (await state.get_data())["topic_id"]
    if topic_id not in topics:
        await message.answer(
            (
                "Темы не существует"
            )
        )
        return

    await message.answer(
        (
            "Вы начали общение\n"+
            "/stop - завершить диалог\n"+
            "/topic - напомнить тему разговора"
        ),
        reply_markup=ReplyKeyboardRemove()
    )
    await users[id].start_discussion(topic_id)
    await bot.send_message(users[id].companion,
        (
            "С вами начали разговор по теме:\n"+
            topics[topic_id].text + "\n"+
            f"Rating: {topics[topic_id].rating}\n\n"+
            "/stop - завершить диалог\n"+
            "/topic - напомнить тему разговора"
        ),
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(SurfingTopicsState.choosing, 
                lambda message: message.text == "Некст")
async def surfing_topics_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_surfing_topics_page(id, state)


@router.message(SurfingTopicsState.choosing,
                lambda message: message.text == "На главную")
async def back_from_surfing_topics_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    await send_home_page(id, state)

# Help page

@router.message(Command(commands=["help"]))
async def help_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} --> help page")
    await state.clear()
    await message.answer(
        (
            "Создай тему для обсуждения, открой его, жди собеседника. \n"+
            "Либо ищи подходящую для тебя тему и начинай общаться\n"+
            "/home - главная страница\n"+
            "/start - начать поиск тем для обсуждения\n"+
            "/topic - напомнить тему обсуждения, находясь в диалоге\n"
            "/help - страница помощи (вот эта)\n"
            "/ready - стать готовым к обсуждению своих тем (с вами можно будет начать диалог)\n"+
            "/busy - с вами нельзя будет обсудить ваши темы"
        )
    )

# Ready / busy states

@router.message(Command(commands=["ready"]))
async def get_ready_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} set his/her state as 'ready'")
    await state.clear()
    await message.answer(
        (
            "Теперь вы открыты для обсуждения своих тем"
        )
    )
    await users[id].get_ready()


@router.message(Command(commands=["busy"]))
async def get_busy_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} set his/her state as 'busy'")
    await state.clear()
    await message.answer(
        (
            "Теперь вы закрыты для обсуждения своих тем, с вами не смогут начать диалог"
        )
    )
    await users[id].get_busy()
