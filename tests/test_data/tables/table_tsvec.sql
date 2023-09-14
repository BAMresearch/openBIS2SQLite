CREATE TABLE public.data_set_properties (
    id public.tech_id NOT NULL,
    ds_id public.tech_id NOT NULL,
    dstpt_id public.tech_id NOT NULL,
    value public.text_value,
    cvte_id public.tech_id,
    mate_prop_id public.tech_id,
    samp_prop_id public.tech_id,
    pers_id_registerer public.tech_id NOT NULL,
    registration_timestamp public.time_stamp_dfl DEFAULT CURRENT_TIMESTAMP NOT NULL,
    pers_id_author public.tech_id NOT NULL,
    modification_timestamp public.time_stamp DEFAULT CURRENT_TIMESTAMP,
    dase_frozen public.boolean_char DEFAULT false NOT NULL,
    tsvector_document tsvector NOT NULL,
    is_unique public.boolean_char DEFAULT false NOT NULL,
    CONSTRAINT dspr_ck CHECK ((((value IS NOT NULL) AND (cvte_id IS NULL) AND (mate_prop_id IS NULL) AND (samp_prop_id IS NULL)) OR ((value IS NULL) AND (cvte_id IS NOT NULL) AND (mate_prop_id IS NULL) AND (samp_prop_id IS NULL)) OR ((value IS NULL) AND (cvte_id IS NULL) AND (mate_prop_id IS NOT NULL) AND (samp_prop_id IS NULL)) OR ((value IS NULL) AND (cvte_id IS NULL) AND (mate_prop_id IS NULL) AND (samp_prop_id IS NOT NULL))))
);
