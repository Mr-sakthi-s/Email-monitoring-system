# AI Mail Intelligence System

## Project Overview

AI Mail Intelligence System is a smart email monitoring and task generation web application built using Python, Flask, SQLite, HTML, and CSS.

This project fetches emails from Gmail, analyzes them, detects important emails, extracts deadlines, and automatically creates tasks from useful emails.

The system also provides a modern dashboard where users can view emails, monitor important tasks, and manually fetch new emails.

---

# Main Features

## Email Fetching

- Connects to Gmail using IMAP
- Fetches recent emails
- Skips already fetched emails using unique email IDs

## Importance Detection

- Detects important emails using keyword scoring
- Classifies emails into:
  - High Priority
  - Medium Priority
  - Low Priority

## Deadline Extraction

- Extracts dates and deadlines from email content
- Detects meeting dates, sessions, reminders, and events

## Automatic Task Generation

- Creates tasks automatically from:
  - Important emails
  - Emails containing deadlines

## Dashboard

- Modern web dashboard using Flask
- Separate pages for:
  - Home
  - Mail Dashboard
  - Task Dashboard
  - Contact Page

## Manual Email Fetch Button

- User can manually fetch new emails from dashboard
- Avoids duplicate email insertion

---

# Technologies Used

| Technology | Purpose              |
| ---------- | -------------------- |
| Python     | Backend Logic        |
| Flask      | Web Framework        |
| SQLite     | Database             |
| HTML       | Frontend Structure   |
| CSS        | Styling              |
| IMAP       | Gmail Email Fetching |

---

# Project Structure

```text
Email_Monitoring/
│
├── app/
│   ├── api/
│   ├── dashboard/
│   ├── database/
│   ├── fetcher/
│   ├── processor/
│   ├── scheduler/
│   ├── static/
│   └── templates/
│
├── data/
│   └── emails.db
│
├── logs/
├── venv/
├── main.py
├── run.py
└── requirements.txt
```

---

# Working Flow

```text
User Clicks Fetch Emails
        ↓
Flask Route Triggered
        ↓
Pipeline Starts
        ↓
Connect Gmail
        ↓
Fetch Recent Emails
        ↓
Analyze Importance
        ↓
Extract Deadlines
        ↓
Save Emails to Database
        ↓
Generate Tasks
        ↓
Display in Dashboard
```

---

# Database Tables

## Emails Table

Stores:

- sender
- subject
- body
- received date
- importance
- deadline

## Tasks Table

Stores:

- task title
- priority
- deadline
- task status

---

# Duplicate Prevention

The system prevents duplicate emails using:

```sql
email_uid TEXT UNIQUE
```

This ensures that already fetched emails are not inserted again.

# Future Improvements

Planned future upgrades:

- Spam Email Classification
- Machine Learning Based Importance Detection
- Email Summarization
- Notification System
- Automatic Background Fetching
- n8n Automation Integration
- User Authentication
- Cloud Deployment
- Sentiment Analysis
- Reminder Notifications

---

# Learning Outcomes

This project helped in learning:

- Flask Web Development
- Database Design
- Python Backend Architecture
- Email Processing
- Modular Programming
- NLP Style Keyword Analysis
- Task Automation
- API Design
- Dashboard Development

---

# Conclusion

AI Mail Intelligence System is a practical intelligent automation project that combines email processing, task management, and web development.

The project demonstrates backend engineering, database management, modular architecture, and automation concepts using real-world workflows.

---

# Author

Sakthi Murugan
Engineering Student | Aspiring Data Scientist
