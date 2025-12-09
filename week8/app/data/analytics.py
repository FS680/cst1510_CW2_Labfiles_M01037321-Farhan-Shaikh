import pandas as pd
from db import connect_database

def fetch_type_stats(connection):
    query = """
        SELECT incident_type, COUNT(*) AS count
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY count DESC
    """
    return pd.read_sql_query(query, connection)

def fetch_high_severity_status(connection):
    sql = """
        SELECT status, COUNT(*) AS count
        FROM cyber_incidents
        WHERE severity = 'High'
        GROUP BY status
        ORDER BY count DESC
    """
    return pd.read_sql_query(sql, connection)

def filter_incident_types(connection, threshold=5):
    statement = """
        SELECT incident_type, COUNT(*) AS count
        FROM cyber_incidents
        GROUP BY incident_type
        HAVING COUNT(*) > ?
        ORDER BY count DESC
    """
    return pd.read_sql_query(statement, connection, params=(threshold,))
