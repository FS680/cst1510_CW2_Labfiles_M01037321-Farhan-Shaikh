import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
from app.data.schema import create_users_table

DATA_DIR = Path("DATA")

def register_user(username, password, role="user"):
    if get_user_by_username(username):
        return False, "Username already exists."

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    insert_user(username, password_hash, role)
    return True, f"User '{username}' registered successfully."


def login_user(username, password):
    user = get_user_by_username(username)

    if not user:
        return False, "User not found."

    stored_hash = user[2]

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return True, "Login successful!"
    else:
        return False, "Incorrect password."


def migrate_users_from_file(filepath=DATA_DIR / "users.txt"):
    conn = connect_database()
    create_users_table(conn)
    cursor = conn.cursor()

    if not filepath.exists():
        conn.close()
        return 0

    count = 0
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]

                cursor.execute(
                    "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, "user")
                )

                if cursor.rowcount > 0:
                    count += 1

    conn.commit()
    conn.close()
    return count
