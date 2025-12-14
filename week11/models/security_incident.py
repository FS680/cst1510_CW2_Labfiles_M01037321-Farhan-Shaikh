from datetime import datetime
from typing import Optional


class SecurityIncident:
    """Represents a cybersecurity incident in the platform."""

    def __init__(
        self,
        incident_id: int,
        date: str,
        incident_type: str,
        severity: str,
        status: str,
        description: str,
        reported_by: Optional[str] = None
    ):
        self.__id = incident_id
        self.__date = date
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
        self.__reported_by = reported_by

    def get_id(self) -> int:
        """Return the incident ID."""
        return self.__id

    def get_date(self) -> str:
        """Return the incident date."""
        return self.__date

    def get_incident_type(self) -> str:
        """Return the incident type."""
        return self.__incident_type

    def get_severity(self) -> str:
        """Return the severity level."""
        return self.__severity

    def get_status(self) -> str:
        """Return the current status."""
        return self.__status

    def get_description(self) -> str:
        """Return the incident description."""
        return self.__description

    def get_reported_by(self) -> Optional[str]:
        """Return who reported the incident."""
        return self.__reported_by

    def update_status(self, new_status: str) -> None:
        """Update the incident status."""
        self.__status = new_status

    def get_severity_level(self) -> int:
        """
        Return an integer severity level for sorting/comparison.

        Returns:
            int: 1 (Low) to 4 (Critical)
        """
        mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping.get(self.__severity.lower(), 0)

    def is_critical(self) -> bool:
        """Check if the incident is critical."""
        return self.__severity.lower() == "critical"

    def is_open(self) -> bool:
        """Check if the incident is still open."""
        return self.__status.lower() in ["open", "investigating"]

    def __str__(self) -> str:
        return f"Incident {self.__id} [{self.__severity.upper()}] {self.__incident_type} - {self.__status}"

    def __repr__(self) -> str:
        return self.__str__()
