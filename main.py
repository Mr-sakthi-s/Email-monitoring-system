from app.fetcher.email_fetcher import EmailFetcher
from app.database.db import create_tables
from app.database.email_repository import save_email
from app.processor.importance_detector import calculate_importance
from app.processor.deadline_extractor import extract_deadline
from app.processor.task_generator import generate_task
from app.database.task_repository import save_task


def run_pipeline():

    create_tables()

    fetcher = EmailFetcher()

    fetcher.connect()

    emails = fetcher.fetch_recent_emails()

    for mail in emails:

        importance = calculate_importance(mail)

        print(
            f"Priority: {importance['priority']} | "
            f"Score: {importance['score']} | "
            f"Positive: {importance['matched_keywords']} | "
            f"Negative: {importance['matched_low_priority']}"
        )

        deadline_info = extract_deadline(mail)

        print(
            f"Dates: {deadline_info['dates']} | "
            f"Times: {deadline_info['times']}"
        )

        mail["is_important"] = (
            1 if importance["priority"] in ["medium", "high"]
            else 0
        )

        mail["deadline"] = (
            deadline_info["dates"][0]
            if deadline_info["dates"]
            else None
        )

        # SAVE EMAIL FIRST
        email_db_id = save_email(mail)

        # ATTACH DB ID
        if not email_db_id:
            continue

        mail["db_id"] = email_db_id

        # GENERATE TASK AFTER EMAIL SAVE
        task = generate_task(
            mail,
            importance,
            deadline_info
        )

        if task:

            print(
                f"Generated Task => "
                f"Title: {task['title']} | "
                f"Priority: {task['priority']} | "
                f"Deadline: {task['deadline']}"
            )

            save_task(task)


if __name__ == "__main__":
    run_pipeline()