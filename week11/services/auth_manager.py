import bcrypt
import re
from typing import Optional, Tuple
from models.user import User
from services.database_manager import DatabaseManager


class PasswordHasher:
    """Handles password hashing and verification using bcrypt."""

    @staticmethod
    def hash_password(plain: str) -> str:
        """
        Hash a plain text password using bcrypt.

        Args:
            plain: Plain text password

        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """
        Verify a plain text password against a hash.

        Args:
            plain: Plain text password
            hashed: Hashed password

        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False


class AuthManager:
    """Handles user registration, login, and authentication."""

    def __init__(self, db: DatabaseManager):
        """
        Initialize the authentication manager.

        Args:
            db: DatabaseManager instance for database operations
        """
        self._db = db
        self._hasher = PasswordHasher()

    def register_user(self, username: str, password: str, role: str = "user") -> bool:
        """
        Register a new user in the system.

        Args:
            username: Username for the new user
            password: Plain text password
            role: User role (default: "user")

        Returns:
            bool: True if registration successful, False if username exists
        """
        # Check if user already exists
        existing_user = self.get_user_by_username(username)
        if existing_user is not None:
            return False

        # Hash password and insert user
        password_hash = self._hasher.hash_password(password)
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        return True

    def login_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user and return User object if successful.

        Args:
            username: Username to authenticate
            password: Plain text password

        Returns:
            Optional[User]: User object if authentication successful, None otherwise
        """
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )

        if row is None:
            return None

        username_db = row["username"]
        password_hash_db = row["password_hash"]
        role_db = row["role"]

        if self._hasher.verify_password(password, password_hash_db):
            return User(username_db, password_hash_db, role_db)

        return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username.

        Args:
            username: Username to search for

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        row = self._db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )

        if row is None:
            return None

        return User(row["username"], row["password_hash"], row["role"])

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format.

        Args:
            username: Username to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty."
        if len(username) < 3 or len(username) > 20:
            return False, "Username must be 3–20 characters."
        if not re.match(r"^[A-Za-z0-9_]+$", username):
            return False, "Only letters, numbers, and _ allowed."
        return True, ""

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.

        Args:
            password: Password to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if not re.search(r"[A-Z]", password):
            return False, "Must include uppercase letter."
        if not re.search(r"[a-z]", password):
            return False, "Must include lowercase letter."
        if not re.search(r"[0-9]", password):
            return False, "Must include number."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Must include special character."
        return True, ""

    @staticmethod
    def check_password_strength(password: str) -> str:
        """
        Check password strength and return rating.

        Args:
            password: Password to check

        Returns:
            str: "Weak", "Medium", or "Strong"
        """
        score = sum([
            len(password) >= 8,
            bool(re.search(r"[A-Z]", password)),
            bool(re.search(r"[a-z]", password)),
            bool(re.search(r"[0-9]", password)),
            bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
        ])

        if score <= 2:
            return "Weak"
        elif score <= 4:
            return "Medium"
        return "Strong"
