# database.py
# Работа с базой данных SQLite (пользователи, лайки)

import sqlite3
import pandas as pd
from contextlib import contextmanager
from config import DB_NAME

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                user_id INTEGER,
                ticker TEXT,
                liked INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, ticker),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

def get_or_create_user(username):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            c.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            return c.lastrowid

def get_username_by_id(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else None

def add_like(user_id, ticker, liked=1):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO likes (user_id, ticker, liked)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, ticker) DO UPDATE SET liked = ?
        ''', (user_id, ticker, liked, liked))
        conn.commit()

def remove_like(user_id, ticker):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM likes WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        conn.commit()

def get_user_likes(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT ticker FROM likes WHERE user_id = ? AND liked = 1", (user_id,))
        return [row[0] for row in c.fetchall()]

def get_all_likes():
    with get_connection() as conn:
        return pd.read_sql_query("SELECT user_id, ticker, liked FROM likes", conn)

# Инициализация при импорте
init_db()