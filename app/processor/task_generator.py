def generate_task(email_data, importance, deadline_info):

    should_create_task = False

    if importance["priority"] in ["medium", "high"]:
        should_create_task = True

    if deadline_info["dates"]:
        should_create_task = True

    if not should_create_task:
        return None

    task = {
        "email_uid": email_data["uid"],
        "title": email_data["subject"],
        "priority": importance["priority"],
        "deadline": (
            deadline_info["dates"][0]
            if deadline_info["dates"]
            else None
        ),
        "status": "pending"
    }

    return task