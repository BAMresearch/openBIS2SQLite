CREATE TABLE public.sample_type_property_types (
    id public.tech_id NOT NULL,
    saty_id public.tech_id NOT NULL,
    prty_id public.tech_id NOT NULL,
    is_mandatory public.boolean_char DEFAULT false NOT NULL,
    is_managed_internally public.boolean_char DEFAULT false NOT NULL,
    pers_id_registerer public.tech_id NOT NULL,
    registration_timestamp public.time_stamp_dfl DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_displayed public.boolean_char DEFAULT true NOT NULL,
    ordinal public.ordinal_int NOT NULL,
    section public.description_2000,
    script_id public.tech_id,
    is_shown_edit public.boolean_char DEFAULT true NOT NULL,
    show_raw_value public.boolean_char DEFAULT false NOT NULL,
    is_unique public.boolean_char DEFAULT false NOT NULL
);
