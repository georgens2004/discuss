from aiogram import Router, types, filters
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from loguru import logger
from emoji import emojize

from init import bot
from filters.basic import InDiscussionFilter
from middlewares.loaders import LoadUsersMiddleware, LoadTopicsMiddleware, AntiSpamMiddleware
from handlers.states import HomeState, SurfingTopicsState
from objects.user import users
from objects.topic import topics

router = Router()
router.message.outer_middleware(LoadUsersMiddleware())
router.message.outer_middleware(LoadTopicsMiddleware())
router.message.middleware(AntiSpamMiddleware())
router.message.filter(InDiscussionFilter())


@router.message(Command(commands="topic"))
async def recall_topic_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    topic_id = users[id].active_topic
    await message.answer(
        (
            "<i>"+
            "Тема разговора:\n\n"+
            "</i>"+
            topics[topic_id].text
        )
    )


@router.message(Command(commands=["stop"]))
async def stop_discussion_page(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} stopped discussion")
    await state.clear()
    topic_id = users[id].active_topic
    msg = None
    chat_id = None
    if topics[topic_id].author == id:
        await message.answer(
            (
                "<i>"+
                "Вы остановили общение\n"+
                "/home - вернуться на главную страницу"+
                "</i>"
            )
        )
        msg = await bot.send_message(users[id].companion,
            (
                "<i>"+
                "Диалог остановлен. Можете оценить разговор\n"+
                "/start - поиск новой темы\n"+
                "/home - вернуться на главную страницу"+
                "</i>"
            )
        )
        chat_id = users[id].companion
    else:
        msg = await message.answer(
            (
                "<i>"+
                "Вы остановили общение. Можете оценить разговор\n"+
                "/start - поиск новой темы\n"+
                "/home - вернуться на главную страницу"+
                "</i>"
            )
        )
        await bot.send_message(users[id].companion,
            (
                "<i>"+
                "Диалог остановлен.\n"+
                "/start - поиск новой темы\n"+
                "/home - вернуться на главную страницу"+
                "</i>"
            ),
        )
        chat_id = id

    topic_rating_kb = InlineKeyboardBuilder()
    topic_rating_kb.add(types.InlineKeyboardButton(
        text = emojize(":thumbs_up:"),
        callback_data = str(topic_id) + "|upvote|" + str(msg.message_id)
    ))
    topic_rating_kb.add(types.InlineKeyboardButton(
        text = emojize(":thumbs_down:"),
        callback_data = str(topic_id) + "|downvote|" + str(msg.message_id)
    ))
    await bot.edit_message_reply_markup(chat_id, msg.message_id, reply_markup=topic_rating_kb.as_markup())
    await users[id].stop_discussion()


@router.callback_query(lambda callback: "upvote" in callback.data)
async def upvote_topic_callback(callback: types.CallbackQuery, state: FSMContext):
    # weirdest stuff here, really don't know how to pass information better
    id = callback.from_user.id
    idx1 = 0
    while callback.data[idx1] != "|":
        idx1 += 1
    idx2 = len(callback.data) - 1
    while callback.data[idx2] != "|":
        idx2 -= 1
    idx2 += 1

    topic_id = int(callback.data[:idx1])
    msg_id = int(callback.data[idx2:])

    await bot.edit_message_reply_markup(id, msg_id, reply_markup=None)
    if topic_id in topics:
        await topics[topic_id].change_rating(1)
    await callback.answer("Рейтинг темы +1")


@router.callback_query(lambda callback: "downvote" in callback.data)
async def downvote_topic_callback(callback: types.CallbackQuery, state: FSMContext):
    id = callback.from_user.id
    idx1 = 0
    while callback.data[idx1] != "|":
        idx1 += 1
    idx2 = len(callback.data) - 1
    while callback.data[idx2] != "|":
        idx2 -= 1
    idx2 += 1

    topic_id = int(callback.data[:idx1])
    msg_id = int(callback.data[idx2:])

    await bot.edit_message_reply_markup(id, msg_id, reply_markup=None)
    if topic_id in topics:
        await topics[topic_id].change_rating(-1)
    await callback.answer("Рейтинг темы -1")


@router.message(filters.Text)
async def chatting_text_message_handler(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} sent message to companion {users[id].companion}")
    await bot.send_message(users[id].companion, message.text)


@router.message(filters.MagicData)
async def chatting_text_message_handler(message: types.Message, state: FSMContext):
    id = message.from_user.id
    logger.info(f"{id} sent message to companion {users[id].companion}")
    await bot.send_message(users[id].companion, message.text)
