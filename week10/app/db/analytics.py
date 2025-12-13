import pandas as pd
from db import connect_database

def get_incidents_by_type_count(conn):
    """
    Count incidents by type.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) AS count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)


def get_high_severity_by_status(conn):
    """
    Count High severity incidents by status.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) AS count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn)


def get_incident_types_with_many_cases(conn, min_count=5):
    """
    Find incident types with more than X cases.
    Uses: SELECT, FROM, GROUP BY, HAVING, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) AS count
    FROM cyber_incidents
    GROUP BY incident_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    return pd.read_sql_query(query, conn, params=(min_count,))
