import sqlite3
from app.database.db import get_connection


def save_email(email_data):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO emails (
            email_uid,
            sender,
            subject,
            body,
            received_at,
            is_important,
            deadline
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email_data["uid"],
                email_data["sender"],
                email_data["subject"],
                email_data["body"],
                email_data["date"],
                email_data.get("is_important", 0),
                email_data.get("deadline")
            )
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
            WHERE email_uid = ?
            """,
            (email_data["uid"],)
        )

        existing_id = cursor.fetchone()[0]

        print(
            f"Skipped duplicate email: "
            f"{email_data['subject']}"
        )

        return existing_id

    finally:
        conn.close()