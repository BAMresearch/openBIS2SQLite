import re


def clean_block(block: str) -> str:
    cleaned = [clean_line(line) for line in block]
    for line in cleaned:
        print(line)


def clean_line(line: str) -> str:
    line = re.sub("public.", "", line)
    line = re.sub("true", "\"t\"", line)
    line = re.sub("false", "\"f\"", line)
    return line
