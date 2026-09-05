from enum import Enum

class eventAccess(Enum):
    Start = 1
    End = 2
    Cancel = 3

class adminAccess(Enum):
    create_channel = 1