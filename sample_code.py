import sqlite3

API_KEY = "sk_live_1234567890abcdef"
ADMIN_PASSWORD = "password123"

def get_user(username):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)

    user = cursor.fetchone()

    try:
        print("API key is:", API_KEY)
        print("Admin password is:", ADMIN_PASSWORD)

        if user:
            return user
    except Exception:
        pass

    return None

def login(username, password):
    user = get_user(username)

    if user and password == ADMIN_PASSWORD:
        return {
            "success": True,
            "token": "jwt_token_hardcoded_in_source"
        }

    return {"success": False}