from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash

from app.database.db import create_tables, get_connection
from app.database.connected_email_repository import (
    add_connected_email,
    list_connected_emails,
    remove_connected_email,
)
from app.database.user_repository import create_user, get_user_by_username
from main import run_pipeline

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "change-me-in-production"
create_tables()


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/login")
        return view_func(*args, **kwargs)

    return wrapped_view


@app.context_processor
def inject_user():
    return {
        "is_logged_in": bool(session.get("user_id")),
        "current_user": session.get("username"),
    }


@app.route("/")
@login_required
def home():
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM emails WHERE user_id = ?",
        (user_id,),
    )
    total_emails = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM emails WHERE user_id = ? AND is_important = 1",
        (user_id,),
    )
    important_emails = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'pending'",
        (user_id,),
    )
    pending_tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'completed'",
        (user_id,),
    )
    completed_tasks = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "home.html",
        total_emails=total_emails,
        important_emails=important_emails,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/mails")
@login_required
def mails():
    user_id = session["user_id"]
    account_id = request.args.get("account", type=int)
    filter_name = request.args.get("filter", "all")
    sort_name = request.args.get("sort", "date")
    conditions = ["user_id = ?"]
    parameters = [user_id]
    if filter_name == "important":
        conditions.append("is_important = 1")
    elif filter_name == "spam":
        conditions.append("is_spam = 1")
    if account_id:
        conditions.append("connected_email_id = ?")
        parameters.append(account_id)
    order_by = "deadline IS NULL, deadline ASC" if sort_name == "deadline" else "received_at DESC"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM emails WHERE {' AND '.join(conditions)} ORDER BY {order_by}",
        parameters,
    )
    emails = cursor.fetchall()
    conn.close()
    return render_template("mails.html", emails=emails, connected_emails=list_connected_emails(user_id))


@app.route("/tasks")
@login_required
def tasks():
    user_id = session["user_id"]
    status_filter = request.args.get("status", "all")
    priority_filter = request.args.get("priority", "all")
    sort_name = request.args.get("sort", "newest")
    conditions = ["user_id = ?"]
    parameters = [user_id]
    if status_filter in {"pending", "completed"}:
        conditions.append("status = ?")
        parameters.append(status_filter)
    if priority_filter in {"high", "medium", "low"}:
        conditions.append("priority = ?")
        parameters.append(priority_filter)
    order_by = {
        "oldest": "created_at ASC",
        "deadline": "deadline IS NULL, deadline ASC",
        "priority": "CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, created_at DESC",
    }.get(sort_name, "created_at DESC")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT * FROM tasks WHERE {' AND '.join(conditions)} ORDER BY {order_by}",
        parameters,
    )
    tasks_list = cursor.fetchall()
    conn.close()
    return render_template(
        "tasks.html",
        tasks=tasks_list,
        status_filter=status_filter,
        priority_filter=priority_filter,
        sort_name=sort_name,
    )


@app.route("/complete-task/<int:task_id>")
@login_required
def complete_task(task_id):
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'completed' WHERE id = ? AND user_id = ? AND status = 'pending'",
        (task_id, user_id),
    )
    conn.commit()
    conn.close()
    return redirect("/tasks")


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, subject, message]):
            flash("Please complete all contact fields.")
            return redirect("/contact")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO contact_messages (name, email, subject, message, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, subject, message, session["user_id"]),
        )
        conn.commit()
        conn.close()

        flash("Your feedback was saved successfully.")

        return redirect("/contact")

    return render_template("contact.html")


@app.route("/fetch-emails")
@login_required
def fetch_emails():
    accounts = list_connected_emails(session["user_id"])
    for account in accounts:
        try:
            run_pipeline(session["user_id"], account["email_address"], account["email_password"], account["id"])
        except Exception as exc:
            flash(f"Email fetch failed for {account['email_address']}: {exc}")
    if accounts:
        flash("Emails were fetched and organized.")
    else:
        flash("Connect an email account before fetching emails.")
    return redirect("/mails")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not all([username, password]):
            flash("All fields are required.")
            return render_template("register.html")

        if get_user_by_username(username):
            flash("That username is already in use.")
            return render_template("register.html")

        create_user(username, password)
        flash("Registration successful. Please log in.")
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if user and user["password"] and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")

        flash("Invalid username or password.")
        return render_template("login.html")

    return render_template("login.html")


@app.route("/connected-emails", methods=["GET", "POST"])
@login_required
def connected_emails():
    user_id = session["user_id"]
    if request.method == "POST":
        email_address = request.form.get("email_address", "").strip()
        email_password = request.form.get("email_password", "")
        if not email_address or not email_password:
            flash("Email address and password are required.")
        else:
            try:
                add_connected_email(user_id, email_address, email_password)
                flash("Email account connected.")
            except Exception:
                flash("That email account is already connected.")
        return redirect("/connected-emails")
    return render_template("connected_emails.html", connected_emails=list_connected_emails(user_id))


@app.route("/connected-emails/<int:account_id>/remove", methods=["POST"])
@login_required
def remove_email_account(account_id):
    remove_connected_email(session["user_id"], account_id)
    flash("Email account removed.")
    return redirect("/connected-emails")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


create_tables()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)