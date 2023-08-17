import argparse
import os
import sys
import typing
from pathlib import Path
from pprint import pprint

import pgdumplib

from cleaning import (
    add_defaults_to_rules,
    apply_mappings,
    clean_line,
    get_data_type_mapping,
)

PATH_TO_DUMP = Path(Path().cwd().parent.parent, "backups", "dump_custom.sql")

PATH_TO_OUTPUT = Path(Path().cwd().parent, "sqlite_dump.sql")

PATH_TO_TESTING = Path(Path().cwd(), "testing.sql")

PATH_TO_TESTING_OUTPUT = sys.stdout

DEBUG = 0


def parse_dump(path_to_dump: os.PathLike, path_to_output: os.PathLike) -> typing.NoReturn:

    tables = set()
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
                line = clean_line(entry.defn)
                table_name = line.split(" ")[2]
                tables.add(table_name)
                line = apply_mappings(line, type_mappings)

                file.write(line)

        tables.remove("external_data")  # Problems with parsing, useless anyways

        print("Starting parsing insert entries")

        for table in tables:
            for line in dump.table_data("public", table):
                line = clean_line(line[0])
                file.write(line)
                file.write("\n")

            file.write("\n")

        file.write("END;\n")

    print("Parsing finished")


def test_cleaning(path_to_dump: os.PathLike) -> typing.NoReturn:

    with open(path_to_dump, "r") as infile:
        entry = infile.read()

    print(clean_line(entry))


def test_gen_entry_list(path_to_dump: os.PathLike) -> typing.NoReturn:

    dump = pgdumplib.load(path_to_dump)

    type_mappings = {}

    for entry in dump.entries:
        if entry.desc == "DOMAIN":
            key, val = get_data_type_mapping(entry.defn)
            type_mappings[key] = val

    pprint(type_mappings)


def main():
    parser = argparse.ArgumentParser(description="True and Test run split")
    parser.add_argument("-t", "--test", action="store_true", help="Cleaning test run")
    parser.add_argument("-l", "--list", action="store_true", help="Generate entry list")

    args = parser.parse_args()

    if args.test:
        test_cleaning(PATH_TO_TESTING)
    elif args.list:
        test_gen_entry_list(PATH_TO_DUMP)
    else:
        parse_dump(PATH_TO_DUMP, PATH_TO_OUTPUT)


if __name__ == "__main__":
    main()
