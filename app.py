from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json
# Import your Milestone 1 process_ticket function (assuming it's in classifier.py)
from classifier import process_ticket 
# Import your new Milestone 2 pipeline
from rag.pipeline import run_pipeline
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, set_access_cookies, unset_jwt_cookies

app = Flask(__name__)
app.secret_key = 'super_secret_support_pilot_key'

# Configure JWT
app.config["JWT_SECRET_KEY"] = "super_secret_jwt_support_pilot_key"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)

@app.before_request
def require_login():
    allowed_routes = ['login', 'api_login', 'mock_google_login', 'static']
    if request.endpoint not in allowed_routes:
        try:
            verify_jwt_in_request()
        except:
            return redirect(url_for('login'))

# Load the Milestone 2 Knowledge Base dynamically
def get_knowledge_base():
    with open("data/knowledge_base.json", "r") as f:
        return json.load(f)

import database

@app.route("/")
def index():
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Get total tickets
    cursor.execute("SELECT COUNT(*) as count FROM tickets")
    total_tickets = cursor.fetchone()["count"]
    
    # Get recent tickets
    cursor.execute("SELECT ticket_id as id, title, category, priority FROM tickets ORDER BY ticket_id DESC LIMIT 5")
    tickets = cursor.fetchall()
    
    conn.close()
    
    return render_template("index.html", total_tickets=total_tickets, tickets=tickets)

@app.route("/dashboard")
def dashboard():
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Get total tickets
    cursor.execute("SELECT COUNT(*) as count FROM tickets")
    total_tickets = cursor.fetchone()["count"]
    
    # Get open tickets
    cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE status != 'Closed' AND status != 'Resolved'")
    open_tickets = cursor.fetchone()["count"]
    
    # Get high priority tickets
    cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE priority IN ('P1', 'P2')")
    high_priority = cursor.fetchone()["count"]
    
    # Get average AI confidence
    cursor.execute("SELECT AVG(confidence) as avg_conf FROM tickets")
    avg_confidence_row = cursor.fetchone()
    avg_confidence = round(avg_confidence_row["avg_conf"], 1) if avg_confidence_row["avg_conf"] else 0
    
    # Get recent tickets for the activity feed
    cursor.execute("SELECT ticket_id as id, title, category, priority, status, created_at FROM tickets ORDER BY ticket_id DESC")
    recent_tickets = cursor.fetchall()

    # Tickets by category
    cursor.execute("SELECT category, COUNT(*) as count FROM tickets GROUP BY category")
    category_counts = cursor.fetchall()
    categories_labels = []
    categories_values = []
    for row in category_counts:
        cat = row["category"]
        if not cat or cat.strip() == "":
            cat = "Unknown"
        categories_labels.append(cat)
        categories_values.append(row["count"])
        
    # Deflection Rate
    cursor.execute("SELECT COUNT(*) as deflected FROM tickets WHERE confidence >= 95")
    deflected_row = cursor.fetchone()
    deflected_count = deflected_row["deflected"] if deflected_row else 0
    deflection_rate = round((deflected_count / total_tickets) * 100, 1) if total_tickets > 0 else 0
    
    conn.close()
    
    return render_template("dashboard.html", 
                          total_tickets=total_tickets, 
                          open_tickets=open_tickets,
                          high_priority=high_priority,
                          avg_confidence=avg_confidence,
                          recent_tickets=recent_tickets,
                          categories_labels=json.dumps(categories_labels),
                          categories_values=json.dumps(categories_values),
                          deflection_rate=deflection_rate,
                          mean_time_to_resolution="4.2h")

@app.route("/agents")
def agents():
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count, AVG(confidence) as avg_conf FROM tickets")
    row = cursor.fetchone()
    triage_count = row["count"] if row else 0
    triage_acc = round(row["avg_conf"], 1) if row and row["avg_conf"] else 0
    
    conn.close()
    
    # Simulating some stats for the RAG engine since we don't have explicit logs for it yet
    rag_generated = triage_count  # Assuming RAG ran on all tickets
    
    return render_template("agents.html", 
                          triage_count=triage_count, 
                          triage_acc=triage_acc,
                          rag_generated=rag_generated)

@app.route("/integrations")
def integrations():
    return render_template("integrations.html")

@app.route("/settings")
def settings():
    # Provide some mock data for settings
    user_settings = {
        "name": "Admin User",
        "email": "admin@example.com",
        "confidence_threshold": 95,
        "auto_triage": True,
        "auto_reply": False,
        "theme": "Light",
        "language": "English (US)",
        "timezone": "UTC-5 (Eastern Time)"
    }
    return render_template("settings.html", settings=user_settings)

@app.route("/analytics")
def analytics():
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Tickets by category
    cursor.execute("SELECT category, COUNT(*) as count FROM tickets GROUP BY category")
    category_counts = cursor.fetchall()
    
    # Calculate percentages for categories
    total_tickets = sum(row["count"] for row in category_counts) if category_counts else 1
    categories_data = []
    for row in category_counts:
        cat = row["category"]
        if cat is None or cat.strip() == "":
            cat = "Unknown"
        pct = round((row["count"] / total_tickets) * 100)
        categories_data.append({"name": cat, "count": row["count"], "percentage": pct})
    
    # Sort by count descending
    categories_data = sorted(categories_data, key=lambda x: x["count"], reverse=True)
    
    # Deflection Rate (tickets with confidence >= 95 as a proxy for deflection)
    cursor.execute("SELECT COUNT(*) as deflected FROM tickets WHERE confidence >= 95")
    deflected_row = cursor.fetchone()
    deflected_count = deflected_row["deflected"] if deflected_row else 0
    deflection_rate = round((deflected_count / total_tickets) * 100, 1) if total_tickets > 0 else 0
    
    conn.close()
    
    return render_template("analytics.html", 
                           categories=categories_data,
                           deflection_rate=deflection_rate,
                           total_tickets=total_tickets)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    if data and data.get("email") and data.get("password"):
        session['logged_in'] = True
        session['user'] = data.get("email")
        access_token = create_access_token(identity=data.get("email"))
        response = jsonify({"success": True})
        set_access_cookies(response, access_token)
        return response
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/login/google/mock", methods=["POST"])
def mock_google_login():
    session['logged_in'] = True
    session['user'] = "google_user@example.com"
    access_token = create_access_token(identity="google_user@example.com")
    response = jsonify({"success": True})
    set_access_cookies(response, access_token)
    return response

@app.route("/logout")
def logout():
    session.clear()
    response = redirect(url_for('login'))
    unset_jwt_cookies(response)
    return response

@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    
    if not ticket:
        return "Ticket not found", 404
        
    ticket_dict = dict(ticket)
    # Give the ticket an ID suitable for the RAG pipeline display
    ticket_dict["id"] = f"T-2023-{ticket_id}" 
    
    # Run the RAG pipeline to get resolution and relevant documents
    rag_output = run_pipeline(ticket_dict, get_knowledge_base())
    
    return render_template("ticket.html", ticket=ticket_dict, rag_output=rag_output)

@app.route("/resolution")
def latest_resolution():
    from flask import redirect, url_for
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY ticket_id DESC LIMIT 1")
    ticket = cursor.fetchone()
    conn.close()
    if ticket:
        return redirect(url_for('view_ticket', ticket_id=ticket["ticket_id"]))
    return "No tickets found to resolve. Please submit a ticket first.", 404

@app.route("/ticket", methods=["POST"])
def create_ticket():
    data = request.json
    
    # Milestone 1: Classification & Severity
    ticket_desc = data.get("description", "")
    ticket_title = data.get("title", "Support Request")
    classification_result = process_ticket(ticket_desc)
    category = classification_result.get("category", "Unknown")
    severity = classification_result.get("severity", "Low")
    priority = classification_result.get("priority", "P4")
    confidence = classification_result.get("confidence", 95.0)
    
    # Save ticket to database
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (employee_name, email, title, description, category, severity, priority, confidence, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("employee_name", ""),
        data.get("email", ""),
        ticket_title,
        ticket_desc,
        category,
        severity,
        priority,
        confidence,
        "Open"
    ))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()

    # Milestone 2: Prepare ticket format for the RAG pipeline
    ticket_dict = {
        "id": f"T-2023-{ticket_id}",
        "title": ticket_title,
        "description": ticket_desc,
        "category": category,
        "priority": priority
    }
    
    # Milestone 2: Generate the resolution
    rag_output = run_pipeline(ticket_dict, get_knowledge_base())
    
    # Combine results to send back to the frontend
    result = {
        "ticket_id": ticket_id,
        "ticket": ticket_desc,
        "category": category,
        "severity": severity,
        "priority": priority,
        "confidence": confidence,
        "status": "Open",
        "resolution": rag_output["resolution"],
        "title": ticket_title
    }
    
    return jsonify(result)

import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    import os
    # Only open the browser once, not every time the auto-reloader kicks in
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1.5, open_browser).start()
    app.run(debug=True)