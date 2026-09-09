import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tickets.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            email TEXT,
            title TEXT,
            description TEXT,
            category TEXT,
            severity TEXT,
            priority TEXT,
            confidence REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Check if admin user exists
    cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@example.com",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            ("admin@example.com", generate_password_hash("admin"))
        )

    conn.commit()
    conn.close()

    print(f"Database initialized: {DB_PATH}")


if __name__ == "__main__":
    init_db()