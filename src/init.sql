SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.admins (
    id integer NOT NULL,
    user_id bigint NOT NULL
);


ALTER TABLE public.admins OWNER TO postgres;

CREATE SEQUENCE public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admins_id_seq OWNER TO postgres;

ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;

CREATE TABLE public.bookings (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    people_count integer NOT NULL,
    people_count_overall integer,
    theme text NOT NULL,
    description text,
    status character varying(50) DEFAULT 'pending'::character varying,
    target_audience text,
    name text,
    registration character varying(10),
    logistics character varying(35),
    type text,
    place text,
    participants_accomodation text,
    experts_count integer,
    curator_fio text,
    curator_position text,
    curator_contact text,
    other_info text
);


ALTER TABLE public.bookings OWNER TO postgres;

CREATE SEQUENCE public.bookings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bookings_id_seq OWNER TO postgres;

ALTER SEQUENCE public.bookings_id_seq OWNED BY public.bookings.id;

CREATE TABLE public.comments (
    id bigint NOT NULL,
    comment text NOT NULL,
    booking_id bigint NOT NULL
);


ALTER TABLE public.comments OWNER TO postgres;

CREATE SEQUENCE public.comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.comments_id_seq OWNER TO postgres;

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;

ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);

ALTER TABLE ONLY public.bookings ALTER COLUMN id SET DEFAULT nextval('public.bookings_id_seq'::regclass);

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);

COPY public.admins (id, user_id) FROM stdin;
1	458920125
2	204980681
3   5994251528
\.

COPY public.comments (id, comment, booking_id) FROM stdin;
\.

SELECT pg_catalog.setval('public.admins_id_seq', 2, true);

SELECT pg_catalog.setval('public.bookings_id_seq', 3, true);

SELECT pg_catalog.setval('public.comments_id_seq', 1, false);

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_user_id_key UNIQUE (user_id);

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);

CREATE INDEX idx_admins_user_id ON public.admins USING btree (user_id);

CREATE INDEX idx_bookings_dates ON public.bookings USING btree (start_date, end_date);

CREATE INDEX idx_bookings_status ON public.bookings USING btree (status);

CREATE INDEX idx_bookings_user_id ON public.bookings USING btree (user_id);

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_booking_fk FOREIGN KEY (booking_id) REFERENCES public.bookings(id) NOT VALID;
