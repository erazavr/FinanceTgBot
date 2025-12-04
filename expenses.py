import re

from db import get_db
from typing import NamedTuple, Optional


class Expenses(NamedTuple):
    id: Optional[int]
    amount: int
    category: str


class Message(NamedTuple):
    amount: int
    category: str


async def add_expense(amount: int, category_id: int) -> Expenses:

    db = get_db()

    cur = db.cursor()
    cur.execute('insert into expenses (amount, category_id) VALUES (?,?)', (amount, category_id))

    cur.execute('select * from categories where id = ?', (category_id,))

    category = cur.fetchone()

    category_name = category[1]

    db.commit()
    db.close()

    return Expenses(None, int(amount), category_name)


async def get_today_expenses() -> str:
    return _get_expenses(start='date("now", "localtime")',
                         end='date("now", "localtime", "+1 day")',
                         text='На сегодня нет расходов ✨')


async def get_month_expenses() -> str:
    return _get_expenses(start='date("now", "start of month")',
                         end='date("now", "start of month", "+1 month")',
                         text='За месяц нет расходов ✨')


async def get_week_expenses() -> str:
    return _get_expenses(start='date("now", "weekday 1", "-7 days")',
                         end='date(created_at) < date("now", "weekday 1")',
                         text='За неделю нет расходов ✨')


async def del_expense(row_id: int) -> None:
    db = get_db()
    cur = db.cursor()
    cur.execute('delete from expenses where id = ?', (row_id,))
    db.commit()
    db.close()


def _get_expenses(start: str, end: str, text: str):
    db = get_db()
    cur = db.cursor()

    query = f'select e.id as id, e.amount as amount, c.name as name from expenses e inner join categories c on c.id = e.category_id where date(e.created_at) >= {start} and date(e.created_at) < {end} order by date(e.created_at) desc'
    cur.execute(query)
    result = cur.fetchall()
    db.close()

    if not result:
        return text

    total = 0
    text_lines = []

    for res in result:
        row_id = res[0]
        amount = int(res[1])
        category = res[2]

        total = total + amount

        text_lines.append(f'{amount} сом на {category.lower()} - /del_{row_id}')

    text_lines.append(f'\nИтого: {total} сом')

    return '\n'.join(text_lines)


def parse_message(raw_message: str) -> int:
    raw = raw_message.strip()

    if not raw.isdigit():
        raise ValueError(
            "Введите только сумму, например:\n300"
        )

    return int(raw)
