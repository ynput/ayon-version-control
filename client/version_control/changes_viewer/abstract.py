class ChangeListItem:
    """Item representing regular change list from Perforce.

    Args:
        change (str): id (number) of change
        user (str): who submitted
        desc (str): comment
        time (str): when it was committed (timestamp)
    """

    def __init__(self, change, user, desc, time):
        self.change = change
        self.user = user
        self.desc = desc
        self.time = time

    def to_data(self):
        return {
            "change": self.change,
            "user": self.user,
            "desc": self.desc,
            "time": self.time,
        }

    @classmethod
    def from_data(cls, data):
        return cls(**data)
