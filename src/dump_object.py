import typing

from dataclasses import dataclass

import pgdumplib
from pgdumplib.dump import Entry

from cleaning import split_body, split_hbt
from constants import EntryType


@dataclass
class DumpObject:
    pgdumplib_entry: Entry
    header: str
    body: typing.List[str]
    trailer: str

    def __init__(self, entry: Entry):
        self.pgdumplib_entry = entry
        self.__entry_type: EntryType = EntryType[entry.desc]
        self.__tag: str = entry.tag

        self.header, temp_body, self.trailer = split_hbt(entry.defn)
        self.body = split_body(temp_body)

    @property
    def entry_type(self) -> EntryType:
        return self.__entry_type

    @property
    def id(self) -> str:
        return self.__id

    def __hash__(self):
        return hash(self.__entry_type, self.__tag)

    def __str__(self):

        combined_body = ",\n".join([line.rjust(len(line) + 4) for line in self.body])

        return f"{self.header} (\n{combined_body}\n{self.trailer}"
