import pandas as pd
from pathlib import Path
from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import migrate_users_from_file
from app.data.db import DB_PATH

DATABASE_FILE = Path("project_database.db")

def initialize_full_database():
    print("\n[1/4] Connecting to database...")
    conn = connect_database()
    print("Database connected successfully.")

    print("\n[2/4] Creating database tables...")
    create_all_tables(conn)
    print("All tables initialized.")

    print("\n[3/4] Loading users from file...")
    user_count = migrate_users_from_file()
    print(f"Loaded {user_count} user(s) into the system.")

    print("\n[4/4] Validating database structure...")
    cursor = conn.cursor()
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']

    print("\n=== Database Summary ===")
    print(f"{'Table':<25} {'Records':<15}")
    print("-" * 40)
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        record_count = cursor.fetchone()[0]
        print(f"{table:<25} {record_count:<15}")

    conn.close()
    print(f"\nDatabase location: {DATABASE_FILE.resolve()}")
    print("Setup complete!")

initialize_full_database()