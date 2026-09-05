from dataclasses import dataclass

from utils.enums import eventAccess

@dataclass
class event_log:
    timestamp: int
    access_type: eventAccess
