import pytest
from src.classes import DumpTable, DumpInsert
from enum import Enum
from pathlib import Path
from pgdumplib.dump import Entry

TABLE_PATH = Path(Path(__file__).parent.absolute(), "test_data", "tables")
INSERT_PATH = Path(Path(__file__).parent.absolute(), "test_data", "inserts")


class Filepaths(Enum):
    TABLE = (Path(TABLE_PATH, "table.sql"), Path(TABLE_PATH, "table_out.sql"))
    TABLE_TSVEC = (Path(TABLE_PATH, "table_tsvec.sql"), Path(TABLE_PATH, "table_tsvec_out.sql"))
    INSERT = (Path(INSERT_PATH, "insert.sql"), Path(INSERT_PATH, "insert_out.sql"))
    INSERT_TSVEC = (Path(INSERT_PATH, "insert_tsvec.sql"), Path(INSERT_PATH, "insert_tsvec_out.sql"))
    INSERT_PHONE = (Path(INSERT_PATH, "insert_phone.sql"), Path(INSERT_PATH, "insert_phone_out.sql"))


class DumpIDs(Enum):
    TABLE = 0
    TABLE_TSVEC = 1


class DumpTag(Enum):
    TABLE = "sample_type_property_types"
    TABLE_TSVEC = "data_set_properties"


@pytest.fixture
def pgdumplib_table_entry(request):
    with open(Filepaths[request.param].value[0], "r") as file:
        raw_sql_input = file.read()

    return Entry(
        DumpIDs[request.param].value,  # dump_id
        False,  # had_dumper
        '',  # table_old
        '',  # oid
        DumpTag[request.param].value,  # tag
        'TABLE',  # desc
        raw_sql_input,  # defn
        '',  # drop_stmt
        '',  # copy_stmt
        '',  # namespace
        '',  # tablespace
        '',  # tableam
        '',  # owner
        False,  # with_oids
        []  # dependencies
    )


@pytest.fixture
def pgdumplib_table_tsvec_entry():
    with open(Filepaths.TABLE_TSVEC.value[0], "r") as file:
        raw_sql_input = file.read()

    return Entry(
        DumpIDs.TABLE.value,  # dump_id
        False,  # had_dumper
        '',  # table_old
        '',  # oid
        'data_set_properties',  # tag
        'TABLE',  # desc
        raw_sql_input,  # defn
        '',  # drop_stmt
        '',  # copy_stmt
        '',  # namespace
        '',  # tablespace
        '',  # tableam
        '',  # owner
        False,  # with_oids
        []  # dependencies
    )


@pytest.fixture
def pgdumplib_domain_mappings():
    return {
        'archiving_status': 'TEXT',
        'authorization_role': 'TEXT',
        'boolean_char': 'INTEGER',
        'boolean_char_or_unknown': 'TEXT',
        'code': 'TEXT',
        'column_label': 'TEXT',
        'data_set_kind': 'TEXT',
        'data_store_service_kind': 'TEXT',
        'data_store_service_reporting_plugin_type': 'TEXT',
        'description_2000': 'TEXT',
        'edms_address_type': 'TEXT',
        'entity_kind': 'TEXT',
        'event_type': 'TEXT',
        'file': 'TEXT',
        'file_name': 'TEXT',
        'grid_expression': 'TEXT',
        'grid_id': 'TEXT',
        'identifier': 'TEXT',
        'location_type': 'TEXT',
        'object_name': 'TEXT',
        'operation_execution_availability': 'TEXT',
        'operation_execution_state': 'TEXT',
        'ordinal_int': 'INTEGER',
        'plugin_type': 'TEXT',
        'query_type': 'TEXT',
        'real_value': 'REAL',
        'sample_identifier': 'TEXT',
        'script_type': 'TEXT',
        'tech_id': 'INTEGER',
        'text_value': 'TEXT',
        'time_stamp': 'TEXT',
        'time_stamp_dfl': 'TEXT',
        'title_100': 'TEXT',
        'user_id': 'TEXT',
        'integer': 'INTEGER',
        'character': 'TEXT',
        'real': 'REAL',
        'boolean': 'INTEGER',
        'bigint': 'INTEGER',
        'smallint': 'INTEGER'
    }


@pytest.mark.parametrize(
    ("pgdumplib_table_entry", "curr_param"),
    [("TABLE", "TABLE"), ("TABLE_TSVEC", "TABLE_TSVEC")],
    indirect=["pgdumplib_table_entry"]
)
def test_reading_table(pgdumplib_table_entry, curr_param, pgdumplib_domain_mappings):

    with open(Filepaths[curr_param].value[1], "r") as outfile:
        output_sql = str(outfile.read())

    table = DumpTable(pgdumplib_table_entry)
    table.apply_mappings(pgdumplib_domain_mappings)

    assert output_sql == str(table)


@pytest.mark.parametrize(
    "insert", ["INSERT", "INSERT_TSVEC", "INSERT_PHONE"]
)
def test_reading_insert(insert):

    with open(Filepaths[insert].value[0]) as infile, open(Filepaths[insert].value[1], "r") as outfile:
        input_sql = str(infile.read()).removesuffix("\n").strip()
        output_sql = str(outfile.read())

    insert = DumpInsert(input_sql)

    assert output_sql == str(insert)
