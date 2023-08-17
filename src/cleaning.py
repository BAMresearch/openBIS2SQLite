import re
import typing

CONVERTING_RULES = {
    "text": "TEXT",
    "real": "REAL",
    "integer": "INTEGER",
    "bigint": "INTEGER",
    "boolean": "INTEGER",
}


def clean_line(entry: str) -> str:
    entry = re.sub("public.", "", entry)
    entry = re.sub("true", "\"t\"", entry)
    entry = re.sub("false", "\"f\"", entry)
    entry = clean_constraints(entry)
    entry = clean_trim_after_pattern(entry, "with")
    entry = clean_trim_after_pattern(entry, "DEFAULT")
    return entry


def clean_constraints(entry: str) -> str:

    constraint_pat = re.compile(r"CONSTRAINT")
    domain_pat = re.compile(r"DOMAIN")

    constraint_found = constraint_pat.search(entry)

    if constraint_found:

        lines = entry.split("\n")

        lines = [line for line in lines if not constraint_pat.search(line)]

        is_domain = domain_pat.search(entry)

        if is_domain:
            # add semicolon to end of line
            lines[-2] = f"{lines[-2]};"
        else:
            # trim the leftover comma from last line of attribute definition
            lines[-3] = lines[-3][:-1]

        entry = "\n".join(lines)

    return entry


def clean_trim_after_pattern(entry: str, pattern: str) -> str:

    search_pat = re.compile(pattern)
    domain_pat = re.compile(r"DOMAIN")

    if not (search_pat.search(entry) and domain_pat.search(entry)):
        return entry

    entry_split = entry.split(pattern, 1)[0].rstrip()
    return f"{entry_split};\n"


def get_data_type_mapping(entry: str, clean: bool = True) -> typing.Tuple[str, str]:

    if clean:
        entry = clean_line(entry)

    key_part, val_part = entry.split(" AS ")
    key = key_part.split(" ")[2]
    val_unconverted = re.sub(r";\n", "", val_part)

    try:
        val = CONVERTING_RULES[val_unconverted]
    except KeyError:
        val = "BLOB"

    return key, val


def add_defaults_to_rules(rules: typing.Dict[str, str]) -> typing.Dict[str, str]:
    defaults = {
        "integer": "INTEGER",
        "character": "TEXT",
        "real": "REAL",
        "boolean": "INTEGER",
        "bigint": "INTEGER",
        "smallint": "INTEGER"
    }

    return rules | defaults


def apply_mappings(entry: str, rules: typing.Dict[str, str]) -> str:

    header, body = entry.split("(", 1)

    body = body.split(",")
    body = [line.strip().removesuffix("\n);").split(" ") for line in body]

    for line in body:
        try:
            line[1] = rules[line[1]]
        except KeyError:
            line[1] = "BLOB"

    body = [" ".join(line).rjust(4) for line in body]
    body = ",\n".join(body)

    entry = f"{header}(\n{body}\n);\n"

    # for key, val in rules.items():
    #     entry = re.sub(key, val, entry)

    return entry
