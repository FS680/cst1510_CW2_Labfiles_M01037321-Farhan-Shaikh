import sqlite3
from typing import Any, Iterable, Optional, List, Tuple


class DatabaseManager:
    """Handles SQLite database connections and queries."""

    def __init__(self, db_path: str):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Establish database connection if not already connected."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row  # Enable column access by name

    def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def get_connection(self) -> sqlite3.Connection:
        """
        Get the current connection, creating one if needed.

        Returns:
            sqlite3.Connection: The active database connection
        """
        if self._connection is None:
            self.connect()
        return self._connection

    def execute_query(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        """
        Execute a write query (INSERT, UPDATE, DELETE).

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            sqlite3.Cursor: The cursor after execution
        """
        if self._connection is None:
            self.connect()

        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        self._connection.commit()
        return cur

    def fetch_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
        """
        Fetch a single row from the database.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            Optional[sqlite3.Row]: The row if found, None otherwise
        """
        if self._connection is None:
            self.connect()

        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()) -> List[sqlite3.Row]:
        """
        Fetch all rows from a query.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List[sqlite3.Row]: List of all matching rows
        """
        if self._connection is None:
            self.connect()

        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchall()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __del__(self):
        """Ensure connection is closed when object is destroyed."""
        self.close()
