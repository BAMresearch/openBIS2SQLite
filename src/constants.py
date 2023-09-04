from enum import Enum, auto
from pathlib import Path

PATH_TO_DUMP = Path(Path().cwd().parent.parent, "backups", "dump_att_inserts.sql")

PATH_TO_OUTPUT = Path(Path().cwd().parent, "sqlite_dump.sql")

PATH_TO_TESTING = Path(Path().cwd(), "testing.sql")


class EntryType(Enum):
    DOMAIN = auto()
    TABLE = auto()
    INSERT = auto()
    OTHER = auto()


class BruhMoment(Exception):
    pass


class NewlineInEntryError(Exception):
    pass


CONVERTING_RULES = {
    "text": "TEXT",
    "real": "REAL",
    "integer": "INTEGER",
    "bigint": "INTEGER",
    "boolean": "INTEGER",
}

IGNORED_TABLES = [
    "core_plugins",
    "events",
    "external_data",
    "data_store_services",
    "data_stores",
    "events_search",
    "scripts",
]

WHITELISTED_TABLES = [
    "data_set_properties",
    "data_set_type_property_types",
    "data_set_types",
    "data_all",
    "data_types",
    "experiment_properties",
    "experiment_type_property_types",
    "experiment_types",
    "experiments_all",
    "projects",
    "property_types",
    "sample_properties",
    "sample_relationships_all",
    "sample_type_property_types",
    "sample_types",
    "samples_all",
    "spaces"
]

all = """

attachment_contents
attachments
authorization_group_persons
authorization_groups
content_copies
controlled_vocabularies
controlled_vocabulary_terms
core_plugins
data_all
data_set_copies_history
data_set_properties_history
data_set_relationships_history
data_set_properties
data_set_relationships_all
data_set_type_property_types
data_set_types
data_store_service_data_set_types
data_store_services
data_stores
data_types
database_version_logs
deletions
entity_operations_log
events
events_search
experiment_properties_history
experiment_relationships_history
experiment_properties
experiment_type_property_types
experiment_types
experiments_all
external_data
external_data_management_systems
file_format_types
filters
grid_custom_columns
link_data
locator_types
material_properties
material_properties_history
material_type_property_types
material_types
materials
metaproject_assignments_all
metaprojects
operation_executions
persons
post_registration_dataset_queue
project_relationships_history
projects
property_types
queries
relationship_types
role_assignments
sample_properties_history
sample_relationships_history
sample_properties
sample_relationships_all
sample_type_property_types
sample_types
samples_all
scripts
semantic_annotations
spaces

"""
