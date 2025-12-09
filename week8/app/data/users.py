from app.data.db import connect_database

def fetch_user(uname):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (uname,))
    user_record = cursor.fetchone()
    connection.close()
    return user_record

def add_user(uname, pwd_hash, role_type='user'):
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (uname, pwd_hash, role_type)
    )
    connection.commit()
    connection.close()