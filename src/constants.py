from enum import Enum, auto


class EntryType(Enum):
    DOMAIN = auto()
    TABLE = auto()
    INSERT = auto()
    OTHER = auto()
