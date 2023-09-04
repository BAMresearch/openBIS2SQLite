import argparse
import os
import typing
from pathlib import Path

import pgdumplib

from classes import DumpInsert, DumpTable
from cleaning import (
    add_defaults_to_rules,
    get_data_type_mapping,
)
from constants import (
    WHITELISTED_TABLES,
    BruhMoment,
    NewlineInEntryError,
)

import re

DEBUG = 0


def parse_dump(path_to_dump: os.PathLike, path_to_output: os.PathLike) -> typing.NoReturn:  # noqa: E501

    tables = {}
    type_mappings = {}

    print("Starting to parse the dump file")

    dump = pgdumplib.load(path_to_dump)

    with open(path_to_output, "w") as file:

        file.write("BEGIN;\n")

        print("Starting parsing domain entries")

        for entry in dump.entries:
            if entry.desc == "DOMAIN":
                key, val = get_data_type_mapping(entry.defn)
                type_mappings[key] = val

        type_mappings = add_defaults_to_rules(type_mappings)

        print("Starting parsing table entries")

        for entry in dump.entries:
            if entry.desc == "TABLE":
                if entry.tag not in WHITELISTED_TABLES:
                    continue
                if re.search(r"data_all", entry.defn):
                    print(entry.defn)
                table = DumpTable(entry)
                if re.search(r"data_all", entry.defn):
                    print(str(table))
                table.apply_mappings(type_mappings)
                tables[table.tag] = table

                file.write(str(table))

        print("Starting parsing insert entries")

        problematic_inserts = []

        for table_tag, table in tables.items():
            if table_tag not in WHITELISTED_TABLES:
                continue
            prev_entry = ""
            infloop_guard = False
            table_attrs = tables[table_tag].get_attributes()
            for entry in dump.table_data("public", table_tag):

                full_entry = prev_entry + entry[0]

                try:
                    insert = DumpInsert(full_entry, table_attrs)
                    file.write(str(insert))
                    prev_entry = ""
                    infloop_guard = False
                except ValueError as err:
                    print("Entry not well defined, Value Error new main")
                    print(err)
                    print("entry: ")
                    print(full_entry)
                    prev_entry = full_entry
                except BruhMoment as err:
                    print("Parsing error, BruhMoment new main")
                    print(err)
                    print("entry: ")
                    print(full_entry)
                    problematic_inserts.append(insert)
                except NewlineInEntryError as err:
                    # TODO: write a real debugger
                    # print("NewlineInEntryError new main")
                    # print(err)
                    # print("entry: ")
                    # print(full_entry)
                    # print(f"ENTRY OBJ LENGTH: {len(entry)}")
                    prev_entry = full_entry

                    if infloop_guard:
                        raise NewlineInEntryError

        file.write("END;\n")
    if len(problematic_inserts) == 0:
        print("No bad inserts found")
        print("Parsing finished")
        return

    print("FOUND PROBLEMATIC INSERTS")
    print("STARTING TO WRITE OUT PROBLEMATIC_INSERTS")

    for insert in problematic_inserts:
        print(insert)
        print(f"{insert.attributes}, len: {len(insert.attributes)}")
        print(f"{insert.values}, len: {len(insert.values)}")
        print("\n")

    print("Parsing finished")


def debug_data_all(path_to_dump):

    dump = pgdumplib.load(path_to_dump)

    for table in dump.entries:
        if not table.desc == "TABLE":
            continue
        if not re.search(r"data_all", table.defn):
            continue
        print(table)
        print("\n\n")
        print(table.defn)


def main():
    parser = argparse.ArgumentParser(description="True and Test run split")
    parser.add_argument("-i", "--input", help="Input (dump) file path")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug")

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise ValueError(f"Input {args.input} if not a valid filepath")

    output_path.touch()

    if args.debug:
        debug_data_all(input_path)
    else:
        parse_dump(input_path, output_path)


if __name__ == "__main__":
    main()
