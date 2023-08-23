from enum import Enum, auto
from pathlib import Path

PATH_TO_DUMP = Path(Path().cwd().parent.parent, "backups", "dump_att_inserts.sql")

PATH_TO_OUTPUT = Path(Path().cwd().parent, "sqlite_dump.sql")

PATH_TO_TESTING = Path(Path().cwd(), "testing.sql")


class EntryType(Enum):
    DOMAIN = auto()
    TABLE = auto()
    INSERT = auto()
    OTHER = auto()


class BruhMoment(Exception):
    pass


CONVERTING_RULES = {
    "text": "TEXT",
    "real": "REAL",
    "integer": "INTEGER",
    "bigint": "INTEGER",
    "boolean": "INTEGER",
}

IGNORED_TABLES = [
    "core_plugins",
    "events",
    "external_data",
    "data_store_services",
    "data_stores",
    "events_search",
]
