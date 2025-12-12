from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from keyboards import inline_categories, cancel_button

import expenses
import categories

router = Router()

pending_amount: dict[int, int] = {}
user_state: dict[int, str] = {}


# Старт бота
@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Бот для учета финансов!💸\n"
        "Просто отправьте сумму и выберите категорию\n"
        "Доступные команды: \n"
        "• /today — показать расходы за сегодня \n"
        "• /week — показать расходы за неделю \n"
        "• /month — показать расходы за месяц \n"
        "• /add_category — добавить категорию \n"
        "• /get_categories — список категорий \n"
    )


# Помощь
@router.message(Command("help"))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Доступные команды: \n"
        "• /today — показать расходы за сегодня \n"
        "• /week — показать расходы за неделю \n"
        "• /month — показать расходы за месяц \n"
        "• /add_category — добавить категорию \n"
        "• /get_categories — список категорий \n"
    )


# Расходы за сегодня
@router.message(Command("today"))
async def command_today_handler(message: Message) -> None:
    try:
        chat_id = message.chat.id
        today_expenses = await expenses.get_today_expenses(chat_id)
    except Exception as e:
        await message.answer(str(e))
        return

    await message.answer(today_expenses, parse_mode=ParseMode.HTML)


# Расходы за неделю
@router.message(Command("week"))
async def command_week_handler(message: Message) -> None:
    try:
        chat_id = message.chat.id
        week_expenses = await expenses.get_week_expenses(chat_id)
    except Exception as e:
        await message.answer(str(e))
        return
    await message.answer(week_expenses, parse_mode=ParseMode.HTML)


# Расходы за месяц
@router.message(Command("month"))
async def command_month_handler(message: Message) -> None:
    try:
        chat_id = message.chat.id
        month_expenses = await expenses.get_month_expenses(chat_id)
    except Exception as e:
        await message.answer(str(e))
        return
    await message.answer(month_expenses, parse_mode=ParseMode.HTML)


# Список категорий
@router.message(Command("get_categories"))
async def command_month_handler(message: Message) -> None:
    try:
        chat_id = message.chat.id
        categories_list = await categories.get_categories(chat_id)
    except Exception as e:
        await message.answer(str(e))
        return
    await message.answer(categories_list)


# Добавление расходов
@router.message(F.text.regexp(r"^\d+([.,]\d+)?$"))
async def amount_handler(message: Message):
    chat_id = message.chat.id
    try:
        amount = expenses.parse_message(message.text)
        user_id = message.from_user.id
        pending_amount[user_id] = amount
    except Exception as e:
        await message.answer(str(e))
        return

    await message.reply(f'Сумма {amount} сом \nВыберите категорию:', reply_markup=await inline_categories(chat_id))


# Добавление категории
@router.message(Command("add_category"))
async def add_category_handler(message: Message) -> None:
    user_id = message.from_user.id
    user_state[user_id] = "waiting_category_name"
    await message.reply('Напишите название категории', reply_markup=cancel_button)


# Удаление категории
@router.message(F.text.startswith("/del_cat_"))
async def command_del_handler(message: Message) -> None:
    row_id = int(message.text.split("/del_cat_")[1])
    await categories.del_category(row_id)
    await message.answer('Категория удалена')


# Удаление расходов
@router.message(F.text.startswith("/del_"))
async def command_del_handler(message: Message) -> None:
    row_id = int(message.text.split("/del_")[1])
    await expenses.del_expense(row_id)
    await message.answer('Расход удален')


@router.callback_query(F.data.startswith("cat:"))
async def category_chosen(callback: CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    if user_id not in pending_amount:
        await callback.answer("Сначала отправь сумму!", show_alert=True)
        return

    category_id = int(callback.data.split(":")[1])

    try:
        expense = await expenses.add_expense(pending_amount[user_id], category_id, chat_id)
    except Exception as e:
        await callback.answer(str(e))
        return

    pending_amount.pop(user_id, None)
    await callback.message.edit_text(f'Добавлен расход {expense.amount} сом на {expense.category.lower()}')


@router.callback_query(F.data == 'cancel')
async def cancel_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id in pending_amount:
        pending_amount.pop(user_id)

    if user_id in user_state:
        user_state.pop(user_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text("❌ Отменено")


@router.message()
async def catch_category_name_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_state.get(user_id) != "waiting_category_name":
        return
    try:
        chat_id = message.chat.id
        await categories.add_category(message.text,chat_id)
    except Exception as e:
        await message.answer(str(e))
        return
    user_state.pop(user_id, None)
    await message.answer('Категория добавлена ✅')
