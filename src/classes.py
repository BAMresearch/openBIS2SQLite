import re
import typing
from dataclasses import dataclass

import pgdumplib
from pgdumplib.dump import Entry

from cleaning import split_body, split_hbt, clean_line
from constants import EntryType


@dataclass
class DumpTable:
    pgdumplib_entry: Entry
    header: str
    body: typing.List[str]
    trailer: str
    constraint_flag: bool

    def __init__(self, entry: Entry):
        self.pgdumplib_entry = entry
        self.__entry_type: EntryType = EntryType[entry.desc]
        self.__tag: str = entry.tag

        sql_entry = entry.defn

        constraint_pat = re.compile(r"CONSTRAINT")
        self.constraint_flag = constraint_pat.search(sql_entry)

        sql_entry = clean_line(sql_entry)

        self.header, temp_body, self.trailer = split_hbt(sql_entry)
        self.body = split_body(temp_body)

    @property
    def entry_type(self) -> EntryType:
        return self.__entry_type

    @property
    def id(self) -> str:
        return self.__id

    def __hash__(self):
        return hash(self.__entry_type, self.__tag)

    def __str__(self) -> str:

        combined_body = ",\n".join([line.rjust(len(line) + 4) for line in self.body])

        return f"{self.header} (\n{combined_body}\n{self.trailer}"

    def _find_attributes(self) -> typing.NoReturn:
        pass
