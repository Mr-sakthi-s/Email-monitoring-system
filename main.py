from app.database.db import create_tables
from app.database.email_repository import save_email
from app.database.task_repository import save_task
from app.fetcher.gmail_fetcher import GmailFetcher
from app.processor.deadline_extractor import extract_deadline
from app.processor.importance_detector import calculate_importance
from app.processor.task_generator import generate_task


def run_pipeline(user_id, email_address, email_password, connected_email_id):
    create_tables()

    if user_id is None:
        raise ValueError("A logged-in user_id is required to fetch and save emails.")

    fetcher = GmailFetcher(email_address, email_password)
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
            1 if importance["priority"] in ["medium", "high"] else 0
        )
        mail["deadline"] = (
            deadline_info["dates"][0] if deadline_info["dates"] else None
        )
        mail["user_id"] = user_id
        mail["connected_email_id"] = connected_email_id

        email_db_id = save_email(mail)
        if not email_db_id:
            continue

        mail["db_id"] = email_db_id
        task = generate_task(mail, importance, deadline_info)

        if task:
            task["user_id"] = user_id
            print(
                f"Generated Task => "
                f"Title: {task['title']} | "
                f"Priority: {task['priority']} | "
                f"Deadline: {task['deadline']}"
            )
            save_task(task)

    fetcher.close()
















