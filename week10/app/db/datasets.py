import pandas as pd
from db.db import connect_database

def get_all_datasets(conn):
    return pd.read_sql_query("SELECT * FROM datasets_metadata", conn)


def insert_dataset(conn, dataset_name, category, source, last_updated, record_count, file_size_mb):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))

    conn.commit()
    return cursor.lastrowid
