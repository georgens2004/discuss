import asyncio
import config

from aiogram import Bot, Dispatcher

from loguru import logger
import logging


logging.basicConfig(level = "INFO")

bot = Bot(token = config.BOT_API_TOKEN, parse_mode='html')
dp = Dispatcher()


async def main():

    logger.add('logs/log.txt', 
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            level="DEBUG")
    
    from handlers import main, admin

    dp.include_router(main.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates = True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
