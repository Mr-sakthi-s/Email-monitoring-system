IMPORTANT_KEYWORDS = {
    "urgent": 5,
    "deadline": 4,
    "submit": 3,
    "interview": 5,
    "meeting": 3,
    "payment": 4,
    "verification": 2,
    "action required": 5,
    "review": 2,
    "important": 3,
    "assignment": 3,
    "exam": 4,
    "last date": 5,
    "due": 3,
    "reminder": 2
}

LOW_PRIORITY_KEYWORDS = {
    "privacy": -3,
    "promotion": -4,
    "offer": -4,
    "sale": -4,
    "discount": -4,
    "youtube": -2,
    "google play": -2,
    "social": -2,
    "newsletter": -3,
    "advertisement": -4
}


def calculate_importance(email_data):

    text = (
        email_data["subject"] + " " + email_data["body"]
    ).lower()

    score = 0

    matched_keywords = []
    matched_low_priority = []
    context_keywords = []

    for keyword, weight in IMPORTANT_KEYWORDS.items():

        if keyword in text:

            score += weight
            matched_keywords.append(keyword)

    for keyword, penalty in LOW_PRIORITY_KEYWORDS.items():

        if keyword in text:
            score += penalty
            matched_low_priority.append(keyword)

    score = max(score, 0)

    CONTEXT_KEYWORDS = ["scheduled", "planned", "session", "event"]
    for word in CONTEXT_KEYWORDS:
        if word in text:
            score += 2
            context_keywords.append(word)

    if score >= 7:
        priority = "high"

    elif score >= 3:
        priority = "medium"

    else:
        priority = "low"

    return {
    "score": score,
    "priority": priority,
    "matched_keywords": matched_keywords,
    "matched_low_priority": matched_low_priority,
    "context_keywords": context_keywords
}