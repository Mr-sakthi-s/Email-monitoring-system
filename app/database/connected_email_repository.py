from app.database.db import get_connection


def list_connected_emails(user_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM connected_emails WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def add_connected_email(user_id, email_address, email_password):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO connected_emails (user_id, email_address, email_password)
            VALUES (?, ?, ?)
            """,
            (user_id, email_address.lower(), email_password),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def remove_connected_email(user_id, account_id):
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM connected_emails WHERE id = ? AND user_id = ?",
            (account_id, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_connected_email(user_id, account_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM connected_emails WHERE id = ? AND user_id = ?",
            (account_id, user_id),
        ).fetchone()
    finally:
        conn.close()