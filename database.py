import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "kms.db")

def get_connection():
    # check_same_thread=False is needed for Streamlit
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Дочерня таблица "children"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birth_date DATE NOT NULL,
            parent_name TEXT NOT NULL,
            parent_phone TEXT,
            enrollment_date DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'активный'
        )
    ''')

    # Таблица "attendance" (Посещаемость)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER NOT NULL,
            date DATE NOT NULL,
            status TEXT NOT NULL, -- 'присутствовал', 'отсутствовал', 'болел'
            FOREIGN KEY (child_id) REFERENCES children (id) ON DELETE CASCADE
        )
    ''')

    # Таблица "products" (Справочник продуктов)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            unit TEXT NOT NULL, -- 'кг', 'литры', 'штуки'
            min_stock REAL NOT NULL DEFAULT 0
        )
    ''')

    # Таблица "product_income" (Приход продуктов)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            date DATE NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            supplier TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')

    # Таблица "product_expense" (Расход продуктов)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_expense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            date DATE NOT NULL,
            quantity REAL NOT NULL,
            purpose TEXT, -- завтрак, обед и т.д.
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')

    # Таблица "expenses" (Финансовые расходы)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            category TEXT NOT NULL, -- продукты, аренда, зарплата, коммунальные услуги, игрушки, прочее
            description TEXT,
            amount REAL NOT NULL,
            comment TEXT
        )
    ''')
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database `kms.db` successfully initialized.")
