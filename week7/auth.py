import os
import time
import bcrypt
import secrets
import re

USER_FILE = "users.txt"
SESS_FILE = "sessions.txt"
ATTEMPT_FILE = "failed_attempts.txt"

LOCK_TIME = 5 * 60
MAX_TRIES = 3

def ensure_file(path):
    if not os.path.exists(path):
        open(path, "w").close()

def read_lines(path):
    ensure_file(path)
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]

def write_lines(path, data):
    with open(path, "w") as f:
        for item in data:
            f.write(item + "\n")

def make_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_hash(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def new_session(user):
    token = secrets.token_hex(20)
    timestamp = time.time()
    with open(SESS_FILE, "a") as sess:
        sess.write(f"{user},{token},{timestamp}\n")
    return token

def load_attempts():
    data = read_lines(ATTEMPT_FILE)
    attempts = {}
    for entry in data:
        user, cnt, ts = entry.split(",")
        attempts[user] = (int(cnt), float(ts))
    return attempts

def store_attempts(attempt_data):
    out = [f"{u},{c},{t}" for u, (c, t) in attempt_data.items()]
    write_lines(ATTEMPT_FILE, out)

def register(username, pwd, role="user"):
    ensure_file(USER_FILE)
    for line in read_lines(USER_FILE):
        saved_user = line.split(",")[0]
        if saved_user == username:
            return False
    hashed = make_hash(pwd)
    with open(USER_FILE, "a") as f:
        f.write(f"{username},{hashed},{role}\n")
    return True

def user_login(username, pwd):
    attempts = load_attempts()
    now = time.time()

    if username in attempts:
        tries, last = attempts[username]
        if tries >= MAX_TRIES and (now - last) < LOCK_TIME:
            remaining = int((LOCK_TIME - (now - last)) // 60)
            print(f"Account locked. Try again in {remaining} minutes.")
            return False
        if now - last >= LOCK_TIME:
            attempts[username] = (0, 0)
            store_attempts(attempts)

    for entry in read_lines(USER_FILE):
        user, hash_pass, *_ = entry.split(",")
        if user == username:
            if check_hash(pwd, hash_pass):
                attempts[username] = (0, 0)
                store_attempts(attempts)
                return True
            fail_count = attempts.get(username, (0, 0))[0] + 1
            attempts[username] = (fail_count, now)
            store_attempts(attempts)
            print(f"Incorrect password. Attempt {fail_count}/{MAX_TRIES}")
            return False

    return False

def username_ok(user):
    if not (3 <= len(user) <= 20):
        return False, "Username must be between 3–20 characters."
    if " " in user:
        return False, "Username cannot contain spaces."
    if not re.match(r"^[A-Za-z0-9_]+$", user):
        return False, "Username can contain only letters, numbers, and underscores."
    return True, ""

def password_ok(pwd):
    if not (6 <= len(pwd) <= 50):
        return False, "Password must be 6–50 characters long."
    if not re.search(r"[A-Z]", pwd):
        return False, "Include at least one uppercase letter."
    if not re.search(r"[a-z]", pwd):
        return False, "Include at least one lowercase letter."
    if not re.search(r"[0-9]", pwd):
        return False, "Include at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
        return False, "Include at least one special character."
    return True, ""

def strength(pwd):
    score = sum([
        len(pwd) >= 8,
        bool(re.search(r"[A-Z]", pwd)),
        bool(re.search(r"[a-z]", pwd)),
        bool(re.search(r"[0-9]", pwd)),
        bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd))
    ])
    return ["Weak", "Medium", "Strong"][2 if score == 5 else 1 if score >= 3 else 0]

def menu():
    print("\n" + "=" * 55)
    print("  AUTHENTICATION MODULE — MULTI-DOMAIN PLATFORM")
    print("=" * 55)
    print("  [1] Register")
    print("  [2] Login")
    print("  [3] Exit")
    print("-" * 55)

def main():
    print("\nWelcome to Week 7 — Authentication System\n")
    while True:
        menu()
        choice = input("Choose (1-3): ").strip()

        if choice == "1":
            print("\n-- REGISTER NEW ACCOUNT --")
            username = input("Username: ").strip()
            ok, msg = username_ok(username)
            if not ok:
                print("Error:", msg)
                continue

            pwd = input("Password: ").strip()
            ok, msg = password_ok(pwd)
            if not ok:
                print("Error:", msg)
                continue

            print("Password Strength:", strength(pwd))

            if pwd != input("Confirm Password: ").strip():
                print("Error: Password mismatch.")
                continue

            role = input("Role (user/admin/analyst): ").lower().strip()
            if role not in ["user", "admin", "analyst"]:
                role = "user"

            register(username, pwd, role)
            print("Registration successful!")

        elif choice == "2":
            print("\n-- LOGIN --")
            u = input("Username: ").strip()
            p = input("Password: ").strip()

            if user_login(u, p):
                tk = new_session(u)
                print("Login successful!")
                print("Session Token:", tk)
                input("Press Enter to continue...")
            else:
                print("Login failed.")
                input("Press Enter to continue...")

        elif choice == "3":
            print("\nExiting system. Goodbye.\n")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
