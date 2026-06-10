import sqlite3

# Issue 1: hardcoded credentials (your guidelines: "Reject hardcoded credentials")
DATABASE_PASSWORD = "admin123"
API_SECRET = "sk-totally-real-secret-key-9999"

def get_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Issue 2: SQL injection via string formatting (your guidelines: "Reject SQL injection vulnerabilities")
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    cursor.execute(query)
    return cursor.fetchall()

def risky_operation():
    try:
        result = 10 / 0
    except:
        # Issue 3: empty catch block (your guidelines: "Reject empty catch blocks")
        pass