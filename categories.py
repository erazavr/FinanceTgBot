from db import get_db


async def get_categories():
    db = get_db()

    cur = db.cursor()

    cur.execute('SELECT * FROM categories')
    categories = cur.fetchall()
    db.close()

    if not categories:
        return 'Пока нет категорий ✨\nДля добавления категорий - /add_category'

    text_lines = []

    for category in categories:
        cat_id = category[0]
        cat_name = category[1]

        text_lines.append(f'{cat_name} - /del_cat_{cat_id}')

    return '\n'.join(text_lines)


async def add_category(name: str):
    db = get_db()

    cur = db.cursor()

    cur.execute(
        'SELECT * FROM categories WHERE name_lower = ?',
        (name.lower(),)
    )

    category = cur.fetchone()

    if category:
        category_name = category[1]
        raise Exception(f'Категория {category_name} уже существует ❗️')

    cur.execute('insert into categories (name,name_lower) VALUES (?,?)', (name, name.lower()))

    db.commit()
    db.close()

async def del_category(row_id: int) -> None:
    db = get_db()
    cur = db.cursor()
    cur.execute('delete from categories where id = ?', (row_id,))
    db.commit()
    db.close()