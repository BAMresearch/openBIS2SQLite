import re


def clean_line(entry: str) -> str:
    entry = re.sub("public.", "", entry)
    entry = re.sub("true", "\"t\"", entry)
    entry = re.sub("false", "\"f\"", entry)
    entry = clean_constraints(entry)
    return entry


def clean_constraints(entry: str) -> str:

    pattern = re.compile(r"CONSTRAINT")

    constraint_found = pattern.search(entry)

    if constraint_found:

        lines = entry.split("\n")

        lines = [line for line in lines if not pattern.search(line)]

        # trim the leftover comma from last line of attribute definition
        lines[-3] = lines[-3][:-1]

        entry = "\n".join(lines)

    return entry
