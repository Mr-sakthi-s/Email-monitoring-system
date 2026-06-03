import re

DATE_PATTERNS = [
    r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
    r'\b\d{1,2}/\d{1,2}\b',
    r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\b',
    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b',
    r'\b(?:today|tomorrow)\b',
    r'\bnext\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
]


TIME_PATTERNS = [
    r'\b\d{1,2}:\d{2}\s?(?:am|pm)?\b',
    r'\b\d{1,2}\s?(?:am|pm)\b'
]


def extract_deadline(email_data):

    text = (
        email_data["subject"] + " " + email_data["body"]
    ).lower()

    found_dates = []

    found_times = []

    for pattern in DATE_PATTERNS:

        matches = re.findall(pattern, text)

        found_dates.extend(matches)

    for pattern in TIME_PATTERNS:

        matches = re.findall(pattern, text)

        found_times.extend(matches)

    return {
    "dates": list(set(found_dates)),
    "times": list(set(found_times))
    }