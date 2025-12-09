import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_users_table

PROJECT_ROOT = Path(__file__).resolve().parents[2]
USER_FILE = PROJECT_ROOT / "DATA" / "users.txt"

def signup(username, pwd, role_type='user'):
    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        connection.close()
        return False, f"Username '{username}' already exists."

    password_bytes = pwd.encode('utf-8')
    salt_value = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt_value).decode('utf-8')

    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed_password, role_type)
    )
    connection.commit()
    connection.close()

    return True, f"Account created for '{username}'."

def signin(username, pwd):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_info = cursor.fetchone()
    connection.close()

    if not user_info:
        return False, "Username not found."

    saved_hash = user_info[2]
    if bcrypt.checkpw(pwd.encode('utf-8'), saved_hash.encode('utf-8')):
        return True, f"Welcome back, {username}!"
    return False, "Incorrect password."

def import_users(file_path=USER_FILE):
    if not file_path.exists():
        return False, f"User file not found at {file_path}"

    connection = connect_database()
    create_users_table(connection)
    cursor = connection.cursor()

    imported = 0
    skipped = 0

    with file_path.open("r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            components = line.split(",")
            if len(components) < 3:
                continue
            username, password_hash, role = map(str.strip, components)
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                if cursor.rowcount > 0:
                    imported += 1
                else:
                    skipped += 1
            except Exception as error:
                print(f"Could not import {username}: {error}")

    connection.commit()
    connection.close()
    return True, f"Successfully imported {imported} users ({skipped} duplicates skipped)."