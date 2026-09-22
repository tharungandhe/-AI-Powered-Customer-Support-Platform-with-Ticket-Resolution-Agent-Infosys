from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json
# Import your Milestone 1 process_ticket function (assuming it's in classifier.py)
from classifier import process_ticket 
# Import your new Milestone 2 pipeline
from rag.pipeline import run_pipeline
from flask_jwt_extended import JWTManager, create_access_token, verify_jwt_in_request, set_access_cookies, unset_jwt_cookies


from dotenv import load_dotenv
from agents import SupportPilot
from jira_service import JiraService
from email_service import EmailService
from concurrent.futures import ThreadPoolExecutor

# Load .env
load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_support_pilot_key'

# Initialize Milestone 3 services
support_pilot = SupportPilot()
jira_service = JiraService()
email_service = EmailService()
executor = ThreadPoolExecutor(max_workers=10)

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
_KNOWLEDGE_BASE_CACHE = None
def get_knowledge_base():
    global _KNOWLEDGE_BASE_CACHE
    if _KNOWLEDGE_BASE_CACHE is None:
        with open("data/knowledge_base.json", "r") as f:
            _KNOWLEDGE_BASE_CACHE = json.load(f)
    return _KNOWLEDGE_BASE_CACHE

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
    
    # Get Jira tickets count
    cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE jira_ticket_id IS NOT NULL")
    jira_tickets_row = cursor.fetchone()
    jira_tickets = jira_tickets_row["count"] if jira_tickets_row else 0
    
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
                          mean_time_to_resolution="4.2h",
                          jira_tickets=jira_tickets)

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
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ticket_id, email, title, category, priority, status, jira_ticket_id, created_at FROM tickets WHERE jira_ticket_id IS NOT NULL ORDER BY ticket_id DESC")
    jira_logs = cursor.fetchall()
    conn.close()
    return render_template("integrations.html", jira_logs=jira_logs)

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

@app.route("/api/ticket", methods=["POST"])
def process_ticket_api():
    data = request.get_json()
    ticket_title = data.get("title", "")
    ticket = data.get("ticket", "")
    user_email = data.get("email", "")

    if not ticket:
        return jsonify({
            "success": False,
            "message": "Ticket description required"
        }), 400

    # Multi-Agent Processing
    result = support_pilot.process_ticket(ticket)
    
    confidence = result["validation"]["confidence"]
    status = result["validation"]["status"]

    # Auto Resolution
    email_result = None
    if status == "AUTO_RESOLVE":
        if user_email:
            email_body = (
                "Hello,\n\n"
                + result["resolution"]["response"]
                + "\n\n"
                + "\n".join(
                    f"{i + 1}. {step}"
                    for i, step in enumerate(result["resolution"]["steps"])
                )
                + f"\n\nResolution confidence: {int(round(confidence))}%.\n\n"
                + "Regards,\nSupportPilot AI"
            )
            executor.submit(
                email_service.send_email,
                user_email, "Support Ticket Resolution", email_body
            )
            email_result = {"success": True, "message": "Email sent in background"}

        conn = database.get_connection()
        cursor = conn.cursor()
        title = ticket_title if ticket_title else result["diagnosis"]["category"]
        cursor.execute("""
            INSERT INTO tickets (email, title, description, category, priority, confidence, status, jira_ticket_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_email, title, ticket, result["diagnosis"]["category"], result["diagnosis"]["priority"], confidence, "Resolved", None))
        conn.commit()
        db_ticket_id = cursor.lastrowid
        conn.close()

        def background_autoresolve_jira(ticket_text, diagnosis, resolution_steps, conf, db_ticket_id):
            jira_res = jira_service.create_ticket(
                summary=f"[Auto-Resolved] {diagnosis['diagnosis']}",
                description=(
                    ticket_text
                    + "\n\nAI Diagnosis: "
                    + diagnosis["diagnosis"]
                    + "\n\nAI Resolution Provided:\n"
                    + "\n".join(resolution_steps)
                    + f"\n\nConfidence: {conf}%"
                ),
                priority=diagnosis["priority"]
            )
            
            if jira_res.get("success"):
                conn_bg = database.get_connection()
                cursor_bg = conn_bg.cursor()
                cursor_bg.execute(
                    "UPDATE tickets SET jira_ticket_id = ? WHERE ticket_id = ?",
                    (jira_res.get("ticket_id"), db_ticket_id)
                )
                conn_bg.commit()
                conn_bg.close()

        executor.submit(
            background_autoresolve_jira,
            ticket, result["diagnosis"], result["resolution"]["steps"], confidence, db_ticket_id
        )

        return jsonify({
            "success": True,
            "status": "AUTO_RESOLVE",
            "confidence": confidence,
            "result": result,
            "email": email_result,
            "jira": {"success": True, "message": "Jira ticket creating in background"}
        })

    # Escalation to Jira
    def background_escalation(ticket_text, diagnosis, resolution_steps, conf, u_email, db_ticket_id):
        jira_res = jira_service.create_ticket(
            summary=diagnosis["diagnosis"],
            description=(
                ticket_text
                + "\n\nAI Diagnosis: "
                + diagnosis["diagnosis"]
                + "\n\nAI Resolution:\n"
                + "\n".join(resolution_steps)
                + f"\n\nConfidence: {conf}%"
            ),
            priority="High"
        )
        
        if u_email:
            email_b = f"Hello,\n\nYour issue has been escalated to our support team.\n\nDiagnosis: {diagnosis['diagnosis']}\n\n"
            if jira_res.get("success"):
                email_b += f"A Jira ticket has been created: {jira_res.get('ticket_id')}."
            email_service.send_email(
                u_email,
                "Support Ticket Escalated",
                email_b
            )
            
        if jira_res.get("success"):
            conn_bg = database.get_connection()
            cursor_bg = conn_bg.cursor()
            cursor_bg.execute(
                "UPDATE tickets SET jira_ticket_id = ? WHERE ticket_id = ?",
                (jira_res.get("ticket_id"), db_ticket_id)
            )
            conn_bg.commit()
            conn_bg.close()

    conn = database.get_connection()
    cursor = conn.cursor()
    title = ticket_title if ticket_title else result["diagnosis"]["category"]
    cursor.execute("""
        INSERT INTO tickets (email, title, description, category, priority, confidence, status, jira_ticket_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_email, title, ticket, result["diagnosis"]["category"], result["diagnosis"]["priority"], confidence, "Open", None))
    conn.commit()
    db_ticket_id = cursor.lastrowid
    conn.close()

    executor.submit(
        background_escalation,
        ticket, result["diagnosis"], result["resolution"]["steps"], confidence, user_email, db_ticket_id
    )

    return jsonify({
        "success": True,
        "status": "ESCALATE",
        "confidence": confidence,
        "result": result,
        "jira": {"success": True, "message": "Jira ticket creating in background"},
        "email": {"success": True, "message": "Email sending in background"}
    })

@app.route("/api/ticket_data/<int:ticket_id>")
def get_ticket_data(ticket_id):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({
        "ticket_id": ticket["ticket_id"],
        "title": ticket["title"],
        "description": ticket["description"],
        "email": ticket["email"],
        "category": ticket["category"]
    })

@app.route("/api/dashboard/stats")
def dashboard_stats():
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

    # Recent tickets
    cursor.execute("SELECT ticket_id as id, title, category, priority, status FROM tickets ORDER BY ticket_id DESC LIMIT 5")
    recent_tickets = [dict(row) for row in cursor.fetchall()]

    # Deflection Rate
    cursor.execute("SELECT COUNT(*) as deflected FROM tickets WHERE confidence >= 95")
    deflected_row = cursor.fetchone()
    deflected_count = deflected_row["deflected"] if deflected_row else 0
    deflection_rate = round((deflected_count / total_tickets) * 100, 1) if total_tickets > 0 else 0

    conn.close()

    return jsonify({
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "high_priority": high_priority,
        "avg_confidence": avg_confidence,
        "deflection_rate": deflection_rate,
        "categories_labels": categories_labels,
        "categories_values": categories_values,
        "recent_tickets": recent_tickets
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "running",
        "service": "SupportPilot AI"
    })

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