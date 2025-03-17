"""Abstract classes for changes viewer."""
from __future__ import annotations


class ChangeListItem:
    """Item representing regular change list from Perforce.

    Args:
        change (str): id (number) of change
        user (str): who submitted
        desc (str): comment
        time (str): when it was committed (timestamp)
    """

    def __init__(self, change: str, user: str, desc: str, time: str):
        """Initialize ChangeListItem."""
        self.change = change
        self.user = user
        self.desc = desc
        self.time = time

    def to_data(self) -> dict:
        """Convert to data.

        Returns:
            dict: Data representation of the object.

        """
        return {
            "change": self.change,
            "user": self.user,
            "desc": self.desc,
            "time": self.time,
        }

    @classmethod
    def from_data(cls, data) -> ChangeListItem:
        """Create instance from data.

        Args:
            data (dict): Data to create instance from.

        Returns:
            ChangeListItem: Instance of the class.

        """
        return cls(**data)
