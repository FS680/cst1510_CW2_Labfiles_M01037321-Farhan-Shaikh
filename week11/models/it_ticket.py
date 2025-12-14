from typing import Optional


class ITTicket:
    """Represents an IT support ticket."""

    def __init__(
        self,
        ticket_db_id: int,
        ticket_id: str,
        priority: str,
        status: str,
        category: str,
        subject: str,
        description: str,
        created_date: str,
        resolved_date: Optional[str] = None,
        assigned_to: Optional[str] = None
    ):
        self.__db_id = ticket_db_id
        self.__ticket_id = ticket_id
        self.__priority = priority
        self.__status = status
        self.__category = category
        self.__subject = subject
        self.__description = description
        self.__created_date = created_date
        self.__resolved_date = resolved_date
        self.__assigned_to = assigned_to

    def get_db_id(self) -> int:
        """Return the database ID."""
        return self.__db_id

    def get_ticket_id(self) -> str:
        """Return the ticket ID."""
        return self.__ticket_id

    def get_priority(self) -> str:
        """Return the priority level."""
        return self.__priority

    def get_status(self) -> str:
        """Return the current status."""
        return self.__status

    def get_category(self) -> str:
        """Return the ticket category."""
        return self.__category

    def get_subject(self) -> str:
        """Return the ticket subject."""
        return self.__subject

    def get_description(self) -> str:
        """Return the ticket description."""
        return self.__description

    def get_created_date(self) -> str:
        """Return the creation date."""
        return self.__created_date

    def get_resolved_date(self) -> Optional[str]:
        """Return the resolution date if resolved."""
        return self.__resolved_date

    def get_assigned_to(self) -> Optional[str]:
        """Return who the ticket is assigned to."""
        return self.__assigned_to

    def assign_to(self, staff: str) -> None:
        """Assign the ticket to a staff member."""
        self.__assigned_to = staff

    def update_status(self, new_status: str) -> None:
        """Update the ticket status."""
        self.__status = new_status

    def close_ticket(self, resolved_date: str) -> None:
        """Close the ticket with a resolution date."""
        self.__status = "Resolved"
        self.__resolved_date = resolved_date

    def is_resolved(self) -> bool:
        """Check if the ticket is resolved."""
        return self.__status.lower() == "resolved"

    def is_critical(self) -> bool:
        """Check if the ticket has critical priority."""
        return self.__priority.lower() == "critical"

    def get_priority_level(self) -> int:
        """
        Return numeric priority level for sorting.

        Returns:
            int: 1 (Low) to 4 (Critical)
        """
        mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping.get(self.__priority.lower(), 0)

    def __str__(self) -> str:
        assigned = self.__assigned_to if self.__assigned_to else "Unassigned"
        return f"Ticket {self.__ticket_id}: {self.__subject} [{self.__priority}] – {self.__status} (assigned to: {assigned})"

    def __repr__(self) -> str:
        return self.__str__()
