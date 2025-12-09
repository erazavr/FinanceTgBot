import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from db import db_start
from expenses import get_end_of_day_expenses
from handlers import router

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
MY_CHAT_ID = int(getenv("MY_CHAT_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def send_midday_reminder():
    await bot.send_message(
        MY_CHAT_ID,
        "Эй, братан, не забудь внести сегодняшние расходы 💸",
    )


async def send_end_of_day_summary():
    try:
        today_expenses = await get_end_of_day_expenses(MY_CHAT_ID)
    except Exception as e:
        await bot.send_message(MY_CHAT_ID, f"Не смог посчитать расходы за сегодня 🥲\nОшибка: {e}")
        return

    await bot.send_message(
        MY_CHAT_ID,
        f"Итоги за сегодня:\n\n{today_expenses}",
    )


async def main() -> None:
    dp.include_router(router)

    scheduler = AsyncIOScheduler(timezone="Asia/Bishkek")

    scheduler.add_job(send_midday_reminder, "cron", hour=17, minute=0)
    scheduler.add_job(send_end_of_day_summary, "cron", hour=23, minute=0)

    scheduler.start()

    # Создание таблицы
    await db_start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
