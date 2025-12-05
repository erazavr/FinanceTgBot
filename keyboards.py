from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import get_db

cancel_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]])

async def inline_categories(chat_id: int):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM categories WHERE chat_id IS NULL OR chat_id = ?", (chat_id,))
    categories = cur.fetchall()
    db.close()

    keyboard = InlineKeyboardBuilder()

    for category in categories:
        category_id = category[0]
        category_name = category[1]

        keyboard.add(InlineKeyboardButton(text=category_name, callback_data=f'cat:{category_id}'))

    keyboard.add(InlineKeyboardButton(text='❌ Отмена', callback_data='cancel'))

    return keyboard.adjust(2).as_markup()

