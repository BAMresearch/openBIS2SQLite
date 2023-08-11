import pgdumplib
import os
import sys
import typing
import argparse
from pathlib import Path
from cleaning import clean_line

PATH_TO_DUMP = Path(Path().cwd().parent.parent, "backups", "dump_custom.sql")

PATH_TO_OUTPUT = Path(Path().cwd().parent, "sqlite_dump.sql")

PATH_TO_TESTING = Path(Path().cwd(), "testing.sql")

PATH_TO_TESTING_OUTPUT = sys.stdout


def parse_dump(path_to_dump: os.PathLike, path_to_output: os.PathLike) -> typing.NoReturn:

    tables = set()

    print("Starting to parse the dump file")

    dump = pgdumplib.load(path_to_dump)

    with open(path_to_output, "w") as file:

        file.write("BEGIN;\n")

        for entry in dump.entries:
            if entry.desc == "TABLE":
                line = clean_line(entry.defn)
                table_name = line.split(" ")[2]
                tables.add(table_name)

                file.write(line)

        tables.remove("external_data")  # Problems with parsing, useless anyways

        for table in tables:
            for line in dump.table_data("public", table):
                file.write(clean_line(line[0]))
                file.write("\n")

            file.write("\n")

        file.write("END;\n")

    print("Parsing finished")


def test_cleaning(path_to_dump: os.PathLike) -> typing.NoReturn:

    with open(path_to_dump, "r") as infile:
        entry = infile.read()

    print(clean_line(entry))


def main():
    parser = argparse.ArgumentParser(description="True and Test run split")
    parser.add_argument("-t", "--test", action="store_true", help="Set if you want to test run")

    args = parser.parse_args()

    if args.test:
        test_cleaning(PATH_TO_TESTING)
    else:
        parse_dump(PATH_TO_DUMP, PATH_TO_OUTPUT)


if __name__ == "__main__":
    main()
