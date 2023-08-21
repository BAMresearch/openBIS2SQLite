import typing
from dataclasses import dataclass

import pgdumplib

from cleaning import split_body, split_hbt
from constants import EntryType


@dataclass
class DumpObject:
    pgdumplib_entry: pgdumplib.dump.Entry
    header: str
    body: typing.List[str]
    trailer: str

    def __init__(self, entry: pgdumplib.dump.Entry):
        self.pgdumplib_entry = entry
        self.__entry_type: EntryType = EntryType[entry.desc]
        self.__tag: str = entry.tag

        self.header, self.body, self.trailer = split_hbt(entry)
        self.body = split_body(self.body)

    @property
    def entry_type(self) -> EntryType:
        return self.__entry_type

    @property
    def id(self) -> str:
        return self.__id

    def __hash__(self):
        return hash(self.__entry_type, self.__tag)
