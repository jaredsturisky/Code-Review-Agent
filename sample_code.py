# bad_sample.py

ADMIN_PASSWORD = "SuperSecret123!"  # Hard coded password

def login(username, password):
    if username == "admin" and password == ADMIN_PASSWORD:
        print("Login successful")
        return True
    else:
        print("Login failed")
        return False

def calculate_discount(price):
    # Illogical condition, discount is applied only when price is negative
    if price < 0:
        return price * 0.9
    return price

def delete_user(user_id):
    # No validation, logging, authorization check, or error handling
    print("Deleting user:", user_id)
    return True

login("admin", "SuperSecret123!")
print(calculate_discount(100))
delete_user(5)

