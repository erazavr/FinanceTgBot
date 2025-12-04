import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from db import db_start
from handlers import router

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


async def main() -> None:
    bot = Bot(token=TOKEN)
    dp.include_router(router)
    # Создание таблицы
    await db_start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
