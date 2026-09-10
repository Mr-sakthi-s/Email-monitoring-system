import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "emails.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _column_exists(table_name, column_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return column_name in columns


def _add_column_if_missing(table_name, column_name, column_definition):
    if not _column_exists(table_name, column_name):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )
        conn.commit()
        conn.close()


def create_tables():
    os.makedirs(str(DB_PATH.parent), exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_uid TEXT UNIQUE,
            sender TEXT,
            subject TEXT,
            body TEXT,
            received_at TEXT,
            is_important INTEGER DEFAULT 0,
            is_spam INTEGER DEFAULT 0,
            deadline TEXT,
            user_id INTEGER,
            connected_email_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_uid TEXT,
            task_title TEXT,
            deadline TEXT,
            priority TEXT,
            status TEXT DEFAULT 'pending',
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            subject TEXT,
            message TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    _add_column_if_missing("emails", "user_id", "INTEGER")
    _add_column_if_missing("emails", "is_spam", "INTEGER DEFAULT 0")
    _add_column_if_missing("emails", "connected_email_id", "INTEGER")
    _add_column_if_missing("emails", "receiver", "TEXT")
    _add_column_if_missing("tasks", "user_id", "INTEGER")
    _add_column_if_missing("contact_messages", "user_id", "INTEGER")
    _add_column_if_missing("users", "username", "TEXT")
    _add_column_if_missing("users", "password", "TEXT")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS connected_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email_address TEXT NOT NULL,
            email_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (user_id, email_address)
        )
        """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database initialized successfully.")