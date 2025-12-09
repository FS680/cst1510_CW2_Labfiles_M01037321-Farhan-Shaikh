from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import migrate_users_from_file
from app.data.csv_loader import load_all_csvs


def setup_database_complete():
    print("\n=== DATABASE SETUP STARTED ===")

    conn = connect_database()

    print("✔ Creating tables...")
    create_all_tables(conn)

    print("✔ Migrating users from file...")
    users = migrate_users_from_file()

    print("✔ Loading CSV files into database...")
    total_rows = load_all_csvs()

    # Verify tables
    cursor = conn.cursor()
    tables = ["users", "cyber_incidents", "datasets_metadata", "it_tickets"]

    print("\n--- DATABASE SUMMARY ---")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} rows")

    conn.close()
    print("\n✅ DATABASE SETUP COMPLETE")
