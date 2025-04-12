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

CREATE TABLE IF NOT EXISTS public.admins (
    id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.admins OWNER TO postgres;

CREATE SEQUENCE IF NOT EXISTS public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admins_id_seq OWNER TO postgres;

ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;

CREATE TABLE IF NOT EXISTS public.bookings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    people_count integer NOT NULL,
    event_theme character varying(255) NOT NULL,
    event_description text,
    status character varying(50) DEFAULT 'pending'::character varying
);


ALTER TABLE public.bookings OWNER TO postgres;

CREATE SEQUENCE IF NOT EXISTS public.bookings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bookings_id_seq OWNER TO postgres;

ALTER SEQUENCE public.bookings_id_seq OWNED BY public.bookings.id;

ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);

ALTER TABLE ONLY public.bookings ALTER COLUMN id SET DEFAULT nextval('public.bookings_id_seq'::regclass);

COPY public.admins (id, user_id) FROM stdin;
1	123456
\.

COPY public.bookings (id, user_id, start_date, end_date, people_count, event_theme, event_description, status) FROM stdin;
1	111111	2025-04-10	2025-04-12	80	Конференция по IT	Ежегодная конференция разработчиков	approved
2	222222	2025-04-15	2025-04-17	150	Мастер-класс	Мастер-класс по программированию	pending
3	333333	2025-04-20	2025-04-22	200	Выставка	Выставка технологических новинок	approved
\.

SELECT pg_catalog.setval('public.admins_id_seq', 1, true);

SELECT pg_catalog.setval('public.bookings_id_seq', 3, true);

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_user_id_key UNIQUE (user_id);

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);

CREATE INDEX IF NOT EXISTS idx_admins_user_id ON public.admins USING btree (user_id);

CREATE INDEX IF NOT EXISTS idx_bookings_dates ON public.bookings USING btree (start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_bookings_status ON public.bookings USING btree (status);

CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON public.bookings USING btree (user_id);