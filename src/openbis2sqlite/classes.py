import re
import typing
from dataclasses import dataclass

from pgdumplib.dump import Entry

from openbis2sqlite.cleaning import (
    clean_change_parenthesis,
    clean_line,
    clean_defaults_body,
    parse_insert_attributes,
    parse_insert_values_ast,
    remove_apostrophes_phone_number,
    split_body_table,
    split_hb_table,
    split_insert,
)
from openbis2sqlite.constants import ParsingError, EntryType, NewlineInEntryError


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
    attributes: typing.List[str]

    def __init__(self, entry: Entry):

        sql_entry = entry.defn

        sql_entry = clean_line(sql_entry)

        self.header, temp_body = split_hb_table(sql_entry)
        temp_body = split_body_table(temp_body)
        self.body = clean_defaults_body(temp_body)

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
                line[1] = "TEXT"

        self.body = [" ".join(line) for line in self.body]


@dataclass
class DumpInsert():
    header: str
    attributes: typing.List[str]
    values: typing.List[str]
    table: str

    def __init__(self, entry: str, table_attrs: typing.Optional[typing.List[str]] = None):  # noqa: E501

        sql_entry = clean_line(entry)

        if not sql_entry.endswith(");"):
            # print(sql_entry)
            raise NewlineInEntryError

        self.header, temp_attributes, temp_values = split_insert(sql_entry)
        self.attributes = parse_insert_attributes(temp_attributes)
        temp_values = remove_apostrophes_phone_number(temp_values)
        temp_values = clean_change_parenthesis(temp_values)
        try:
            self.values = parse_insert_values_ast(temp_values)
        except SyntaxError as err:
            print("\n")
            print(sql_entry)
            raise SyntaxError(err)
        self.table = self.header.split(" ")[2]

        if not len(self.attributes) == len(self.values):
            if len(self.attributes) > len(self.values):
                self.attributes = self.attributes[:len(self.values)]
            else:
                self.values = self.values[:len(self.attributes)]

        if not table_attrs:
            return

        to_remove = set(self.attributes) ^ set(table_attrs)

        assert to_remove < set(self.attributes)

        for to_remove_attr in list(to_remove):
            self.pop_attribute(to_remove_attr)

        if not len(self.attributes) == len(self.values):
            print(f"attributes lenght: {len(self.attributes)}")
            print(f"values lenght: {len(self.values)}")
            for idx in range(min(len(self.attributes), len(self.values))):
                print(f"{self.attributes[idx]}: {self.values[idx]}")
            if len(self.attributes) < len(self.values):
                print(self.values[-1])
            else:
                print(self.attributes[-1])
            raise ParsingError

    def __str__(self) -> str:

        combined_attributes = ", ".join(self.attributes)
        combined_values = [f"\'{element}\'" if isinstance(element, str) else str(element) for element in self.values]  # noqa: E501
        combined_values = ", ".join(combined_values)
        combined_values = re.sub("None", "NULL", combined_values)

        return f"{self.header} ({combined_attributes}) VALUES ({combined_values});\n"

    def pop_attribute(self, attribute_name: str) -> str:
        attribute_index = self.attributes.index(attribute_name)

        self.attributes.pop(attribute_index)
        return self.values.pop(attribute_index)
