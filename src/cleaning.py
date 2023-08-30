import re
import typing
from ast import literal_eval

import sqlparse

from constants import CONVERTING_RULES, BruhMoment


def clean_line(entry: str) -> str:
    entry = re.sub("public.", "", entry)
    entry = re.sub("true", "True", entry)
    entry = re.sub("false", "False", entry)
    entry = clean_constraints(entry)
    entry = clean_trim_after_pattern(entry, "with", "DOMAIN")
    entry = clean_trim_after_pattern(entry, "DEFAULT", r".*(DOMAIN|TABLE).*")
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


def clean_trim_after_pattern(entry: str, pattern: str, check: str) -> str:

    search_pat = re.compile(pattern)
    domain_pat = re.compile(check)

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
        val = "TEXT"  # changed from blob

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

    pattern = re.compile(r".*varying\([0-9]+\)")

    for line in body:
        if pattern.match(" ".join(line)):
            line.pop(2)
        try:
            line[1] = rules[line[1]]
        except KeyError:
            line[1] = "TEXT"

    body = [" ".join(line) for line in body]
    body = [line.rjust(len(line) + 4) for line in body]
    body = ",\n".join(body)

    entry = f"{header}(\n{body}\n);\n"

    return entry


def split_hb_table(entry: str) -> typing.Tuple[str, str]:
    header, body = entry.split("(", 1)
    header = header.strip()
    body = body.strip().removesuffix("\n);")

    return header, body


def split_body_table(body: str) -> typing.List[str]:
    body_split = body.split(",")
    body_split = [line.strip() for line in body_split]

    return body_split


def split_insert(entry: str) -> typing.Tuple[str, str, str]:
    entry_split = entry.split(" ")

    values_index = entry_split.index("VALUES")

    header = " ".join(entry_split[0:3])
    attributes = " ".join(entry_split[3:values_index])
    values = " ".join(entry_split[values_index + 1:])

    return header, attributes, values


def parse_insert_attributes(attributes: str) -> typing.List[str]:
    trimmed_attributes = attributes.lstrip("(").rstrip(")")
    split_attributes = trimmed_attributes.split(",")
    split_attributes = [attribute.strip() for attribute in split_attributes]
    return split_attributes


def parse_insert_values(values: str) -> typing.List[str]:
    trimmed_values = values.lstrip("(").rstrip(");")
    split_values = trimmed_values.split(",")
    split_values = [value.strip() for value in split_values]
    return split_values


def parse_insert_values_sqlparse(statement: sqlparse.sql.Statement):

    for field in statement.tokens:
        if isinstance(field, sqlparse.sql.Values):
            values_field = field
            break
    else:
        print("ERROR LOG : PARSE INSERT VALUES")
        print("\n")
        print(statement.tokens)
        print("\n")
        for field in statement.tokens:
            print(field)
            print("\n")
        raise BruhMoment

    for values_token in values_field:
        if isinstance(values_token, sqlparse.sql.Parenthesis):
            values_generator = values_token._groupable_tokens[0].get_identifiers()
            break

    return [str(token) for token in values_generator]


def parse_insert_values_ast(values: str) -> typing.List[str]:
    trimmed_values = values.rstrip(";")
    trimmed_values = re.sub("NULL", "None", trimmed_values)
    return list(literal_eval(trimmed_values))


def clean_change_parenthesis(entry: str) -> str:
    pat = re.compile(r"'(\"(.+)\":(\w|,)+\s?)*((''([\w/\-\.\+@]+)'')|('''))(:(\w|,)+)\s?('(.*)':[\w,]+\s?)*'")  # noqa: E501
    guard = 0

    while pat.search(entry) and guard < 50:
        entry = pat.sub("'\\1\"\\6\"\\8 \\10'", entry)
        guard += 1

    return entry


def remove_apostrophes_phone_number(entry: str) -> str:
    pat = re.compile(r"'([\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6})'''")

    while pat.search(entry):
        entry = pat.sub("'\\1\"'", entry)

    return entry
