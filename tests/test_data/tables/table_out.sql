CREATE TABLE sample_type_property_types (
    id INTEGER NOT NULL,
    saty_id INTEGER NOT NULL,
    prty_id INTEGER NOT NULL,
    is_mandatory INTEGER,
    is_managed_internally INTEGER,
    pers_id_registerer INTEGER NOT NULL,
    registration_timestamp TEXT,
    is_displayed INTEGER,
    ordinal INTEGER NOT NULL,
    section TEXT,
    script_id INTEGER,
    is_shown_edit INTEGER,
    show_raw_value INTEGER,
    is_unique INTEGER
);
