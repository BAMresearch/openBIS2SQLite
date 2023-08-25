import argparse
import os
import typing
from pprint import pprint

import pgdumplib

from classes import DumpInsert, DumpTable
from cleaning import (
    add_defaults_to_rules,
    apply_mappings,
    clean_line,
    get_data_type_mapping,
)
from constants import (
    IGNORED_TABLES,
    PATH_TO_DUMP,
    PATH_TO_OUTPUT,
    PATH_TO_TESTING,
    BruhMoment,
)

DEBUG = 0


def parse_dump(path_to_dump: os.PathLike, path_to_output: os.PathLike) -> typing.NoReturn:  # noqa: E501

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


def test_gen_domain_list(path_to_dump: os.PathLike) -> typing.NoReturn:

    dump = pgdumplib.load(path_to_dump)

    type_mappings = {}

    for entry in dump.entries:
        if entry.desc == "DOMAIN":
            print(entry.defn)
            key, val = get_data_type_mapping(entry.defn)
            type_mappings[key] = val

    pprint(type_mappings)


def test_entry(path_to_dump: os.PathLike, entry_desc: str = "") -> typing.NoReturn:

    dump = pgdumplib.load(path_to_dump)

    if entry_desc == "ALL":
        for idx, entry in enumerate(dump.entries):
            print(entry)
            print("\n\n")

    else:
        for entry in dump.entries:
            if entry.desc == entry_desc:

                do = DumpTable(entry)

                print(do)
                print(do.body)
                print(dir(do))
                print("\n\n")


def get_all_inserts(path_to_dump: os.PathLike) -> typing.NoReturn:

    dump = pgdumplib.load(path_to_dump)

    tables = {}

    for entry in dump.entries:
        if entry.desc == "TABLE":
            table = DumpTable(entry)
            tables[table.tag] = table

    for ignored_table in IGNORED_TABLES:
        tables.pop(ignored_table)

    for table in tables:
        for entry in dump.table_data("public", table):
            print(entry)
            print("\n")


def new_parse_dump(path_to_dump: os.PathLike, path_to_output: os.PathLike) -> typing.NoReturn:  # noqa: E501

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
                table = DumpTable(entry)
                table.apply_mappings(type_mappings)
                tables[table.tag] = table

                file.write(str(table))

        for ignored_table in IGNORED_TABLES:
            tables.pop(ignored_table)

        print("Starting parsing insert entries")

        problematic_inserts = []

        cnt = 0
        for table_tag, table in tables.items():
            prev_entry = ""
            for entry in dump.table_data("public", table_tag):

                full_entry = prev_entry + entry[0]

                try:
                    insert = DumpInsert(full_entry)
                    cnt += 1
                    if cnt % 500 == 0:
                        print(f"created insert {cnt}")
                    file.write(str(insert))
                    prev_entry = ""
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

                    # print("\n\n")
                    # for attribute in set(insert.attributes) ^ set(table.get_attributes()):
                    #    print(attribute)
                    #    print("\n")
                    #    print(insert.attributes)
                    #    print("\n")
                    #    print(insert.values)
                    #    insert.pop_attribute(attribute)

        file.write("END;\n")
        for insert in problematic_inserts:
            print(insert)
            print("\n")
            print(f"{insert.attributes}, len: {len(insert.attributes)}")
            print("\n")
            print(f"{insert.values}, len: {len(insert.values)}")
            print("\n")

    print("Parsing finished")


def main():
    parser = argparse.ArgumentParser(description="True and Test run split")
    parser.add_argument("-t", "--test", action="store_true", help="Cleaning test run")
    parser.add_argument("-d", "--domain", action="store_true", help="Generate domain list")  # noqa: E501
    parser.add_argument("-e", "--entry", help="Debug entry")
    parser.add_argument("-n", "--new", action="store_true", help="new version")
    parser.add_argument("-i", "--insert", action="store_true", help="inserts")

    args = parser.parse_args()

    if args.test:
        test_cleaning(PATH_TO_TESTING)
    elif args.domain:
        test_gen_domain_list(PATH_TO_DUMP)
    elif args.entry:
        test_entry(PATH_TO_DUMP, args.entry)
    elif args.new:
        new_parse_dump(PATH_TO_DUMP, PATH_TO_OUTPUT)
    elif args.insert:
        get_all_inserts(PATH_TO_DUMP)
    else:
        parse_dump(PATH_TO_DUMP, PATH_TO_OUTPUT)


if __name__ == "__main__":
    main()
