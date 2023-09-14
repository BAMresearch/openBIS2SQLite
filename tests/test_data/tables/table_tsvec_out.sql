CREATE TABLE data_set_properties (
    id INTEGER NOT NULL,
    ds_id INTEGER NOT NULL,
    dstpt_id INTEGER NOT NULL,
    value TEXT,
    cvte_id INTEGER,
    mate_prop_id INTEGER,
    samp_prop_id INTEGER,
    pers_id_registerer INTEGER NOT NULL,
    registration_timestamp TEXT,
    pers_id_author INTEGER NOT NULL,
    modification_timestamp TEXT,
    dase_frozen INTEGER,
    tsvector_document TEXT NOT NULL,
    is_unique INTEGER
);
