import pandas as pd
from pathlib import Path
from app.data.db import connect_database

# Path to DATA folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "DATA"


def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table.

    Args:
        conn: database connection
        csv_path: Path to the CSV file
        table_name: target table name

    Returns:
        int: number of rows inserted
    """
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return 0

    df = pd.read_csv(csv_path)
    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)

    print(f"✅ Loaded {len(df)} rows into {table_name}")
    return len(df)


def load_all_csvs():
    """
    Load all CSV files into their respective tables.
    """
    conn = connect_database()
    total = 0

    total += load_csv_to_table(conn, DATA_DIR / "cyber_incidents.csv", "cyber_incidents")
    total += load_csv_to_table(conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata")
    total += load_csv_to_table(conn, DATA_DIR / "it_tickets.csv", "it_tickets")

    conn.close()
    return total
