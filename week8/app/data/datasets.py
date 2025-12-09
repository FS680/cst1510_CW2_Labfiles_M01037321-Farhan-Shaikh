import pandas as pd
from app.data.db import connect_database

def add_data_entry(db, name, cat, src, updated_at, records, size_mb):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO datasets_metadata (dataset_name, category, source, last_updated, record_count, file_size_mb) VALUES (?, ?, ?, ?, ?, ?)",
        (name, cat, src, updated_at, records, size_mb)
    )
    db.commit()
    return cursor.lastrowid

def fetch_datasets(db):
    return pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY id DESC", db)

def modify_dataset(db, ds_id, **fields):
    update_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [ds_id]
    cursor = db.cursor()
    cursor.execute(f"UPDATE datasets_metadata SET {update_clause} WHERE id = ?", values)
    db.commit()
    return cursor.rowcount

def remove_dataset(db, ds_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (ds_id,))
    db.commit()
    return cursor.rowcount

def category_breakdown(db):
    sql_query = "SELECT category, COUNT(*) AS count FROM datasets_metadata GROUP BY category ORDER BY count DESC"
    return pd.read_sql_query(sql_query, db)
