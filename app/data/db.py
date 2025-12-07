import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "DATA"
DATABASE_FILE = DATA_DIR / "intelligence_platform.db"

def open_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_FILE.as_posix())
