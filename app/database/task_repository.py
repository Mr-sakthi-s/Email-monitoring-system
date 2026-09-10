import sqlite3

from app.database.db import get_connection


def save_task(task):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id
            FROM tasks
            WHERE LOWER(task_title) = LOWER(?)
            AND user_id = ?
            """,
            (task["title"], task.get("user_id")),
        )

        existing_task = cursor.fetchone()
        if existing_task:
            print(f"Task already exists: {task['title']}")
            return

        cursor.execute(
            """
            INSERT INTO tasks (
                email_uid,
                task_title,
                priority,
                deadline,
                status,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task["email_uid"],
                task["title"],
                task["priority"],
                task["deadline"],
                task["status"],
                task.get("user_id"),
            ),
        )

        conn.commit()
        print(f"Task Saved: {task['title']}")

    except sqlite3.IntegrityError:
        print(f"Skipped duplicate task: {task['title']}")

    except Exception as e:
        print(f"Task insert failed: {e}")

    finally:
        conn.close()