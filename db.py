import sqlite3


# Будем подключаться один раз при запуске
def get_db():
    db = sqlite3.connect("finance.db")
    db.row_factory = sqlite3.Row
    return db


async def db_start():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                chat_id INTEGER,
                name_lower TEXT NOT NULL UNIQUE
            );
        """)

    # Создание таблицы расходов
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            chat_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    """)

    default_categories = ['Такси', 'Обед', 'Проезд', 'Развлечение', 'Еда', 'Маркетплейс', 'Подарки']

    for category in default_categories:
        cur.execute("INSERT OR IGNORE INTO categories (name,name_lower) VALUES (?,?)", (category, category.lower()))

    db.commit()
    db.close()
