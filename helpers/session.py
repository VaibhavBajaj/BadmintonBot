from dataclasses import dataclass
from typing import NamedTuple


# Key to accessing session data of each upcoming session
class SessionKey(NamedTuple):
    date: str
    start_time: str
    end_time: str
    location: str


# Data about one slot in an upcoming session
@dataclass
class Slot:
    level: str
    count: int
    booked: bool
    slot_added: bool

    def __init__(self, level):
        self.level = level
        self.count = 0
        self.booked = False
        self.slot_added = False