import sqlite3
conn=sqlite3.connect('tickets.db')
print(conn.cursor().execute('SELECT ticket_id, created_at, status FROM tickets ORDER BY ticket_id DESC LIMIT 10').fetchall())
