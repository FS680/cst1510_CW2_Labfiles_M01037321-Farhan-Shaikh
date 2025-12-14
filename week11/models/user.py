class User:
    """Represents a user in the Multi-Domain Intelligence Platform."""

    def __init__(self, username: str, password_hash: str, role: str):
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role

    def get_username(self) -> str:
        """Return the username."""
        return self.__username

    def get_role(self) -> str:
        """Return the user's role."""
        return self.__role

    def get_password_hash(self) -> str:
        """Return the password hash (for verification purposes)."""
        return self.__password_hash

    def verify_password(self, plain_password: str, hasher) -> bool:
        """
        Check if a plain-text password matches this user's hash.

        Args:
            plain_password: The plain text password to verify
            hasher: Object with verify_password(plain, hashed) method

        Returns:
            bool: True if password matches, False otherwise
        """
        return hasher.verify_password(plain_password, self.__password_hash)

    def __str__(self) -> str:
        return f"User({self.__username}, role={self.__role})"

    def __repr__(self) -> str:
        return self.__str__()
