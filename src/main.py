import pgdumplib
from pathlib import Path
from cleaning import clean_line

PATH_TO_DUMP = Path(Path().cwd().parent.parent, "backups", "dump_custom.sql")

dump = pgdumplib.load(PATH_TO_DUMP)

tables = set()

with open("schema.sql", "w") as schema_f, open("data.sql", "w") as data_f:

    for entry in dump.entries:
        if entry.desc == "TABLE":
            line = clean_line(entry.defn)
            table_name = line.split(" ")[2]
            tables.add(table_name)

            schema_f.write(line)

    for table in tables:
        for line in dump.table_data("public", table):
            data_f.write(clean_line(line[0]))
            data_f.write("\n")

        data_f.write("\n")
