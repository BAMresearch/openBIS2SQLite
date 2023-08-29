import re
import typing
from dataclasses import dataclass

import sqlparse
from pgdumplib.dump import Entry

from cleaning import (
    clean_change_parenthesis,
    clean_line,
    parse_insert_attributes,
    parse_insert_values,
    parse_insert_values_ast,
    parse_insert_values_sqlparse,
    remove_apostrophes_phone_number,
    split_body_table,
    split_hb_table,
    split_insert,
)
from constants import BruhMoment, EntryType, NewlineInEntryError


@dataclass
class DumpBase:
    pgdumplib_entry: Entry

    def __init__(self, entry: Entry):
        self.pgdumplib_entry = entry
        self.__entry_type: EntryType = EntryType[entry.desc]
        self.__tag: str = entry.tag

    @property
    def entry_type(self) -> EntryType:
        return self.__entry_type

    @property
    def tag(self) -> str:
        return self.__tag


@dataclass
class DumpTable(DumpBase):
    pgdumplib_entry: Entry
    header: str
    body: typing.List[str]
    constraint_flag: bool
    attributes: typing.List[str]

    def __init__(self, entry: Entry):

        sql_entry = entry.defn

        constraint_pat = re.compile(r"CONSTRAINT")
        self.constraint_flag = constraint_pat.search(sql_entry)

        sql_entry = clean_line(sql_entry)

        self.header, temp_body = split_hb_table(sql_entry)
        self.body = split_body_table(temp_body)

        super(DumpTable, self).__init__(entry=entry)

    def __hash__(self):
        return hash(self.__entry_type, self.__tag)

    def __str__(self) -> str:

        combined_body = ",\n".join([line.rjust(len(line) + 4) for line in self.body])

        return f"{self.header} (\n{combined_body}\n);\n"

    def get_attributes(self) -> typing.List[str]:
        attributes = []

        for line in self.body:
            attribute = line.split(" ")[0]
            attributes.append(attribute)

        return attributes

    def apply_mappings(self, rules: typing.Dict[str, str]) -> typing.NoReturn:

        pattern = re.compile(r".*varying\([0-9]+\)")
        self.body = [line.split(" ") for line in self.body]

        for line in self.body:
            if pattern.match(" ".join(line)):
                line.pop(2)
            try:
                line[1] = rules[line[1]]
            except KeyError:
                line[1] = "BLOB"

        self.body = [" ".join(line) for line in self.body]


@dataclass
class DumpInsert():
    pgdumplib_entry: Entry
    header: str
    attributes: typing.List[str]
    values: typing.List[str]
    table: str
    sqlparse_obj: sqlparse.sql.Statement

    def __init__(self, entry: str):

        sql_entry = clean_line(entry)
        # self.sqlparse_tokens = sqlparse.parse(sql_entry)[0]

        if not sql_entry.endswith(");"):
            print(sql_entry)
            raise NewlineInEntryError

        self.header, temp_attributes, temp_values = split_insert(sql_entry)
        self.attributes = parse_insert_attributes(temp_attributes)
        # self.values = parse_insert_values_sqlparse(self.sqlparse_tokens)
        print("temp values before")
        print(temp_values)
        temp_values = remove_apostrophes_phone_number(temp_values)
        temp_values = clean_change_parenthesis(temp_values)
        print("temp values after")
        print(temp_values)
        try:
            self.values = parse_insert_values_ast(temp_values)
        except SyntaxError as err:
            print("\n" * 5)
            print(sql_entry)
            raise SyntaxError(err)
        self.table = self.header.split(" ")[2]

        if not len(self.attributes) == len(self.values):
            # problem = commas in string values break parsing
            print(f"{self.attributes}, lenght: {len(self.attributes)}")
            print(f"{self.values}, lenght: {len(self.values)}")
            raise BruhMoment

    def __str__(self) -> str:

        combined_attributes = ", ".join(self.attributes)
        combined_values = [str(element)for element in self.values]
        combined_values = ", ".join(combined_values)
        combined_values = re.sub("None", "NULL", combined_values)

        return f"{self.header} ({combined_attributes}) VALUES ({combined_values});\n"

    def pop_attribute(self, attribute_name: str) -> str:
        attribute_index = self.attributes.index(attribute_name)

        self.attributes.pop(attribute_index)
        return self.values.pop(attribute_index)
