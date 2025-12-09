import pandas as pd
from app.data.db import connect_database

def get_all_tickets(conn):
    return pd.read_sql_query("SELECT * FROM it_tickets", conn)


def insert_ticket(conn, ticket_id, priority, status, category, subject, description,
                  created_date, resolved_date, assigned_to):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets
        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id, priority, status, category, subject, description,
        created_date, resolved_date, assigned_to
    ))

    conn.commit()
    return cursor.lastrowid
