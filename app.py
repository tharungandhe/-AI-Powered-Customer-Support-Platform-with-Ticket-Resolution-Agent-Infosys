from flask import Flask, request, jsonify, render_template
import sqlite3
import os

from classifier import process_ticket
from database import init_db

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tickets.db")

# Initialize database when application starts
init_db()


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db_connection()

    try:
        tickets = conn.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC LIMIT 5"
        ).fetchall()

        total_tickets = conn.execute(
            "SELECT COUNT(*) FROM tickets"
        ).fetchone()[0]

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        tickets = []
        total_tickets = 0

    finally:
        conn.close()

    return render_template(
        "index.html",
        tickets=tickets,
        total_tickets=total_tickets
    )


@app.route("/ticket", methods=["POST"])
def create_ticket():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No ticket data received"
        }), 400

    employee_name = data.get("employee_name", "Anonymous")
    email = data.get("email", "")
    title = data.get("title", "")
    description = data.get("description", "")
    department = data.get("department", "IT")

    if not description:
        return jsonify({
            "error": "Ticket description is required"
        }), 400

    try:

        # --------------------------------
        # AI CLASSIFICATION
        # --------------------------------

        classification = process_ticket(
            f"{title} {description}",
            department
        )

        print("Classification result:")
        print(classification)

        category = classification["category"]
        severity = classification["severity"]
        priority = classification["priority"]
        confidence = classification["confidence"]

        # --------------------------------
        # SAVE TICKET TO DATABASE
        # --------------------------------

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tickets
            (
                employee_name,
                email,
                title,
                description,
                category,
                severity,
                priority,
                confidence,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_name,
            email,
            title,
            description,
            category,
            severity,
            priority,
            confidence,
            "Open"
        ))

        ticket_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # --------------------------------
        # RESPONSE
        # --------------------------------

        result = {
            "ticket_id": ticket_id,
            "title": title,
            "category": category,
            "severity": severity,
            "priority": priority,
            "confidence": confidence,
            "status": "Open"
        }

        return jsonify(result), 201

    except Exception as e:

        print("=" * 60)
        print("ERROR WHILE CREATING TICKET")
        print("=" * 60)
        print(f"Error: {e}")
        print("=" * 60)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    import threading
    import webbrowser

    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        threading.Timer(
            1.25,
            lambda: webbrowser.open(
                "http://127.0.0.1:5000"
            )
        ).start()

    app.run(debug=True)