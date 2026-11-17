import sqlite3

DB_NAME = "expenses.db"


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            user_id INTEGER
        )
    """)

    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]

    if "user_id" not in columns:
        cursor.execute(
            "ALTER TABLE transactions ADD COLUMN user_id INTEGER"
        )

    conn.commit()
    conn.close()


def add_transaction(transaction_type, amount, category,
                    description, date, user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (transaction_type, amount, category, description, date, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        transaction_type, amount, category,
        description, date, user_id
    ))

    conn.commit()
    conn.close()


def fetch_transactions(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, transaction_type, amount,
               category, description, date
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()

    return data


def delete_transaction(transaction_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?
    """, (transaction_id, user_id))

    conn.commit()
    conn.close()

def create_user_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def add_user_id_column():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]

    if "user_id" not in columns:
        cursor.execute(
            "ALTER TABLE transactions ADD COLUMN user_id INTEGER"
        )

    conn.commit()
    conn.close()