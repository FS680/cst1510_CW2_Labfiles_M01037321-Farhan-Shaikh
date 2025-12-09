import pandas as pd
from app.data.db import connect_database

def add_incident(db, d, itype, level, state, detail, reporter=None):
    cursor = db.cursor()
    cursor.execute(
        """
            INSERT INTO cyber_incidents
            (date, incident_type, severity, status, description, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (d, itype, level, state, detail, reporter)
    )
    db.commit()
    return cursor.lastrowid

def fetch_incidents(db):
    return pd.read_sql_query("SELECT * FROM cyber_incidents", db)

def change_incident_state(db, inc_id, state):
    cursor = db.cursor()
    cursor.execute("UPDATE cyber_incidents SET status = ? WHERE id = ?", (state, inc_id))
    db.commit()
    return cursor.rowcount

def drop_incident(db, inc_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (inc_id,))
    db.commit()
    return cursor.rowcount

def type_totals(db):
    sql = """
        SELECT incident_type, COUNT(*) AS count
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY count DESC
    """
    return pd.read_sql_query(sql, db)

def high_severity_status_breakdown(db):
    sql = """
        SELECT status, COUNT(*) AS count
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY count DESC
    """
    return pd.read_sql_query(sql, db)
