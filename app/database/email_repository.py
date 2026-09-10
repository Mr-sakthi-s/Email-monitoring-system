import sqlite3

from app.database.db import get_connection


def save_email(email_data):
    conn = get_connection()
    cursor = conn.cursor()
    stored_uid = (
        f"{email_data['connected_email_id']}:{email_data['uid']}"
        if email_data.get("connected_email_id")
        else email_data["uid"]
    )

    try:
        cursor.execute(
            """
            INSERT INTO emails (
                email_uid,
                receiver,
                sender,
                subject,
                body,
                received_at,
                is_important,
                deadline,
                user_id,
                connected_email_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stored_uid,
                email_data.get("receiver"),
                email_data["sender"],
                email_data["subject"],
                email_data["body"],
                email_data["date"],
                email_data.get("is_important", 0),
                email_data.get("deadline"),
                email_data.get("user_id"),
                email_data.get("connected_email_id"),
            ),
        )

        conn.commit()
        email_db_id = cursor.lastrowid
        print(f"Saved: {email_data['subject']}")
        return email_db_id

    except sqlite3.IntegrityError:
        cursor.execute(
            """
            SELECT id
            FROM emails
            WHERE email_uid = ? AND user_id = ? AND connected_email_id = ?
            """,
            (stored_uid, email_data.get("user_id"), email_data.get("connected_email_id")),
        )

        existing = cursor.fetchone()
        if existing:
            print(f"Skipped duplicate email: {email_data['subject']}")
            return existing[0]

        return None

    finally:
        conn.close()