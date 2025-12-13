import bcrypt
import secrets
import time
import re

from db.db import connect_database
from db.users import get_user_by_username, insert_user

# ============================================================
# PASSWORD HASHING
# ============================================================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ============================================================
# USER AUTHENTICATION
# ============================================================
def register_user(username: str, password: str, role: str = "user") -> bool:
    """
    Register a new user in the DB.
    Returns True if successful, False if username exists.
    """
    conn = connect_database()
    if get_user_by_username(username):
        conn.close()
        return False

    pw_hash = hash_password(password)
    insert_user(username, pw_hash, role)
    conn.close()
    return True


def login_user(username: str, password: str) -> bool:
    """
    Login user by verifying credentials.
    Returns True on success, False otherwise.
    """
    user = get_user_by_username(username)
    if not user:
        return False

    stored_hash = user[2]  # password_hash column
    return verify_password(password, stored_hash)


# ============================================================
# SESSION MANAGEMENT
# ============================================================
def create_session(username: str) -> str:
    """
    Create a session token for logging in.
    """
    token = secrets.token_hex(16)
    return token


# ============================================================
# INPUT VALIDATION
# ============================================================
def validate_username(username: str):
    if not username:
        return False, "Username cannot be empty."
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3–20 characters."
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return False, "Only letters, numbers, and _ allowed."
    return True, ""


def validate_password(password: str):
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Must include uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Must include lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Must include number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Must include special character."
    return True, ""


def check_password_strength(pw: str) -> str:
    score = sum([
        len(pw) >= 8,
        bool(re.search(r"[A-Z]", pw)),
        bool(re.search(r"[a-z]", pw)),
        bool(re.search(r"[0-9]", pw)),
        bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw))
    ])
    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    return "Strong"
