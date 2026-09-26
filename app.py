from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import date, datetime, timedelta
import calendar

app = Flask(__name__)

DATABASE = "database.db"


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    # One-time and recurring event master table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_time TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            event_type TEXT DEFAULT 'task',
            recurrence TEXT DEFAULT 'none',
            start_date TEXT NOT NULL,
            end_date TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Individual daily occurrence/completion records
    conn.execute("""
        CREATE TABLE IF NOT EXISTS occurrences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            occurrence_date TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_at TEXT,
            UNIQUE(event_id, occurrence_date),
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# DATE / RECURRENCE HELPERS
# =========================================================

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def recurrence_applies(event, selected_date):

    start = parse_date(event["start_date"])

    if selected_date < start:
        return False

    if event["end_date"]:
        end = parse_date(event["end_date"])

        if selected_date > end:
            return False

    recurrence = event["recurrence"]

    # One-time event
    if recurrence == "none":
        return selected_date == start

    # Every day
    if recurrence == "daily":
        return True

    # Monday-Friday
    if recurrence == "weekdays":
        return selected_date.weekday() < 5

    # Every week on the same weekday
    if recurrence == "weekly":
        return selected_date.weekday() == start.weekday()

    # Every month on the same date
    if recurrence == "monthly":
        return selected_date.day == start.day

    return False


def ensure_occurrence(event_id, occurrence_date):

    conn = get_db()

    conn.execute("""
        INSERT OR IGNORE INTO occurrences
        (event_id, occurrence_date, completed)
        VALUES (?, ?, 0)
    """, (event_id, occurrence_date))

    conn.commit()
    conn.close()


def get_events_for_date(selected_date):

    conn = get_db()

    events = conn.execute("""
        SELECT *
        FROM events
        WHERE active = 1
        ORDER BY event_time
    """).fetchall()

    result = []

    for event in events:

        if recurrence_applies(event, selected_date):

            occurrence_date = selected_date.isoformat()

            conn.execute("""
                INSERT OR IGNORE INTO occurrences
                (event_id, occurrence_date, completed)
                VALUES (?, ?, 0)
            """, (event["id"], occurrence_date))

            occurrence = conn.execute("""
                SELECT *
                FROM occurrences
                WHERE event_id = ?
                AND occurrence_date = ?
            """, (event["id"], occurrence_date)).fetchone()

            result.append({
                "id": event["id"],
                "title": event["title"],
                "event_time": event["event_time"],
                "priority": event["priority"],
                "event_type": event["event_type"],
                "recurrence": event["recurrence"],
                "completed": occurrence["completed"]
            })

    conn.commit()
    conn.close()

    return result


# =========================================================
# PRODUCTIVITY CALCULATIONS
# =========================================================

def daily_productivity(selected_date):

    events = get_events_for_date(selected_date)

    total = len(events)

    completed = sum(
        1 for event in events
        if event["completed"]
    )

    if total == 0:
        return 0

    return round((completed / total) * 100)


def monthly_daily_data(year, month):

    days_in_month = calendar.monthrange(year, month)[1]

    data = []

    for day in range(1, days_in_month + 1):

        current = date(year, month, day)

        percentage = daily_productivity(current)

        data.append({
            "day": day,
            "percentage": percentage
        })

    return data


def weekly_data(year, month):

    days_in_month = calendar.monthrange(year, month)[1]

    weeks = {}

    for day in range(1, days_in_month + 1):

        current = date(year, month, day)

        # Monday-based week
        week_number = current.isocalendar().week

        if week_number not in weeks:
            weeks[week_number] = []

        weeks[week_number].append(
            daily_productivity(current)
        )

    result = []

    for week, values in weeks.items():

        active_days = [
            value for value in values
            if value > 0
        ]

        if active_days:
            average = round(sum(active_days) / len(active_days))
        else:
            average = 0

        result.append({
            "week": f"Week {len(result) + 1}",
            "percentage": average
        })

    return result


def monthly_data(year):

    result = []

    for month in range(1, 13):

        values = monthly_daily_data(year, month)

        active_days = [
            item["percentage"]
            for item in values
            if item["percentage"] > 0
        ]

        if active_days:
            percentage = round(
                sum(active_days) / len(active_days)
            )
        else:
            percentage = 0

        result.append({
            "month": calendar.month_abbr[month],
            "percentage": percentage
        })

    return result


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    selected_date_string = request.args.get(
        "date",
        date.today().isoformat()
    )

    try:
        selected_date = parse_date(selected_date_string)
    except ValueError:
        selected_date = date.today()

    events = get_events_for_date(selected_date)

    total = len(events)

    completed = sum(
        1 for event in events
        if event["completed"]
    )

    if total:
        percentage = round(
            completed / total * 100
        )
    else:
        percentage = 0

    previous_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    return render_template(
        "index.html",

        events=events,

        selected_date=selected_date,

        total=total,

        completed=completed,

        percentage=percentage,

        previous_date=previous_date.isoformat(),

        next_date=next_date.isoformat()
    )


# =========================================================
# ADD EVENT
# =========================================================

@app.route("/add", methods=["POST"])
def add_event():

    title = request.form["title"]
    event_time = request.form["event_time"]
    priority = request.form["priority"]
    event_type = request.form["event_type"]

    recurrence = request.form["recurrence"]

    start_date = request.form["start_date"]

    end_date = request.form.get("end_date") or None

    conn = get_db()

    conn.execute("""
        INSERT INTO events
        (
            title,
            event_time,
            priority,
            event_type,
            recurrence,
            start_date,
            end_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        event_time,
        priority,
        event_type,
        recurrence,
        start_date,
        end_date
    ))

    conn.commit()
    conn.close()

    return redirect(
        "/?date=" + start_date
    )


# =========================================================
# EDIT EVENT
# =========================================================

@app.route("/edit/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):

    conn = get_db()

    event = conn.execute("""
        SELECT *
        FROM events
        WHERE id = ?
    """, (event_id,)).fetchone()

    if not event:
        conn.close()
        return redirect("/")

    if request.method == "POST":

        title = request.form["title"]
        event_time = request.form["event_time"]
        priority = request.form["priority"]
        recurrence = request.form["recurrence"]

        start_date = request.form["start_date"]

        end_date = request.form.get("end_date") or None

        conn.execute("""
            UPDATE events

            SET title = ?,
                event_time = ?,
                priority = ?,
                recurrence = ?,
                start_date = ?,
                end_date = ?

            WHERE id = ?
        """, (
            title,
            event_time,
            priority,
            recurrence,
            start_date,
            end_date,
            event_id
        ))

        conn.commit()
        conn.close()

        return redirect(
            "/?date=" + start_date
        )

    conn.close()

    return render_template(
        "edit.html",
        event=event
    )


# =========================================================
# DELETE EVENT
# =========================================================

@app.route("/delete/<int:event_id>")
def delete_event(event_id):

    conn = get_db()

    conn.execute("""
        UPDATE events
        SET active = 0
        WHERE id = ?
    """, (event_id,))

    conn.commit()
    conn.close()

    return redirect("/")


# =========================================================
# COMPLETE EVENT
# =========================================================

@app.route("/complete/<int:event_id>/<selected_date>")
def complete_event(event_id, selected_date):

    ensure_occurrence(
        event_id,
        selected_date
    )

    conn = get_db()

    conn.execute("""
        UPDATE occurrences

        SET completed = 1,
            completed_at = ?

        WHERE event_id = ?
        AND occurrence_date = ?
    """, (
        datetime.now().isoformat(),
        event_id,
        selected_date
    ))

    conn.commit()
    conn.close()

    return redirect(
        "/?date=" + selected_date
    )


# =========================================================
# UNCOMPLETE EVENT
# =========================================================

@app.route("/uncomplete/<int:event_id>/<selected_date>")
def uncomplete_event(event_id, selected_date):

    conn = get_db()

    conn.execute("""
        UPDATE occurrences

        SET completed = 0,
            completed_at = NULL

        WHERE event_id = ?
        AND occurrence_date = ?
    """, (
        event_id,
        selected_date
    ))

    conn.commit()
    conn.close()

    return redirect(
        "/?date=" + selected_date
    )


# =========================================================
# ANALYTICS
# =========================================================

@app.route("/analytics")
def analytics():

    today = date.today()

    selected_year = int(
        request.args.get(
            "year",
            today.year
        )
    )

    selected_month = int(
        request.args.get(
            "month",
            today.month
        )
    )

    daily_data = monthly_daily_data(
        selected_year,
        selected_month
    )

    weeks = weekly_data(
        selected_year,
        selected_month
    )

    months = monthly_data(
        selected_year
    )

    active_days = [
        item["percentage"]
        for item in daily_data
        if item["percentage"] > 0
    ]

    if active_days:
        month_percentage = round(
            sum(active_days) / len(active_days)
        )
    else:
        month_percentage = 0

    return render_template(
        "analytics.html",

        daily_data=daily_data,

        weeks=weeks,

        months=months,

        month_percentage=month_percentage,

        selected_year=selected_year,

        selected_month=selected_month,

        month_name=calendar.month_name[selected_month]
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )