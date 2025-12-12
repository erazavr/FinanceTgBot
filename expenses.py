from typing import NamedTuple, Optional

from db import get_db
from utils import format_amount


class Expenses(NamedTuple):
    id: Optional[int]
    amount: int
    category: str


class Message(NamedTuple):
    amount: int
    category: str


async def add_expense(amount: int, category_id: int, chat_id: int) -> Expenses:
    db = get_db()

    cur = db.cursor()
    cur.execute('insert into expenses (amount, category_id, chat_id) VALUES (?,?,?)', (amount, category_id, chat_id))

    cur.execute('select * from categories where id = ?', (category_id,))

    category = cur.fetchone()

    category_name = category[1]

    db.commit()
    db.close()

    return Expenses(None, amount, category_name)


async def get_today_expenses(chat_id: int) -> str:
    return _get_expenses(start='date("now", "localtime")',
                         end='date("now", "localtime", "+1 day")',
                         text='На сегодня нет расходов ✨',
                         chat_id=chat_id)


async def get_month_expenses(chat_id: int) -> str:
    return _get_expenses(start='date("now", "start of month")',
                         end='date("now", "start of month", "+1 month")',
                         text='За месяц нет расходов ✨',
                         chat_id=chat_id,
                         group_by_day=True)


async def get_week_expenses(chat_id: int) -> str:
    return _get_expenses(start='date("now", "weekday 1", "-7 days")',
                         end='date(created_at) < date("now", "weekday 1")',
                         text='За неделю нет расходов ✨',
                         chat_id=chat_id,
                         group_by_day=True)


async def get_end_of_day_expenses(chat_id: int) -> str:
    return _get_expenses(start='date("now", "localtime")',
                         end='date("now", "localtime", "+1 day")',
                         text='На сегодня нет расходов ✨',
                         chat_id=chat_id,
                         end_of_day=True)


async def del_expense(row_id: int) -> None:
    db = get_db()
    cur = db.cursor()
    cur.execute('delete from expenses where id = ?', (row_id,))
    db.commit()
    db.close()


def _get_expenses(start: str, end: str, text: str, chat_id: int, end_of_day: bool = False, group_by_day=False):
    db = get_db()
    cur = db.cursor()

    if end_of_day:
        query = f'select c.id as category_id, sum(e.amount) as amount, c.name as name from expenses e inner join categories c on c.id = e.category_id where e.chat_id = {chat_id} and date(e.created_at) >= {start} and date(e.created_at) < {end} group by c.id, c.name order by amount desc'
    else:
        query = f'select e.id as id, e.amount as amount, c.name as name, e.created_at from expenses e inner join categories c on c.id = e.category_id where e.chat_id = {chat_id} and date(e.created_at) >= {start} and date(e.created_at) < {end}'
    cur.execute(query)
    result = cur.fetchall()
    db.close()

    if not result:
        return text

    total = 0

    output_lines = []
    category_by_dates = {}

    if group_by_day:
        for cat_id, amount, category, created_at in result:
            date = created_at.split(' ')[0]
            total += amount
            _amount = format_amount(amount)
            category_by_dates.setdefault(date, {})
            category_by_dates[date][category] = category_by_dates[date].get(category, 0) + _amount

        for date, cats in category_by_dates.items():
            output_lines.append(f'📅 <b>{date}</b>')
            for category, amount in cats.items():
                output_lines.append(f'  • <b>{amount}</b> сом - {category.lower()}')

        output_lines.append(f'\n✨ <b>Итого: {format_amount(total)} сом</b>')
        return '\n'.join(output_lines)

    text_lines = []

    for res in result:
        if end_of_day:
            _, raw_amount, category = res
            total += raw_amount
            amount = format_amount(raw_amount)
            text_lines.append(f"{amount} сом на {category.lower()}")
        else:
            row_id, raw_amount, category, _ = res
            total += raw_amount
            amount = format_amount(raw_amount)
            text_lines.append(f"<b>{amount}</b> сом - {category.lower()} - /del_{row_id}")

    text_lines.append(f'\n✨ <b>Итого: {format_amount(total)} сом</b>')

    return '\n'.join(text_lines)


def parse_message(raw_message: str):
    cleaned = raw_message.replace(",", ".").strip()

    try:
        amount = float(cleaned)
    except ValueError:
        raise ValueError("Введите сумму в формате 200 или 12.5")

    if amount <= 0:
        raise ValueError("Сумма должна быть больше нуля")

    return format_amount(amount)
