import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(__file__), "..", "data", "student_helper.db")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_user_id INTEGER PRIMARY KEY,
            group_id TEXT NOT NULL,
            group_name TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_user_group(telegram_user_id: int, group_id: str, group_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users (telegram_user_id, group_id, group_name)
        VALUES (?, ?, ?)
    """, (telegram_user_id, group_id, group_name))

    conn.commit()
    conn.close()


def get_user_group(telegram_user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT group_id, group_name
        FROM users
        WHERE telegram_user_id = ?
    """, (telegram_user_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "group_id": row[0],
            "group_name": row[1]
        }

    return None
