from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.data.incidents import (
    insert_incident,
    get_all_incidents,
    update_incident_status,
    delete_incident
)
from app.data.analytics import (
    get_incidents_by_type_count,
    get_high_severity_by_status,
    get_incident_types_with_many_cases
)
from app.services.user_service import (
    register_user,
    login_user,
    migrate_users_from_file
)
from app.services.setup_service import setup_database_complete


def main():
    print("=" * 60)
    print(" Week 8 — Database demo")
    print(" A short demonstration of user registration, login, incident CRUD, and analytics")
    print("=" * 60)

    setup_database_complete()

    print("\n--- User registration ---")
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(f"Registration result: {msg}")

    print("\n--- User login ---")
    success, msg = login_user("alice", "SecurePass123!")
    print(f"Login result: {msg}")

    print("\n--- Incident CRUD tests ---")
    conn = connect_database()

    incident_id = insert_incident(
        conn,
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        "alice"
    )
    print(f"Created incident with ID {incident_id}.")

    df = get_all_incidents(conn)
    print("\nAll incidents (table):")
    print(df)

    updated = update_incident_status(conn, incident_id, "Resolved")
    print(f"Updated {updated} incident(s).")

    deleted = delete_incident(conn, incident_id)
    print(f"Deleted {deleted} incident(s).")

    print("\n--- Analytics ---")

    print("\nIncidents by type:")
    print(get_incidents_by_type_count(conn))

    print("\nHigh-severity incidents by status:")
    print(get_high_severity_by_status(conn))

    print("\nIncident types with more than 3 cases:")
    print(get_incident_types_with_many_cases(conn, 3))

    conn.close()

    print("\nDemo complete — all operations finished.")


if __name__ == "__main__":
    main()
