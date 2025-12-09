import pandas as pd
from app.data.db import connect_database

def add_ticket(db, t_id, pr, st, cat, title, desc, c_date, r_date=None, assigned=None):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO it_tickets (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (t_id, pr, st, cat, title, desc, c_date, r_date, assigned)
    )
    db.commit()
    return cursor.lastrowid

def fetch_tickets(db):
    return pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id DESC", db)

def edit_ticket(db, t_id, **fields):
    set_statement = ", ".join(f"{field} = ?" for field in fields)
    values = list(fields.values()) + [t_id]
    cursor = db.cursor()
    cursor.execute(f"UPDATE it_tickets SET {set_statement} WHERE ticket_id = ?", values)
    db.commit()
    return cursor.rowcount

def drop_ticket(db, t_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (t_id,))
    db.commit()
    return cursor.rowcount

def priority_overview(db):
    sql_query = "SELECT priority, COUNT(*) AS count FROM it_tickets GROUP BY priority ORDER BY count DESC"
    return pd.read_sql_query(sql_query, db)