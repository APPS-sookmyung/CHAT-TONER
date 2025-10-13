
-- Step 1: Drop tables, which will cascade to SOME dependencies.
DROP TABLE IF EXISTS public.communication_guidelines CASCADE;
DROP TABLE IF EXISTS public.company_learning_data CASCADE;
DROP TABLE IF EXISTS public.company_profiles CASCADE;
DROP TABLE IF EXISTS public.company_survey_responses CASCADE;
DROP TABLE IF EXISTS public.company_user_feedback CASCADE;
DROP TABLE IF EXISTS public.query_analysis_results CASCADE;
DROP TABLE IF EXISTS public.user_company_preferences CASCADE;
DROP TABLE IF EXISTS public.user_company_relations CASCADE;

-- Step 2: Explicitly drop sequences to clean up any orphans.
DROP SEQUENCE IF EXISTS public.communication_guidelines_id_seq;
DROP SEQUENCE IF EXISTS public.company_learning_data_id_seq;
DROP SEQUENCE IF EXISTS public.company_profiles_id_seq;
DROP SEQUENCE IF EXISTS public.company_survey_responses_id_seq;
DROP SEQUENCE IF EXISTS public.company_user_feedback_id_seq;
DROP SEQUENCE IF EXISTS public.query_analysis_results_id_seq;
DROP SEQUENCE IF EXISTS public.user_company_preferences_id_seq;
DROP SEQUENCE IF EXISTS public.user_company_relations_id_seq;


-- Step 3: Recreate everything from scratch.

--
-- PostgreSQL database dump
--

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: communication_guidelines; Type: TABLE; Schema: public
--

CREATE TABLE public.communication_guidelines (
    id integer NOT NULL,
    company_id character varying(100) NOT NULL,
    document_type character varying(50) NOT NULL,
    document_name character varying(255),
    document_content text NOT NULL,
    processed_chunks jsonb,
    uploaded_by character varying(100),
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    vector_embeddings jsonb,
    chunk_metadata jsonb
);


--
-- Name: communication_guidelines_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.communication_guidelines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: communication_guidelines_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.communication_guidelines_id_seq OWNED BY public.communication_guidelines.id;


--
-- Name: company_learning_data; Type: TABLE; Schema: public
--

CREATE TABLE public.company_learning_data (
    id integer NOT NULL,
    company_id character varying(100) NOT NULL,
    user_id character varying(100),
    input_text text NOT NULL,
    output_text text NOT NULL,
    feedback character varying(10),
    context jsonb,
    embedding jsonb,
    is_approved boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: company_learning_data_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.company_learning_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: company_learning_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.company_learning_data_id_seq OWNED BY public.company_learning_data.id;


--
-- Name: company_profiles; Type: TABLE; Schema: public
--

CREATE TABLE public.company_profiles (
    id integer NOT NULL,
    company_id character varying(100) NOT NULL,
    company_name character varying(255) NOT NULL,
    industry character varying(100),
    team_size integer,
    primary_business text,
    communication_style character varying(50),
    main_channels jsonb,
    target_audience jsonb,
    generated_profile text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: company_profiles_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.company_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: company_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.company_profiles_id_seq OWNED BY public.company_profiles.id;


--
-- Name: company_survey_responses; Type: TABLE; Schema: public
--

CREATE TABLE public.company_survey_responses (
    id integer NOT NULL,
    company_id character varying(100) NOT NULL,
    respondent_name character varying(255),
    respondent_role character varying(100),
    survey_responses jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: company_survey_responses_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.company_survey_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: company_survey_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.company_survey_responses_id_seq OWNED BY public.company_survey_responses.id;


--
-- Name: company_user_feedback; Type: TABLE; Schema: public
--

CREATE TABLE public.company_user_feedback (
    id integer NOT NULL,
    user_id character varying(100) NOT NULL,
    company_id character varying(100) NOT NULL,
    session_id character varying(100),
    original_text text NOT NULL,
    suggested_text text NOT NULL,
    feedback_type character varying(20) NOT NULL,
    feedback_value character varying(10) NOT NULL,
    applied_in_final boolean DEFAULT false,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: company_user_feedback_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.company_user_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: company_user_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.company_user_feedback_id_seq OWNED BY public.company_user_feedback.id;


--
-- Name: query_analysis_results; Type: TABLE; Schema: public
--

CREATE TABLE public.query_analysis_results (
    id integer NOT NULL,
    user_input text NOT NULL,
    analyzed_metadata jsonb,
    company_id character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: query_analysis_results_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.query_analysis_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: query_analysis_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.query_analysis_results_id_seq OWNED BY public.query_analysis_results.id;


--
-- Name: user_company_preferences; Type: TABLE; Schema: public
--

CREATE TABLE public.user_company_preferences (
    id integer NOT NULL,
    user_id character varying(100) NOT NULL,
    company_id character varying(100) NOT NULL,
    personal_style jsonb,
    negative_prompts text,
    preference_weights jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_company_preferences_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.user_company_preferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_company_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.user_company_preferences_id_seq OWNED BY public.user_company_preferences.id;


--
-- Name: user_company_relations; Type: TABLE; Schema: public
--

CREATE TABLE public.user_company_relations (
    id integer NOT NULL,
    user_id character varying(100) NOT NULL,
    company_id character varying(100) NOT NULL,
    role character varying(50) DEFAULT 'employee'::character varying,
    status character varying(20) DEFAULT 'active'::character varying,
    onboarding_completed boolean DEFAULT false,
    joined_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_company_relations_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.user_company_relations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_company_relations_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.user_company_relations_id_seq OWNED BY public.user_company_relations.id;


--
-- Name: communication_guidelines id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.communication_guidelines ALTER COLUMN id SET DEFAULT nextval('public.communication_guidelines_id_seq'::regclass);


--
-- Name: company_learning_data id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.company_learning_data ALTER COLUMN id SET DEFAULT nextval('public.company_learning_data_id_seq'::regclass);


--
-- Name: company_profiles id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.company_profiles ALTER COLUMN id SET DEFAULT nextval('public.company_profiles_id_seq'::regclass);


--
-- Name: company_survey_responses id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.company_survey_responses ALTER COLUMN id SET DEFAULT nextval('public.company_survey_responses_id_seq'::regclass);


--
-- Name: company_user_feedback id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.company_user_feedback ALTER COLUMN id SET DEFAULT nextval('public.company_user_feedback_id_seq'::regclass);


--
-- Name: query_analysis_results id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.query_analysis_results ALTER COLUMN id SET DEFAULT nextval('public.query_analysis_results_id_seq'::regclass);


--
-- Name: user_company_preferences id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.user_company_preferences ALTER COLUMN id SET DEFAULT nextval('public.user_company_preferences_id_seq'::regclass);


--
-- Name: user_company_relations id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.user_company_relations ALTER COLUMN id SET DEFAULT nextval('public.user_company_relations_id_seq'::regclass);


--
-- Name: communication_guidelines communication_guidelines_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.communication_guidelines
    ADD CONSTRAINT communication_guidelines_pkey PRIMARY KEY (id);


--
-- Name: company_learning_data company_learning_data_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.company_learning_data
    ADD CONSTRAINT company_learning_data_pkey PRIMARY KEY (id);


--
-- Name: company_profiles company_profiles_company_id_key; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.company_profiles
    ADD CONSTRAINT company_profiles_company_id_key UNIQUE (company_id);


--
-- Name: company_profiles company_profiles_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.company_profiles
    ADD CONSTRAINT company_profiles_pkey PRIMARY KEY (id);


--
-- Name: company_survey_responses company_survey_responses_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.company_survey_responses
    ADD CONSTRAINT company_survey_responses_pkey PRIMARY KEY (id);


--
-- Name: company_user_feedback company_user_feedback_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.company_user_feedback
    ADD CONSTRAINT company_user_feedback_pkey PRIMARY KEY (id);


--
-- Name: query_analysis_results query_analysis_results_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.query_analysis_results
    ADD CONSTRAINT query_analysis_results_pkey PRIMARY KEY (id);


--
-- Name: user_company_preferences user_company_preferences_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.user_company_preferences
    ADD CONSTRAINT user_company_preferences_pkey PRIMARY KEY (id);


--
-- Name: user_company_preferences user_company_preferences_user_id_company_id_key; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.user_company_preferences
    ADD CONSTRAINT user_company_preferences_user_id_company_id_key UNIQUE (user_id, company_id);


--
-- Name: user_company_relations user_company_relations_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.user_company_relations
    ADD CONSTRAINT user_company_relations_pkey PRIMARY KEY (id);


--
-- Name: user_company_relations user_company_relations_user_id_company_id_key; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.user_company_relations
    ADD CONSTRAINT user_company_relations_user_id_company_id_key UNIQUE (user_id, company_id);


--
-- Name: idx_communication_guidelines_company_id; Type: INDEX; Schema: public
--

CREATE INDEX idx_communication_guidelines_company_id ON public.communication_guidelines USING btree (company_id);


--
-- Name: idx_company_learning_data_company_id; Type: INDEX; Schema: public
--

CREATE INDEX idx_company_learning_data_company_id ON public.company_learning_data USING btree (company_id);


--
-- Name: idx_company_profiles_company_id; Type: INDEX; Schema: public
--

CREATE INDEX idx_company_profiles_company_id ON public.company_profiles USING btree (company_id);


--
-- Name: idx_company_user_feedback_company_id; Type: INDEX; Schema: public
--

CREATE INDEX idx_company_user_feedback_company_id ON public.company_user_feedback USING btree (company_id);


--
-- Name: idx_company_user_feedback_user_id; Type: INDEX; Schema: public
--

CREATE INDEX idx_company_user_feedback_user_id ON public.company_user_feedback USING btree (user_id);


--
-- Name: idx_user_company_preferences_user_company; Type: INDEX; Schema: public
--

CREATE INDEX idx_user_company_preferences_user_company ON public.user_company_preferences USING btree (user_id, company_id);


--
-- Name: idx_user_company_relations_user_company; Type: INDEX; Schema: public
--

CREATE INDEX idx_user_company_relations_user_company ON public.user_company_relations USING btree (user_id, company_id);


--
-- PostgreSQL database dump complete
--
