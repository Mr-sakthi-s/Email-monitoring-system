import sqlite3


DB_PATH = "data/emails.db"


def save_task(task):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    try:

        # CHECK EXISTING TASK TITLE
        cursor.execute(
            """
            SELECT id
            FROM tasks
            WHERE LOWER(task_title) = LOWER(?)
            """,
            (task["title"],)
        )

        existing_task = cursor.fetchone()

        if existing_task:
            print(
                f"Task already exists: "
                f"{task['title']}"
            )
            conn.close()
            return

        # INSERT NEW TASK
        cursor.execute(
            """
            INSERT INTO tasks (
                email_uid,
                task_title,
                priority,
                deadline,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task["email_uid"],
                task["title"],
                task["priority"],
                task["deadline"],
                task["status"]
            )
        )

        conn.commit()

        print(f"Task Saved: {task['title']}")

    except sqlite3.IntegrityError:

        print(
            f"Skipped duplicate task: "
            f"{task['title']}"
        )

    except Exception as e:

        print(f"Task insert failed: {e}")

    finally:

        conn.close()