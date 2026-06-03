from flask import Flask, render_template, redirect, request
import sqlite3
from main import run_pipeline
from flask import redirect

app = Flask(__name__)

DB_PATH = "data/emails.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM emails")
    total_emails = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM emails WHERE is_important = 1"
    )
    important_emails = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='pending'"
    )
    pending_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='completed'"
    )
    completed_tasks = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "home.html",
        total_emails=total_emails,
        important_emails=important_emails,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


@app.route("/mails")
def mails():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM emails
        ORDER BY created_at DESC
        """
    )

    emails = cursor.fetchall()

    conn.close()

    return render_template(
        "mails.html",
        emails=emails
    )


@app.route("/tasks")
def tasks():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        ORDER BY
        CASE priority
            WHEN 'high' THEN 1
            WHEN 'medium' THEN 2
            ELSE 3
        END
        """
    )

    tasks = cursor.fetchall()

    conn.close()

    return render_template(
        "tasks.html",
        tasks=tasks
    )


@app.route("/complete-task/<int:task_id>")
def complete_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = 'completed'
        WHERE id = ?
        """,
        (task_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/tasks")


@app.route("/delete-task/<int:task_id>")
def delete_task(task_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/tasks")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/fetch-emails")
def fetch_emails():

    run_pipeline()

    return redirect("/mails")