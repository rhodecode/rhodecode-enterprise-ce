--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: cache_invalidation; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE cache_invalidation (
    cache_id integer NOT NULL,
    cache_key character varying(255),
    cache_args character varying(255),
    cache_active boolean
);


ALTER TABLE public.cache_invalidation OWNER TO postgres;

--
-- Name: cache_invalidation_cache_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE cache_invalidation_cache_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cache_invalidation_cache_id_seq OWNER TO postgres;

--
-- Name: cache_invalidation_cache_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE cache_invalidation_cache_id_seq OWNED BY cache_invalidation.cache_id;


--
-- Name: changeset_comments; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE changeset_comments (
    comment_id integer NOT NULL,
    repo_id integer NOT NULL,
    revision character varying(40),
    pull_request_id integer,
    line_no character varying(10),
    hl_lines character varying(512),
    f_path character varying(1000),
    user_id integer NOT NULL,
    text text NOT NULL,
    created_on timestamp without time zone NOT NULL,
    modified_at timestamp without time zone NOT NULL
);


ALTER TABLE public.changeset_comments OWNER TO postgres;

--
-- Name: changeset_comments_comment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE changeset_comments_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.changeset_comments_comment_id_seq OWNER TO postgres;

--
-- Name: changeset_comments_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE changeset_comments_comment_id_seq OWNED BY changeset_comments.comment_id;


--
-- Name: changeset_statuses; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE changeset_statuses (
    changeset_status_id integer NOT NULL,
    repo_id integer NOT NULL,
    user_id integer NOT NULL,
    revision character varying(40) NOT NULL,
    status character varying(128) NOT NULL,
    changeset_comment_id integer,
    modified_at timestamp without time zone NOT NULL,
    version integer NOT NULL,
    pull_request_id integer
);


ALTER TABLE public.changeset_statuses OWNER TO postgres;

--
-- Name: changeset_statuses_changeset_status_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE changeset_statuses_changeset_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.changeset_statuses_changeset_status_id_seq OWNER TO postgres;

--
-- Name: changeset_statuses_changeset_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE changeset_statuses_changeset_status_id_seq OWNED BY changeset_statuses.changeset_status_id;


--
-- Name: db_migrate_version; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE db_migrate_version (
    repository_id character varying(250) NOT NULL,
    repository_path text,
    version integer
);


ALTER TABLE public.db_migrate_version OWNER TO postgres;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE groups (
    group_id integer NOT NULL,
    group_name character varying(255) NOT NULL,
    group_parent_id integer,
    group_description character varying(10000),
    enable_locking boolean NOT NULL,
    CONSTRAINT groups_check CHECK ((group_id <> group_parent_id))
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- Name: groups_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE groups_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.groups_group_id_seq OWNER TO postgres;

--
-- Name: groups_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE groups_group_id_seq OWNED BY groups.group_id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE notifications (
    notification_id integer NOT NULL,
    subject character varying(512),
    body text,
    created_by integer,
    created_on timestamp without time zone NOT NULL,
    type character varying(256)
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE notifications_notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notifications_notification_id_seq OWNER TO postgres;

--
-- Name: notifications_notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE notifications_notification_id_seq OWNED BY notifications.notification_id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE permissions (
    permission_id integer NOT NULL,
    permission_name character varying(255),
    permission_longname character varying(255)
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE permissions_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.permissions_permission_id_seq OWNER TO postgres;

--
-- Name: permissions_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE permissions_permission_id_seq OWNED BY permissions.permission_id;


--
-- Name: pull_request_reviewers; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pull_request_reviewers (
    pull_requests_reviewers_id integer NOT NULL,
    pull_request_id integer NOT NULL,
    user_id integer
);


ALTER TABLE public.pull_request_reviewers OWNER TO postgres;

--
-- Name: pull_request_reviewers_pull_requests_reviewers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE pull_request_reviewers_pull_requests_reviewers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pull_request_reviewers_pull_requests_reviewers_id_seq OWNER TO postgres;

--
-- Name: pull_request_reviewers_pull_requests_reviewers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE pull_request_reviewers_pull_requests_reviewers_id_seq OWNED BY pull_request_reviewers.pull_requests_reviewers_id;


--
-- Name: pull_requests; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pull_requests (
    pull_request_id integer NOT NULL,
    title character varying(256),
    description text,
    status character varying(256) NOT NULL,
    created_on timestamp without time zone NOT NULL,
    updated_on timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    revisions text,
    org_repo_id integer NOT NULL,
    org_ref character varying(256) NOT NULL,
    other_repo_id integer NOT NULL,
    other_ref character varying(256) NOT NULL
);


ALTER TABLE public.pull_requests OWNER TO postgres;

--
-- Name: pull_requests_pull_request_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE pull_requests_pull_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pull_requests_pull_request_id_seq OWNER TO postgres;

--
-- Name: pull_requests_pull_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE pull_requests_pull_request_id_seq OWNED BY pull_requests.pull_request_id;


--
-- Name: repo_to_perm; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE repo_to_perm (
    repo_to_perm_id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL,
    repository_id integer NOT NULL
);


ALTER TABLE public.repo_to_perm OWNER TO postgres;

--
-- Name: repo_to_perm_repo_to_perm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE repo_to_perm_repo_to_perm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_to_perm_repo_to_perm_id_seq OWNER TO postgres;

--
-- Name: repo_to_perm_repo_to_perm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE repo_to_perm_repo_to_perm_id_seq OWNED BY repo_to_perm.repo_to_perm_id;


--
-- Name: repositories; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE repositories (
    repo_id integer NOT NULL,
    repo_name character varying(255) NOT NULL,
    clone_uri character varying(255),
    repo_type character varying(255) NOT NULL,
    user_id integer NOT NULL,
    private boolean,
    statistics boolean,
    downloads boolean,
    description character varying(10000),
    created_on timestamp without time zone,
    updated_on timestamp without time zone,
    landing_revision character varying(255) NOT NULL,
    enable_locking boolean NOT NULL,
    locked character varying(255),
    changeset_cache bytea,
    fork_id integer,
    group_id integer
);


ALTER TABLE public.repositories OWNER TO postgres;

--
-- Name: repositories_fields; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE repositories_fields (
    repo_field_id integer NOT NULL,
    repository_id integer NOT NULL,
    field_key character varying(250),
    field_label character varying(1024) NOT NULL,
    field_value character varying(10000) NOT NULL,
    field_desc character varying(1024) NOT NULL,
    field_type character varying(256) NOT NULL,
    created_on timestamp without time zone NOT NULL
);


ALTER TABLE public.repositories_fields OWNER TO postgres;

--
-- Name: repositories_fields_repo_field_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE repositories_fields_repo_field_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repositories_fields_repo_field_id_seq OWNER TO postgres;

--
-- Name: repositories_fields_repo_field_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE repositories_fields_repo_field_id_seq OWNED BY repositories_fields.repo_field_id;


--
-- Name: repositories_repo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE repositories_repo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repositories_repo_id_seq OWNER TO postgres;

--
-- Name: repositories_repo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE repositories_repo_id_seq OWNED BY repositories.repo_id;


--
-- Name: rhodecode_settings; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE rhodecode_settings (
    app_settings_id integer NOT NULL,
    app_settings_name character varying(255),
    app_settings_value character varying(255)
);


ALTER TABLE public.rhodecode_settings OWNER TO postgres;

--
-- Name: rhodecode_settings_app_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE rhodecode_settings_app_settings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rhodecode_settings_app_settings_id_seq OWNER TO postgres;

--
-- Name: rhodecode_settings_app_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE rhodecode_settings_app_settings_id_seq OWNED BY rhodecode_settings.app_settings_id;


--
-- Name: rhodecode_ui; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE rhodecode_ui (
    ui_id integer NOT NULL,
    ui_section character varying(255),
    ui_key character varying(255),
    ui_value character varying(255),
    ui_active boolean
);


ALTER TABLE public.rhodecode_ui OWNER TO postgres;

--
-- Name: rhodecode_ui_ui_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE rhodecode_ui_ui_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rhodecode_ui_ui_id_seq OWNER TO postgres;

--
-- Name: rhodecode_ui_ui_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE rhodecode_ui_ui_id_seq OWNED BY rhodecode_ui.ui_id;


--
-- Name: statistics; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE statistics (
    stat_id integer NOT NULL,
    repository_id integer NOT NULL,
    stat_on_revision integer NOT NULL,
    commit_activity bytea NOT NULL,
    commit_activity_combined bytea NOT NULL,
    languages bytea NOT NULL
);


ALTER TABLE public.statistics OWNER TO postgres;

--
-- Name: statistics_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE statistics_stat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.statistics_stat_id_seq OWNER TO postgres;

--
-- Name: statistics_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE statistics_stat_id_seq OWNED BY statistics.stat_id;


--
-- Name: user_email_map; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_email_map (
    email_id integer NOT NULL,
    user_id integer,
    email character varying(255)
);


ALTER TABLE public.user_email_map OWNER TO postgres;

--
-- Name: user_email_map_email_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_email_map_email_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_email_map_email_id_seq OWNER TO postgres;

--
-- Name: user_email_map_email_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_email_map_email_id_seq OWNED BY user_email_map.email_id;


--
-- Name: user_followings; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_followings (
    user_following_id integer NOT NULL,
    user_id integer NOT NULL,
    follows_repository_id integer,
    follows_user_id integer,
    follows_from timestamp without time zone
);


ALTER TABLE public.user_followings OWNER TO postgres;

--
-- Name: user_followings_user_following_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_followings_user_following_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_followings_user_following_id_seq OWNER TO postgres;

--
-- Name: user_followings_user_following_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_followings_user_following_id_seq OWNED BY user_followings.user_following_id;


--
-- Name: user_ip_map; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_ip_map (
    ip_id integer NOT NULL,
    user_id integer,
    ip_addr character varying(255),
    active boolean
);


ALTER TABLE public.user_ip_map OWNER TO postgres;

--
-- Name: user_ip_map_ip_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_ip_map_ip_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_ip_map_ip_id_seq OWNER TO postgres;

--
-- Name: user_ip_map_ip_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_ip_map_ip_id_seq OWNED BY user_ip_map.ip_id;


--
-- Name: user_logs; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_logs (
    user_log_id integer NOT NULL,
    user_id integer,
    username character varying(255),
    repository_id integer,
    repository_name character varying(255),
    user_ip character varying(255),
    action text,
    action_date timestamp without time zone
);


ALTER TABLE public.user_logs OWNER TO postgres;

--
-- Name: user_logs_user_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_logs_user_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_logs_user_log_id_seq OWNER TO postgres;

--
-- Name: user_logs_user_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_logs_user_log_id_seq OWNED BY user_logs.user_log_id;


--
-- Name: user_repo_group_to_perm; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_repo_group_to_perm (
    group_to_perm_id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.user_repo_group_to_perm OWNER TO postgres;

--
-- Name: user_repo_group_to_perm_group_to_perm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_repo_group_to_perm_group_to_perm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_repo_group_to_perm_group_to_perm_id_seq OWNER TO postgres;

--
-- Name: user_repo_group_to_perm_group_to_perm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_repo_group_to_perm_group_to_perm_id_seq OWNED BY user_repo_group_to_perm.group_to_perm_id;


--
-- Name: user_to_notification; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_to_notification (
    user_id integer NOT NULL,
    notification_id integer NOT NULL,
    read boolean,
    sent_on timestamp without time zone
);


ALTER TABLE public.user_to_notification OWNER TO postgres;

--
-- Name: user_to_perm; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_to_perm (
    user_to_perm_id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.user_to_perm OWNER TO postgres;

--
-- Name: user_to_perm_user_to_perm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_to_perm_user_to_perm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_to_perm_user_to_perm_id_seq OWNER TO postgres;

--
-- Name: user_to_perm_user_to_perm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_to_perm_user_to_perm_id_seq OWNED BY user_to_perm.user_to_perm_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE users (
    user_id integer NOT NULL,
    username character varying(255),
    password character varying(255),
    active boolean,
    admin boolean,
    firstname character varying(255),
    lastname character varying(255),
    email character varying(255),
    last_login timestamp without time zone,
    ldap_dn character varying(255),
    api_key character varying(255),
    inherit_default_permissions boolean NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_group_repo_group_to_perm; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE users_group_repo_group_to_perm (
    users_group_repo_group_to_perm_id integer NOT NULL,
    users_group_id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.users_group_repo_group_to_perm OWNER TO postgres;

--
-- Name: users_group_repo_group_to_per_users_group_repo_group_to_per_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_group_repo_group_to_per_users_group_repo_group_to_per_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_group_repo_group_to_per_users_group_repo_group_to_per_seq OWNER TO postgres;

--
-- Name: users_group_repo_group_to_per_users_group_repo_group_to_per_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_group_repo_group_to_per_users_group_repo_group_to_per_seq OWNED BY users_group_repo_group_to_perm.users_group_repo_group_to_perm_id;


--
-- Name: users_group_repo_to_perm; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE users_group_repo_to_perm (
    users_group_to_perm_id integer NOT NULL,
    users_group_id integer NOT NULL,
    permission_id integer NOT NULL,
    repository_id integer NOT NULL
);


ALTER TABLE public.users_group_repo_to_perm OWNER TO postgres;

--
-- Name: users_group_repo_to_perm_users_group_to_perm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_group_repo_to_perm_users_group_to_perm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_group_repo_to_perm_users_group_to_perm_id_seq OWNER TO postgres;

--
-- Name: users_group_repo_to_perm_users_group_to_perm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_group_repo_to_perm_users_group_to_perm_id_seq OWNED BY users_group_repo_to_perm.users_group_to_perm_id;


--
-- Name: users_group_to_perm; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE users_group_to_perm (
    users_group_to_perm_id integer NOT NULL,
    users_group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.users_group_to_perm OWNER TO postgres;

--
-- Name: users_group_to_perm_users_group_to_perm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_group_to_perm_users_group_to_perm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_group_to_perm_users_group_to_perm_id_seq OWNER TO postgres;

--
-- Name: users_group_to_perm_users_group_to_perm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_group_to_perm_users_group_to_perm_id_seq OWNED BY users_group_to_perm.users_group_to_perm_id;


--
-- Name: users_groups; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE users_groups (
    users_group_id integer NOT NULL,
    users_group_name character varying(255) NOT NULL,
    users_group_active boolean,
    users_group_inherit_default_permissions boolean NOT NULL
);


ALTER TABLE public.users_groups OWNER TO postgres;

--
-- Name: users_groups_members; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE users_groups_members (
    users_group_member_id integer NOT NULL,
    users_group_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.users_groups_members OWNER TO postgres;

--
-- Name: users_groups_members_users_group_member_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_groups_members_users_group_member_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_groups_members_users_group_member_id_seq OWNER TO postgres;

--
-- Name: users_groups_members_users_group_member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_groups_members_users_group_member_id_seq OWNED BY users_groups_members.users_group_member_id;


--
-- Name: users_groups_users_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_groups_users_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_groups_users_group_id_seq OWNER TO postgres;

--
-- Name: users_groups_users_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_groups_users_group_id_seq OWNED BY users_groups.users_group_id;


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE users_user_id_seq OWNED BY users.user_id;


--
-- Name: cache_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cache_invalidation ALTER COLUMN cache_id SET DEFAULT nextval('cache_invalidation_cache_id_seq'::regclass);


--
-- Name: comment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_comments ALTER COLUMN comment_id SET DEFAULT nextval('changeset_comments_comment_id_seq'::regclass);


--
-- Name: changeset_status_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_statuses ALTER COLUMN changeset_status_id SET DEFAULT nextval('changeset_statuses_changeset_status_id_seq'::regclass);


--
-- Name: group_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY groups ALTER COLUMN group_id SET DEFAULT nextval('groups_group_id_seq'::regclass);


--
-- Name: notification_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY notifications ALTER COLUMN notification_id SET DEFAULT nextval('notifications_notification_id_seq'::regclass);


--
-- Name: permission_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY permissions ALTER COLUMN permission_id SET DEFAULT nextval('permissions_permission_id_seq'::regclass);


--
-- Name: pull_requests_reviewers_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pull_request_reviewers ALTER COLUMN pull_requests_reviewers_id SET DEFAULT nextval('pull_request_reviewers_pull_requests_reviewers_id_seq'::regclass);


--
-- Name: pull_request_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pull_requests ALTER COLUMN pull_request_id SET DEFAULT nextval('pull_requests_pull_request_id_seq'::regclass);


--
-- Name: repo_to_perm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repo_to_perm ALTER COLUMN repo_to_perm_id SET DEFAULT nextval('repo_to_perm_repo_to_perm_id_seq'::regclass);


--
-- Name: repo_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repositories ALTER COLUMN repo_id SET DEFAULT nextval('repositories_repo_id_seq'::regclass);


--
-- Name: repo_field_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repositories_fields ALTER COLUMN repo_field_id SET DEFAULT nextval('repositories_fields_repo_field_id_seq'::regclass);


--
-- Name: app_settings_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY rhodecode_settings ALTER COLUMN app_settings_id SET DEFAULT nextval('rhodecode_settings_app_settings_id_seq'::regclass);


--
-- Name: ui_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY rhodecode_ui ALTER COLUMN ui_id SET DEFAULT nextval('rhodecode_ui_ui_id_seq'::regclass);


--
-- Name: stat_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY statistics ALTER COLUMN stat_id SET DEFAULT nextval('statistics_stat_id_seq'::regclass);


--
-- Name: email_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_email_map ALTER COLUMN email_id SET DEFAULT nextval('user_email_map_email_id_seq'::regclass);


--
-- Name: user_following_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_followings ALTER COLUMN user_following_id SET DEFAULT nextval('user_followings_user_following_id_seq'::regclass);


--
-- Name: ip_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_ip_map ALTER COLUMN ip_id SET DEFAULT nextval('user_ip_map_ip_id_seq'::regclass);


--
-- Name: user_log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_logs ALTER COLUMN user_log_id SET DEFAULT nextval('user_logs_user_log_id_seq'::regclass);


--
-- Name: group_to_perm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_repo_group_to_perm ALTER COLUMN group_to_perm_id SET DEFAULT nextval('user_repo_group_to_perm_group_to_perm_id_seq'::regclass);


--
-- Name: user_to_perm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_to_perm ALTER COLUMN user_to_perm_id SET DEFAULT nextval('user_to_perm_user_to_perm_id_seq'::regclass);


--
-- Name: user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users ALTER COLUMN user_id SET DEFAULT nextval('users_user_id_seq'::regclass);


--
-- Name: users_group_repo_group_to_perm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_repo_group_to_perm ALTER COLUMN users_group_repo_group_to_perm_id SET DEFAULT nextval('users_group_repo_group_to_per_users_group_repo_group_to_per_seq'::regclass);


--
-- Name: users_group_to_perm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_repo_to_perm ALTER COLUMN users_group_to_perm_id SET DEFAULT nextval('users_group_repo_to_perm_users_group_to_perm_id_seq'::regclass);


--
-- Name: users_group_to_perm_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_to_perm ALTER COLUMN users_group_to_perm_id SET DEFAULT nextval('users_group_to_perm_users_group_to_perm_id_seq'::regclass);


--
-- Name: users_group_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_groups ALTER COLUMN users_group_id SET DEFAULT nextval('users_groups_users_group_id_seq'::regclass);


--
-- Name: users_group_member_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_groups_members ALTER COLUMN users_group_member_id SET DEFAULT nextval('users_groups_members_users_group_member_id_seq'::regclass);


--
-- Data for Name: cache_invalidation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY cache_invalidation (cache_id, cache_key, cache_args, cache_active) FROM stdin;
1	1RC/mygr/lol	RC/mygr/lol	f
2	1RC/fakeclone	RC/fakeclone	t
3	1RC/muay	RC/muay	f
4	1BIG/git	BIG/git	t
5	1RC/origin-fork	RC/origin-fork	f
6	1one	one	f
7	1rhodecode.bak.1	rhodecode.bak.1	f
8	1csa-collins	csa-collins	t
9	1csa-harmony	csa-harmony	t
10	1RC/ąqweqwe	RC/ąqweqwe	f
11	1rhodecode	rhodecode	f
12	1csa-unity	csa-unity	t
13	1RC/łęcina	RC/łęcina	f
14	1waitress	waitress	t
15	1RC/rc2/test2	RC/rc2/test2	t
16	1RC/origin-fork-fork	RC/origin-fork-fork	f
17	1RC/rc2/test4	RC/rc2/test4	t
18	1RC/vcs-git	RC/vcs-git	t
19	1rhodecode-extensions	rhodecode-extensions	f
20	1rhodecode-cli-gist	rhodecode-cli-gist	f
21	1test.onaut.com	test.onaut.com	t
22	1RC/new	RC/new	f
23	1csa-aldrin	csa-aldrin	t
24	1vcs	vcs	f
25	1csa-prometheus	csa-prometheus	t
26	1RC/INRC/trololo	RC/INRC/trololo	f
27	1RC/empty-git	RC/empty-git	t
28	1csa-salt-states	csa-salt-states	t
29	1rhodecode-premium	rhodecode-premium	f
30	1RC/qweqwe-fork	RC/qweqwe-fork	f
31	1testrepo-quick	testrepo-quick	t
32	1RC/test	RC/test	f
33	1remote-salt	remote-salt	t
34	1BIG/android	BIG/android	t
35	1DOCS	DOCS	t
36	1rhodecode-git	rhodecode-git	t
37	1RC/bin-ops	RC/bin-ops	f
38	1RC/INRC/L2_NEW/lalalal	RC/INRC/L2_NEW/lalalal	f
39	1RC/fork-remote	RC/fork-remote	f
40	1RC/INRC/L2_NEW/L3/repo_test_move	RC/INRC/L2_NEW/L3/repo_test_move	f
41	1RC/gogo-fork	RC/gogo-fork	f
42	1quest	quest	f
43	1RC/foobar	RC/foobar	f
44	1csa-hyperion	csa-hyperion	t
45	1RC/git-pull-test	RC/git-pull-test	t
46	1RC/qweqwe-fork2	RC/qweqwe-fork2	f
47	1RC/jap	RC/jap	t
48	1RC/hg-repo	RC/hg-repo	f
49	1RC/origin	RC/origin	f
50	1rhodecode-cli-api	rhodecode-cli-api	f
51	1RC/rc2/test3	RC/rc2/test3	t
52	1csa-armstrong	csa-armstrong	t
53	1RC/trololo	RC/trololo	f
54	1testrepo-wp	testrepo-wp	t
55	1pyramidpypi	pyramidpypi	t
56	1salt	salt	t
57	1RC/lol/haha	RC/lol/haha	f
58	1csa-io	csa-io	t
59	1enc-envelope	enc-envelope	f
60	1RC/gogo2	RC/gogo2	f
61	1csa-libcloud	csa-libcloud	t
62	1RC/git-test	RC/git-test	t
63	1RC/rc2/test	RC/rc2/test	f
64	1rhodecode.bak	rhodecode.bak	f
65	1RC/kiall-nova	RC/kiall-nova	t
\.


--
-- Name: cache_invalidation_cache_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('cache_invalidation_cache_id_seq', 65, true);


--
-- Data for Name: changeset_comments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY changeset_comments (comment_id, repo_id, revision, pull_request_id, line_no, hl_lines, f_path, user_id, text, created_on, modified_at) FROM stdin;
\.


--
-- Name: changeset_comments_comment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('changeset_comments_comment_id_seq', 1, false);


--
-- Data for Name: changeset_statuses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY changeset_statuses (changeset_status_id, repo_id, user_id, revision, status, changeset_comment_id, modified_at, version, pull_request_id) FROM stdin;
\.


--
-- Name: changeset_statuses_changeset_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('changeset_statuses_changeset_status_id_seq', 1, false);


--
-- Data for Name: db_migrate_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY db_migrate_version (repository_id, repository_path, version) FROM stdin;
rhodecode_db_migrations	versions	11
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY groups (group_id, group_name, group_parent_id, group_description, enable_locking) FROM stdin;
1	RC	\N	RC group	f
2	RC/mygr	1	RC/mygr group	f
3	BIG	\N	BIG group	f
4	RC/rc2	1	RC/rc2 group	f
5	RC/INRC	1	RC/INRC group	f
6	RC/INRC/L2_NEW	5	RC/INRC/L2_NEW group	f
7	RC/INRC/L2_NEW/L3	6	RC/INRC/L2_NEW/L3 group	f
8	RC/lol	1	RC/lol group	f
\.


--
-- Name: groups_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('groups_group_id_seq', 8, true);


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY notifications (notification_id, subject, body, created_by, created_on, type) FROM stdin;
\.


--
-- Name: notifications_notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('notifications_notification_id_seq', 1, false);


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY permissions (permission_id, permission_name, permission_longname) FROM stdin;
1	repository.none	repository.none
2	repository.read	repository.read
3	repository.write	repository.write
4	repository.admin	repository.admin
5	group.none	group.none
6	group.read	group.read
7	group.write	group.write
8	group.admin	group.admin
9	hg.admin	hg.admin
10	hg.create.none	hg.create.none
11	hg.create.repository	hg.create.repository
12	hg.fork.none	hg.fork.none
13	hg.fork.repository	hg.fork.repository
14	hg.register.none	hg.register.none
15	hg.register.manual_activate	hg.register.manual_activate
16	hg.register.auto_activate	hg.register.auto_activate
\.


--
-- Name: permissions_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('permissions_permission_id_seq', 16, true);


--
-- Data for Name: pull_request_reviewers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY pull_request_reviewers (pull_requests_reviewers_id, pull_request_id, user_id) FROM stdin;
\.


--
-- Name: pull_request_reviewers_pull_requests_reviewers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('pull_request_reviewers_pull_requests_reviewers_id_seq', 1, false);


--
-- Data for Name: pull_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY pull_requests (pull_request_id, title, description, status, created_on, updated_on, user_id, revisions, org_repo_id, org_ref, other_repo_id, other_ref) FROM stdin;
\.


--
-- Name: pull_requests_pull_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('pull_requests_pull_request_id_seq', 1, false);


--
-- Data for Name: repo_to_perm; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY repo_to_perm (repo_to_perm_id, user_id, permission_id, repository_id) FROM stdin;
1	1	2	1
2	1	2	2
3	1	2	3
4	1	2	4
5	1	2	5
6	1	2	6
7	1	2	7
8	1	2	8
9	1	2	9
10	1	2	10
11	1	2	11
12	1	2	12
13	1	2	13
14	1	2	14
15	1	2	15
16	1	2	16
17	1	2	17
18	1	2	18
19	1	2	19
20	1	2	20
21	1	2	21
22	1	2	22
23	1	2	23
24	1	2	24
25	1	2	25
26	1	2	26
27	1	2	27
28	1	2	28
29	1	2	29
30	1	2	30
31	1	2	31
32	1	2	32
33	1	2	33
34	1	2	34
35	1	2	35
36	1	2	36
37	1	2	37
38	1	2	38
39	1	2	39
40	1	2	40
41	1	2	41
42	1	2	42
43	1	2	43
44	1	2	44
45	1	2	45
46	1	2	46
47	1	2	47
48	1	2	48
49	1	2	49
50	1	2	50
51	1	2	51
52	1	2	52
53	1	2	53
54	1	2	54
55	1	2	55
56	1	2	56
57	1	2	57
58	1	2	58
59	1	2	59
60	1	2	60
61	1	2	61
62	1	2	62
63	1	2	63
64	1	2	64
65	1	2	65
\.


--
-- Name: repo_to_perm_repo_to_perm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('repo_to_perm_repo_to_perm_id_seq', 65, true);


--
-- Data for Name: repositories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY repositories (repo_id, repo_name, clone_uri, repo_type, user_id, private, statistics, downloads, description, created_on, updated_on, landing_revision, enable_locking, locked, changeset_cache, fork_id, group_id) FROM stdin;
1	RC/mygr/lol	http://user@vm/RC/mygr/lol	hg	2	f	f	f	RC/mygr/lol repository	2013-05-28 20:26:59.886314	2013-05-28 20:26:59.886502	tip	f	\N	\N	\N	2
2	RC/fakeclone	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:26:59.94415	2013-05-09 01:48:00	tip	f	\N	\\x7b227261775f6964223a202264666137643337363737386436383164313831386634316231373730366566613630333362343037222c202273686f72745f6964223a2022646661376433373637373864222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d30395430313a34383a3030222c20226d657373616765223a202266697865645c6e222c20227265766973696f6e223a203239337d	\N	1
3	RC/muay	\N	hg	2	f	f	f	RC/muay repository	2013-05-28 20:27:00.114841	2013-05-28 20:27:00.114864	tip	f	\N	\N	\N	1
4	BIG/git	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:00.171891	2012-10-21 23:47:54	tip	f	\N	\\x7b227261775f6964223a202233306634633636653633343736306138316162323761323336666531663234383266366637383536222c202273686f72745f6964223a2022333066346336366536333437222c2022617574686f72223a20224a756e696f20432048616d616e6f203c6769747374657240706f626f782e636f6d3e222c202264617465223a2022323031322d31302d32315432333a34373a3534222c20226d657373616765223a202257686174277320636f6f6b696e672028323031322f313020233037295c6e222c20227265766973696f6e223a2033323136307d	\N	3
5	RC/origin-fork	\N	hg	2	f	f	f	RC/origin-fork repository	2013-05-28 20:27:01.457264	2013-03-06 20:16:20	tip	f	\N	\\x7b227261775f6964223a202266306365333961366639656466633633393264346436313337663035626233383731653431373830222c202273686f72745f6964223a2022663063653339613666396564222c2022617574686f72223a202252686f6465436f64652041646d696e203c6d617263696e40707974686f6e2d626c6f672e636f6d3e222c202264617465223a2022323031332d30332d30365432303a31363a3230222c20226d657373616765223a20224564697465642066696c6520766961206f7074696f6e735c6e2d20666978656420315c6e2d66207869656420325c6e616e6420736f206f6e20736f206f6e207472616c6c616c616c61222c20227265766973696f6e223a2032317d	\N	1
6	one	\N	hg	2	f	f	f	one repository	2013-05-28 20:27:01.525404	2013-05-23 12:11:57	tip	f	\N	\\x7b227261775f6964223a202233393435643961623264396533323262623666643561613763333461316530313132326265343662222c202273686f72745f6964223a2022333934356439616232643965222c2022617574686f72223a202252686f6465436f64652041646d696e203c6d617263696e40707974686f6e2d626c6f672e636f6d3e222c202264617465223a2022323031332d30352d32335431323a31313a3537222c20226d657373616765223a202241646465642066696c65207669612052686f6465436f6465222c20227265766973696f6e223a20307d	\N	\N
7	rhodecode.bak.1	\N	hg	2	f	f	f	rhodecode.bak.1 repository	2013-05-28 20:27:01.578685	2013-05-28 14:44:56	tip	f	\N	\\x7b227261775f6964223a202232336637333938396439323230343636666239646237633635316431336162663637393666373663222c202273686f72745f6964223a2022323366373339383964393232222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d32385431343a34343a3536222c20226d657373616765223a20226d657267652064657620696e746f2072686f6465636f64652d70616d222c20227265766973696f6e223a20343034307d	\N	\N
8	csa-collins	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:01.645073	2013-02-25 17:31:39	tip	f	\N	\\x7b227261775f6964223a202238626536613130643634356338646461356631663333313439363232383131386165383732636538222c202273686f72745f6964223a2022386265366131306436343563222c2022617574686f72223a20224261737469616e20416c62657273203c696e666f406261737469616e616c626572732e64653e222c202264617465223a2022323031332d30322d32355431373a33313a3339222c20226d657373616765223a20224d65726765206272616e6368202773746167652720696e746f207374616765325c6e222c20227265766973696f6e223a20323733317d	\N	\N
9	csa-harmony	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:01.870853	2013-05-22 14:49:45	tip	f	\N	\\x7b227261775f6964223a202232376235393630333631386230373235396361306462366230303939306665656261393639333066222c202273686f72745f6964223a2022323762353936303336313862222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d32325431343a34393a3435222c20226d657373616765223a20224164646564206b776172677320746f2073657475702066756e6374696f6e7320666f72206c61746572206f7074696f6e616c20706172616d735c6e222c20227265766973696f6e223a203333397d	\N	\N
10	RC/ąqweqwe	\N	hg	2	f	f	f	RC/ąqweqwe repository	2013-05-28 20:27:02.376512	2013-05-28 20:27:02.376535	tip	f	\N	\N	\N	1
11	rhodecode	\N	hg	2	f	f	f	rhodecode repository	2013-05-28 20:27:02.424079	2013-05-28 20:16:08	tip	f	\N	\\x7b227261775f6964223a202237613161333935356434343661343664353235663034326265373339343161303231323266633332222c202273686f72745f6964223a2022376131613339353564343436222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d32385432303a31363a3038222c20226d657373616765223a20226d6967726174696f6e20746f20312e372e30222c20227265766973696f6e223a20343034357d	\N	\N
12	csa-unity	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:02.495342	2013-04-29 14:38:23	tip	f	\N	\\x7b227261775f6964223a202230393337303837353965626634666432626231626463616436316662363131626333323933336433222c202273686f72745f6964223a2022303933373038373539656266222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30342d32395431343a33383a3233222c20226d657373616765223a202272657665727420746f206c6f67626f6f6b20302e332e30222c20227265766973696f6e223a2032387d	\N	\N
13	RC/łęcina	\N	hg	2	f	f	f	RC/łęcina repository	2013-05-28 20:27:02.664128	2013-03-06 16:17:49	tip	f	\N	\\x7b227261775f6964223a202231656535383962636661393231326335313130656135633166653263633866663665616631333033222c202273686f72745f6964223a2022316565353839626366613932222c2022617574686f72223a202252686f6465436f64652041646d696e203c6d617263696e40707974686f6e2d626c6f672e636f6d3e222c202264617465223a2022323031332d30332d30365431363a31373a3439222c20226d657373616765223a202241646465642066696c65207669612052686f6465436f6465222c20227265766973696f6e223a20307d	\N	1
14	waitress	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:02.721063	2013-05-28 13:21:35	tip	f	\N	\\x7b227261775f6964223a202265356431333863653366373534653630333165376162643736653566353237333633666461663432222c202273686f72745f6964223a2022653564313338636533663735222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d32385431333a32313a3335222c20226d657373616765223a2022416464656420646f637320616e64206e657720666c616720696e746f2072756e6e65725c6e222c20227265766973696f6e223a203237327d	\N	\N
15	RC/rc2/test2	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:02.896717	2013-03-03 00:29:35	tip	f	\N	\\x7b227261775f6964223a202230656233333034666333336430356433323866383632376239616434346461653833663331336132222c202273686f72745f6964223a2022306562333330346663333364222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30332d30335430303a32393a3335222c20226d657373616765223a20224d65726765206272616e636820277374616765275c6e5c6e2a2073746167653a5c6e202066697820726571756573747320312e31206a736f6e206d6574686f645c6e202066697865642074657374735c6e20206d6f76656420746573747320696e746f207061636b6167655c6e20202d62756d7020646973747269627574655c6e2020757064617465202e67697469676e6f72655c6e202076657273696f6e20667265657a65206f66206c6962735c6e202072656d6f766520676576656e742066726f6d20494f20617320646570656e64656e63795c6e202061646420756e69747920617320646570735c6e202066756c6c792064656c65676174652041555448206261636b20746f2061726d7374726f6e675c6e222c20227265766973696f6e223a2035307d	\N	4
16	RC/origin-fork-fork	\N	hg	2	f	f	f	RC/origin-fork-fork repository	2013-05-28 20:27:03.013741	2013-05-06 23:44:50	tip	f	\N	\\x7b227261775f6964223a202236643939653064346466636334613561666135633133386665613230393834373036333466373733222c202273686f72745f6964223a2022366439396530643464666363222c2022617574686f72223a202252686f6465436f64652041646d696e203c6d617263696e40707974686f6e2d626c6f672e636f6d3e222c202264617465223a2022323031332d30352d30365432333a34343a3530222c20226d657373616765223a20224973737565202331373039343a20436c656172207374616c65207468726561642073746174657320616674657220666f726b28292e5c6e5c6e4e6f746520746861742074686973206973206120706f74656e7469616c6c792064697372757074697665206368616e67652073696e6365206974206d61795c6e72656c6561736520736f6d652073797374656d207265736f757263657320776869636820776f756c64206f74686572776973652072656d61696e5c6e70657270657475616c6c7920616c6976652028652e672e20646174616261736520636f6e6e656374696f6e73206b65707420696e207468726561642d6c6f63616c5c6e73746f72616765292e222c20227265766973696f6e223a2032357d	\N	1
17	RC/rc2/test4	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:03.077195	2013-03-21 22:55:29	tip	f	\N	\\x7b227261775f6964223a202233623661633766356539333264346464313338373161306232336436636139383531306438386332222c202273686f72745f6964223a2022336236616337663565393332222c2022617574686f72223a202252686f6465436f64652041646d696e203c6d617263696e40707974686f6e2d626c6f672e636f6d3e222c202264617465223a2022323031332d30332d32315432323a35353a3239222c20226d657373616765223a2022647361646173222c20227265766973696f6e223a2035317d	\N	4
18	RC/vcs-git	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:03.207037	2013-04-26 23:34:15	tip	f	\N	\\x7b227261775f6964223a202239306461316636396136633630663764346435363436656533396163356636313038626330373763222c202273686f72745f6964223a2022393064613166363961366336222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30342d32365432333a33343a3135222c20226d657373616765223a20226d65726765207769746820474954207663735c6e222c20227265766973696f6e223a203634387d	\N	1
19	rhodecode-extensions	\N	hg	2	f	f	f	rhodecode-extensions repository	2013-05-28 20:27:03.363473	2013-02-13 16:50:33	tip	f	\N	\\x7b227261775f6964223a202264613765356637613339643332303366663062346166353031386163346138306439346564316434222c202273686f72745f6964223a2022646137653566376133396433222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30322d31335431363a35303a3333222c20226d657373616765223a20224c696e6b6966792068697063686174206d65737361676573222c20227265766973696f6e223a20327d	\N	\N
20	rhodecode-cli-gist	\N	hg	2	f	f	f	rhodecode-cli-gist repository	2013-05-28 20:27:03.415835	2013-05-28 20:27:03.415858	tip	f	\N	\N	\N	\N
21	test.onaut.com	\N	git	2	f	f	f	Unnamed repository	2013-05-28 20:27:03.46164	2013-04-29 11:08:31	tip	f	\N	\\x7b227261775f6964223a202236666465656664323034633461656637636263623966656563646564313436373364383563663230222c202273686f72745f6964223a2022366664656566643230346334222c2022617574686f72223a2022596f7572204e616d65203c796f75406578616d706c652e636f6d3e222c202264617465223a2022323031332d30342d32395431313a30383a3331222c20226d657373616765223a2022666f6f6261725c6e222c20227265766973696f6e223a20307d	\N	\N
22	RC/new	\N	hg	2	f	f	f	RC/new repository	2013-05-28 20:27:03.580255	2013-04-17 13:02:59	tip	f	\N	\\x7b227261775f6964223a202239333139326530336133353532623864613466656534306530303163363033303437323362623432222c202273686f72745f6964223a2022393331393265303361333535222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30342d31375431333a30323a3539222c20226d657373616765223a202272656e616d65222c20227265766973696f6e223a20317d	\N	1
46	RC/qweqwe-fork2	\N	hg	2	f	f	f	RC/qweqwe-fork2 repository	2013-05-28 20:27:17.359662	2013-05-28 20:27:17.359684	tip	f	\N	\N	\N	1
23	csa-aldrin	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:03.639793	2013-05-02 23:47:52	tip	f	\N	\\x7b227261775f6964223a202236376565396538333063323235393231656331353937346163316466646531376139333065326662222c202273686f72745f6964223a2022363765653965383330633232222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d30325432333a34373a3532222c20226d657373616765223a20224d65726765206272616e636820277374616765275c6e5c6e2a2073746167653a5c6e20206d6f76656420676576656e7420696e746f206f757420696e7465726e616c207365727665725c6e202073747570696420617373686f6c657320696e20676576656e742073686f756c64206c6561726e20686f7720746f207061636b6167652e2e2e5c6e2020666978656420676576656e7420646570656e64656e6379206c696e6b5c6e202061646465642073657061726174652063616c6c20666f722073657373696f6e2076616c69646174696f6e5c6e222c20227265766973696f6e223a203239337d	\N	\N
24	vcs	\N	hg	2	f	f	f	vcs repository	2013-05-28 20:27:03.856575	2013-05-09 00:28:54	tip	f	\N	\\x7b227261775f6964223a202236666261353966396637383036613534356130653565626163393336393931383238343336323630222c202273686f72745f6964223a2022366662613539663966373830222c2022617574686f72223a20224c756b61737a2042616c6365727a616b203c6c756b61737a62616c6365727a616b40676d61696c2e636f6d3e222c202264617465223a2022323031332d30352d30395430303a32383a3534222c20226d657373616765223a20224d657267652070756c6c207265717565737420233131372066726f6d206e69656462616c736b692f6d61737465725c6e5c6e4b65794572726f723a2027616c6c27222c20227265766973696f6e223a203730377d	\N	\N
25	csa-prometheus	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:03.916977	2013-04-29 14:37:43	tip	f	\N	\\x7b227261775f6964223a202261373139626438326432356537343131666462373937396331326330383366353961323036613663222c202273686f72745f6964223a2022613731396264383264323565222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30342d32395431343a33373a3433222c20226d657373616765223a2022726576657274206c6f67626f6f6b20746f20302e332e30222c20227265766973696f6e223a2037397d	\N	\N
26	RC/INRC/trololo	\N	hg	2	f	f	f	RC/INRC/trololo repository	2013-05-28 20:27:04.096413	2013-05-28 20:27:04.096437	tip	f	\N	\N	\N	5
27	RC/empty-git	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:04.148472	2013-05-28 20:27:04.148509	tip	f	\N	\N	\N	1
28	csa-salt-states	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:04.212846	2013-05-06 14:48:48	tip	f	\N	\\x7b227261775f6964223a202230633230646337326261656564633363653834306336313131373463376531636433623034393139222c202273686f72745f6964223a2022306332306463373262616565222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d30365431343a34383a3438222c20226d657373616765223a2022696e6372656173652073616d706c696e67206f66204350552074696d6520746f20302e357320666f72206d6f7265207265616c697374696320646174612e222c20227265766973696f6e223a2037317d	\N	\N
29	rhodecode-premium	\N	hg	2	f	f	f	rhodecode-premium repository	2013-05-28 20:27:04.419538	2013-03-21 22:58:11	tip	f	\N	\\x7b227261775f6964223a202264656433356266303137663136626361643636313163376666653362316231633130393432663530222c202273686f72745f6964223a2022646564333562663031376631222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30332d32315432323a35383a3131222c20226d657373616765223a202276657273696f6e2062756d7020746f20312e352e347032222c20227265766973696f6e223a20333637347d	\N	\N
30	RC/qweqwe-fork	\N	hg	2	f	f	f	RC/qweqwe-fork repository	2013-05-28 20:27:04.494164	2013-05-28 20:27:04.494188	tip	f	\N	\N	\N	1
31	testrepo-quick	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:04.547757	2012-08-31 11:34:33	tip	f	\N	\\x7b227261775f6964223a202236303763396632336633373731626633353731346639626166353539666433313138366432353930222c202273686f72745f6964223a2022363037633966323366333737222c2022617574686f72223a202253656261737469616e204b726575747a626572676572203c73656261737469616e406170707a6f6e6175742e636f6d3e222c202264617465223a2022323031322d30382d33315431313a33343a3333222c20226d657373616765223a20226164646564207465737420666f72202e617a2d7368617265642066696c655c6e222c20227265766973696f6e223a2031327d	\N	\N
32	RC/test	\N	hg	2	f	f	f	RC/test repository	2013-05-28 20:27:04.697514	2013-01-30 22:56:03	tip	f	\N	\\x7b227261775f6964223a202265353032356533313664396163623339653566383631633439343234306265346635643536646536222c202273686f72745f6964223a2022653530323565333136643961222c2022617574686f72223a202252686f6465436f64652041646d696e203c6d617263696e406d61712e696f3e222c202264617465223a2022323031332d30312d33305432323a35363a3033222c20226d657373616765223a20223c7363726970743e616c65727428277873733227293b3c2f7363726970743e202066697865732023373030222c20227265766973696f6e223a20327d	\N	1
33	remote-salt	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:04.750525	2012-10-14 22:04:05	tip	f	\N	\\x7b227261775f6964223a202264363631646337323439326536366361623761363437646362353635323030393036376161386364222c202273686f72745f6964223a2022643636316463373234393265222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031322d31302d31345432323a30343a3035222c20226d657373616765223a20224c6f6767696e675c6e4f6e2d7468652d666c79206d736720656e6372797074696f6e207573696e6720676f6f676c6573206b6579437a6172206c6962222c20227265766973696f6e223a20337d	\N	\N
34	BIG/android	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:04.869224	2012-06-17 00:44:46	tip	f	\N	\\x7b227261775f6964223a202265383662313437653462363930386137633561623039363364373766623038363736373962316565222c202273686f72745f6964223a2022653836623134376534623639222c2022617574686f72223a20224265726e6861726420526f73656e6b7261656e7a6572203c4265726e686172642e526f73656e6b72616e7a6572406c696e61726f2e6f72673e222c202264617465223a2022323031322d30362d31375430303a34343a3436222c20226d657373616765223a202270616e64613a204261636b706f72742048444d492076732e204456492070617463682066726f6d206b65726e656c2f70616e64612e6769745c6e5c6e5468697320706174636820616c6c6f777320737769746368696e6720746865207072696d61727920646973706c6179206f7574707574206465766963652e5c6e5c6e4368616e67652d49643a2049366533306538376262633761613732623561636336653663346564333430313938333565363532345c6e5369676e65642d6f66662d62793a204265726e6861726420526f73656e6b7261656e7a6572203c4265726e686172642e526f73656e6b72616e7a6572406c696e61726f2e6f72673e5c6e222c20227265766973696f6e223a203239343839367d	\N	3
35	DOCS	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:16.065483	2013-04-25 16:45:59	tip	f	\N	\\x7b227261775f6964223a202231653461373238656537613661613838626531313236306436343739613434366562383635646533222c202273686f72745f6964223a2022316534613732386565376136222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30342d32355431363a34353a3539222c20226d657373616765223a202273796e6320646f637320776974682061726d7374726f6e67222c20227265766973696f6e223a2031357d	\N	\N
36	rhodecode-git	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:16.225335	2013-01-04 00:24:22	tip	f	\N	\\x7b227261775f6964223a202236323966313533386164343830306666303531313335313666366139333365326232343366323035222c202273686f72745f6964223a2022363239663135333861643438222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30312d30345430303a32343a3232222c20226d657373616765223a20226e6963657220726570726573656e746174696f6e206f66206c697374206f662072657363616e6e6564207265706f7369746f726965735c6e5c6e2d2d48472d2d5c6e6272616e6368203a20626574615c6e222c20227265766973696f6e223a20333134327d	\N	\N
37	RC/bin-ops	\N	hg	2	f	f	f	RC/bin-ops repository	2013-05-28 20:27:16.463774	2013-05-12 12:39:34	tip	f	\N	\\x7b227261775f6964223a202234323331373632643863316161636135626533646231353939313037313233366333326537363534222c202273686f72745f6964223a2022343233313736326438633161222c2022617574686f72223a202252686f6465436f64652041646d696e203c6d617263696e40707974686f6e2d626c6f672e636f6d3e222c202264617465223a2022323031332d30352d31325431323a33393a3334222c20226d657373616765223a20224564697465642066696c652066696c6531207669612052686f6465436f6465222c20227265766973696f6e223a2032337d	\N	1
38	RC/INRC/L2_NEW/lalalal	\N	hg	2	f	f	f	RC/INRC/L2_NEW/lalalal repository	2013-05-28 20:27:16.555625	2013-05-28 20:27:16.55565	tip	f	\N	\N	\N	6
39	RC/fork-remote	\N	hg	2	f	f	f	RC/fork-remote repository	2013-05-28 20:27:16.622524	2013-03-10 22:47:24	tip	f	\N	\\x7b227261775f6964223a202236303535353438346130613064366535323565396437616231623164636535616239656239343837222c202273686f72745f6964223a2022363035353534383461306130222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30332d31305432323a34373a3234222c20226d657373616765223a2022616161222c20227265766973696f6e223a2032367d	\N	1
40	RC/INRC/L2_NEW/L3/repo_test_move	\N	hg	2	f	f	f	RC/INRC/L2_NEW/L3/repo_test_move repository	2013-05-28 20:27:16.717095	2013-05-28 20:27:16.717133	tip	f	\N	\N	\N	7
41	RC/gogo-fork	\N	hg	2	f	f	f	RC/gogo-fork repository	2013-05-28 20:27:16.790103	2013-05-28 20:27:16.790129	tip	f	\N	\N	\N	1
42	quest	\N	hg	2	f	f	f	quest repository	2013-05-28 20:27:16.858741	2013-03-04 23:01:40	tip	f	\N	\\x7b227261775f6964223a202235346230316366646561323562663431636438653961313834633538353263356434386438363463222c202273686f72745f6964223a2022353462303163666465613235222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30332d30345432333a30313a3430222c20226d657373616765223a202274656d706c61746520616e642076657273696f6e20302e302e31222c20227265766973696f6e223a2034317d	\N	\N
43	RC/foobar	\N	hg	2	f	f	f	RC/foobar repository	2013-05-28 20:27:16.930525	2013-04-15 21:34:57	tip	f	\N	\\x7b227261775f6964223a202263313764633363353636393532383133653834303337646664363261343735356564336339313263222c202273686f72745f6964223a2022633137646333633536363935222c2022617574686f72223a20224d6972656b204b6f7474203c6d617263696e40707974686f6e2d626c6f672e636f6d3e222c202264617465223a2022323031332d30342d31355432313a33343a3537222c20226d657373616765223a20224564697465642066696c65206c6f6c2e727374207669612052686f6465436f6465222c20227265766973696f6e223a20317d	\N	1
44	csa-hyperion	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:17.021283	2013-05-20 21:58:28	tip	f	\N	\\x7b227261775f6964223a202232353263393236643130373032653665663763323435366632666332333839323830386535336130222c202273686f72745f6964223a2022323532633932366431303730222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d32305432313a35383a3238222c20226d657373616765223a2022666978657320666f72206e657720636f64655c6e222c20227265766973696f6e223a2035377d	\N	\N
45	RC/git-pull-test	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:17.231975	2013-05-20 13:03:02	tip	f	\N	\\x7b227261775f6964223a202262326366313133366630396661363164663930343639623433333130363135393834626337643535222c202273686f72745f6964223a2022623263663131333666303966222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d32305431333a30333a3032222c20226d657373616765223a202261646465645c6e222c20227265766973696f6e223a2031337d	\N	1
47	RC/jap	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:17.427862	2013-04-24 11:15:30	tip	f	\N	\\x7b227261775f6964223a202232663632636532323435336136376565666436666162316434653035333532306538646562646636222c202273686f72745f6964223a2022326636326365323234353361222c2022617574686f72223a202244656d6f2055736572203c64656d6f4072686f6465636f64652e6f72673e222c202264617465223a2022323031332d30342d32345431313a31353a3330222c20226d657373616765223a20225c75333064355c75333061315c75333061345c75333065625c75386666645c7535326130222c20227265766973696f6e223a20357d	\N	1
48	RC/hg-repo	\N	hg	2	f	f	f	RC/hg-repo repository	2013-05-28 20:27:17.558936	2013-05-08 22:54:45	tip	f	\N	\\x7b227261775f6964223a202264363364343065386230363835616636646235663263663737303065383032313661663563373339222c202273686f72745f6964223a2022643633643430653862303638222c2022617574686f72223a202252686f6465436f64652041646d696e203c6d617263696e40707974686f6e2d626c6f672e636f6d3e222c202264617465223a2022323031332d30352d30385432323a35343a3435222c20226d657373616765223a20224564697465642066696c652068616861207669612052686f6465436f6465222c20227265766973696f6e223a2032357d	\N	1
49	RC/origin	\N	hg	2	f	f	f	RC/origin repository	2013-05-28 20:27:17.634344	2013-04-05 13:05:02	tip	f	\N	\\x7b227261775f6964223a202235666266326630656164613433626333336139346534383335303333333564386636373537303933222c202273686f72745f6964223a2022356662663266306561646134222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30342d30355431333a30353a3032222c20226d657373616765223a20226669786564222c20227265766973696f6e223a2032397d	\N	1
50	rhodecode-cli-api	\N	hg	2	f	f	f	rhodecode-cli-api repository	2013-05-28 20:27:17.708944	2013-05-28 20:27:17.708995	tip	f	\N	\N	\N	\N
51	RC/rc2/test3	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:17.781161	2013-03-03 00:29:35	tip	f	\N	\\x7b227261775f6964223a202230656233333034666333336430356433323866383632376239616434346461653833663331336132222c202273686f72745f6964223a2022306562333330346663333364222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30332d30335430303a32393a3335222c20226d657373616765223a20224d65726765206272616e636820277374616765275c6e5c6e2a2073746167653a5c6e202066697820726571756573747320312e31206a736f6e206d6574686f645c6e202066697865642074657374735c6e20206d6f76656420746573747320696e746f207061636b6167655c6e20202d62756d7020646973747269627574655c6e2020757064617465202e67697469676e6f72655c6e202076657273696f6e20667265657a65206f66206c6962735c6e202072656d6f766520676576656e742066726f6d20494f20617320646570656e64656e63795c6e202061646420756e69747920617320646570735c6e202066756c6c792064656c65676174652041555448206261636b20746f2061726d7374726f6e675c6e222c20227265766973696f6e223a2035307d	\N	4
52	csa-armstrong	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:17.898234	2013-05-22 18:10:20	tip	f	\N	\\x7b227261775f6964223a202236306666613230313866613132306339376330633566636162393365636438326532633361363931222c202273686f72745f6964223a2022363066666132303138666131222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d32325431383a31303a3230222c20226d657373616765223a20226669782061637475616c2070726f677265737320696e63726561736520696e2073616c742063616c6c735c6e222c20227265766973696f6e223a20313134307d	\N	\N
53	RC/trololo	\N	hg	2	f	f	f	RC/trololo repository	2013-05-28 20:27:18.620592	2013-03-28 02:35:50	tip	f	\N	\\x7b227261775f6964223a202238393064373436396162616333363036333763386366373966313538623137303431356531363533222c202273686f72745f6964223a2022383930643734363961626163222c2022617574686f72223a202264656d6f2075736572203c6d617263696e406d61712e696f3e222c202264617465223a2022323031332d30332d32385430323a33353a3530222c20226d657373616765223a202241646465642066696c65207669612052686f6465436f6465222c20227265766973696f6e223a20307d	\N	1
54	testrepo-wp	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:18.695645	2012-08-27 11:05:37	tip	f	\N	\\x7b227261775f6964223a202264393461663531633130313032303433306132386463616561313135336464643932326332396563222c202273686f72745f6964223a2022643934616635316331303130222c2022617574686f72223a202253656261737469616e204b726575747a626572676572203c73656261737469616e406170707a6f6e6175742e636f6d3e222c202264617465223a2022323031322d30382d32375431313a30353a3337222c20226d657373616765223a2022757064617465642063726564735c6e222c20227265766973696f6e223a20377d	\N	\N
55	pyramidpypi	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:18.824235	2013-04-25 16:34:48	tip	f	\N	\\x7b227261775f6964223a202265643961636566666164613365663338353039633564373031306230313662613435653832393434222c202273686f72745f6964223a2022656439616365666661646133222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30342d32355431363a33343a3438222c20226d657373616765223a202276657273696f6e2062756d70222c20227265766973696f6e223a2032387d	\N	\N
56	salt	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:19.036099	2012-10-15 05:20:58	tip	f	\N	\\x7b227261775f6964223a202262643434383332323330666331396562383066653439656630316261646234373765663863613663222c202273686f72745f6964223a2022626434343833323233306663222c2022617574686f72223a202254686f6d61732053204861746368203c746861746368343540676d61696c2e636f6d3e222c202264617465223a2022323031322d31302d31355430353a32303a3538222c20226d657373616765223a20224d657267652070756c6c20726571756573742023323234342066726f6d2046697265486f73742f746f706c6576656c5f776d695f696d706f72745c6e5c6e546f706c6576656c20776d6920696d706f7274222c20227265766973696f6e223a20363935377d	\N	\N
57	RC/lol/haha	\N	hg	2	f	f	f	RC/lol/haha repository	2013-05-28 20:27:19.44935	2013-05-28 20:27:19.449372	tip	f	\N	\N	\N	8
58	csa-io	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:19.531664	2013-05-02 22:52:54	tip	f	\N	\\x7b227261775f6964223a202262643065663731666366643038386138326238363237653630616161316632303230656433336261222c202273686f72745f6964223a2022626430656637316663666430222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d30325432323a35323a3534222c20226d657373616765223a20224d65726765206272616e636820277374616765275c6e5c6e2a2073746167653a5c6e2020557365206578745f6a736f6e20696e7374656164206f6620706c61696e2073696d706c656a736f6e2073657269616c697a65725c6e20206c6f67206572726f7273206f6e207265737466756c6c206a736f6e20706172736572732f6465636f646572735c6e2020666978656420736f6d652073657269616c697a6174696f6e2070726f626c656d735c6e202076657273696f6e2062756d705c6e20205265706f7369746f7279207265766973696f6e73204150495c6e20206d657263757269616c2076657273696f6e2062756d705c6e202042756d70205643532076657273696f6e20746f20302e342e3020616e64206d6f766520697420746f20636f64652e6170707a6f6e6175742e636f6d5c6e2020666978206c6f6767696e67206f6e206368616e676573206a736f6e206d6f64756c6520696e20726571756573747320312e585c6e222c20227265766973696f6e223a2035397d	\N	\N
59	enc-envelope	\N	hg	2	f	f	f	enc-envelope repository	2013-05-28 20:27:19.74793	2013-03-07 15:37:40	tip	f	\N	\\x7b227261775f6964223a202238313030363666383335643663303832393530666337383238646564353062396238643963323239222c202273686f72745f6964223a2022383130303636663833356436222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30332d30375431353a33373a3430222c20226d657373616765223a202273686f77206d6f72652064657461696c656420696e666f2061626f75742077726f6e672073747265616d222c20227265766973696f6e223a20357d	\N	\N
60	RC/gogo2	\N	hg	2	f	f	f	RC/gogo2 repository	2013-05-28 20:27:19.827312	2013-05-28 20:27:19.827334	tip	f	\N	\N	\N	1
61	csa-libcloud	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:19.892075	2013-04-17 16:42:42	tip	f	\N	\\x7b227261775f6964223a202261326661353531363333636533363937616336336139333561613731663165376238303232326165222c202273686f72745f6964223a2022613266613535313633336365222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30342d31375431363a34323a3432222c20226d657373616765223a202266696c746572206f6e6c79206c697374656e65727320427269676874626f782063616e2070726f63657373222c20227265766973696f6e223a20313839357d	\N	\N
62	RC/git-test	\N	git	2	f	f	f	Unnamed repository	2013-05-28 20:27:20.231554	2013-03-25 22:50:04	tip	f	\N	\\x7b227261775f6964223a202235643561646464666339323963643839653931313131366436306231323064316361613866333964222c202273686f72745f6964223a2022356435616464646663393239222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30332d32355432323a35303a3034222c20226d657373616765223a202266785c6e222c20227265766973696f6e223a20397d	\N	1
63	RC/rc2/test	\N	hg	2	f	f	f	RC/rc2/test repository	2013-05-28 20:27:20.356786	2013-05-28 20:27:20.35683	tip	f	\N	\N	\N	4
64	rhodecode.bak	\N	hg	2	f	f	f	rhodecode.bak repository	2013-05-28 20:27:20.423238	2013-05-28 02:41:49	tip	f	\N	\\x7b227261775f6964223a202262633862616365663164303663306330643132616337386638326565353330666363393661663561222c202273686f72745f6964223a2022626338626163656631643036222c2022617574686f72223a20224d617263696e204b757a6d696e736b69203c6d617263696e40707974686f6e2d776f726b732e636f6d3e222c202264617465223a2022323031332d30352d32385430323a34313a3439222c20226d657373616765223a20224164646564206e657720617069206d6574686f64735c6e2d206765745f7365727665725f696e666f5c6e2d206765745f69705c6e2d207570646174655f7265706f5c6e2d206765745f7265706f5f67726f75705c6e2d206765745f7265706f5f67726f7570735c6e2d206372656174655f7265706f5f67726f75705c6e2d207570646174655f7265706f5f67726f75705c6e2d2064656c6574655f7265706f5f67726f75705c6e2d207570646174655f757365725f67726f75705c6e2d206765745f676973745c6e2d206765745f67697374735c6e2d2064656c6574655f676973745c6e5c6e2b207265666163746f72696e67206f66206e616d657320616e642067656e6572616c2041504920636c65616e75702e5c6e41504920646f63732077696c6c206e6f772062652067656e657261746564206261736564206f6e2066756e6374696f6e20646f63737472696e67735c6e546869732077696c6c206d616b652069742065617369657220746f20646f2070726f70657220646f63756d656e746174696f6e20666f72204150492e222c20227265766973696f6e223a20343033397d	\N	\N
65	RC/kiall-nova	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:27:20.524084	2012-10-23 10:22:06	tip	f	\N	\\x7b227261775f6964223a202261306663643132343830373161643636623631306561633439303361646633366233313433393062222c202273686f72745f6964223a2022613066636431323438303731222c2022617574686f72223a20224a656e6b696e73203c6a656e6b696e73407265766965772e6f70656e737461636b2e6f72673e222c202264617465223a2022323031322d31302d32335431303a32323a3036222c20226d657373616765223a20224d65726765205c22466978206e6f76612d766f6c756d652d75736167652d61756469745c22222c20227265766973696f6e223a2031373235337d	\N	1
\.


--
-- Data for Name: repositories_fields; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY repositories_fields (repo_field_id, repository_id, field_key, field_label, field_value, field_desc, field_type, created_on) FROM stdin;
\.


--
-- Name: repositories_fields_repo_field_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('repositories_fields_repo_field_id_seq', 1, false);


--
-- Name: repositories_repo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('repositories_repo_id_seq', 65, true);


--
-- Data for Name: rhodecode_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY rhodecode_settings (app_settings_id, app_settings_name, app_settings_value) FROM stdin;
1	realm	RhodeCode authentication
2	title	RhodeCode
3	ga_code	123456
4	show_public_icon	True
5	show_private_icon	True
6	stylify_metatags	False
7	ldap_active	false
8	ldap_host	
9	ldap_port	389
10	ldap_tls_kind	PLAIN
11	ldap_tls_reqcert	
12	ldap_dn_user	
13	ldap_dn_pass	
14	ldap_base_dn	
15	ldap_filter	
16	ldap_search_scope	
17	ldap_attr_login	
18	ldap_attr_firstname	
19	ldap_attr_lastname	
20	ldap_attr_email	
21	default_repo_enable_locking	False
22	default_repo_enable_downloads	False
23	default_repo_enable_statistics	False
24	default_repo_private	False
25	default_repo_type	hg
\.


--
-- Name: rhodecode_settings_app_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('rhodecode_settings_app_settings_id_seq', 25, true);


--
-- Data for Name: rhodecode_ui; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY rhodecode_ui (ui_id, ui_section, ui_key, ui_value, ui_active) FROM stdin;
1	hooks	changegroup.update	hg update >&2	f
2	hooks	changegroup.repo_size	python:rhodecode.lib.hooks.repo_size	t
3	hooks	changegroup.push_logger	python:rhodecode.lib.hooks.log_push_action	t
4	hooks	prechangegroup.pre_push	python:rhodecode.lib.hooks.pre_push	t
5	hooks	outgoing.pull_logger	python:rhodecode.lib.hooks.log_pull_action	t
6	hooks	preoutgoing.pre_pull	python:rhodecode.lib.hooks.pre_pull	t
7	extensions	largefiles		t
8	extensions	hgsubversion		f
9	extensions	hggit		f
10	web	push_ssl	false	t
11	web	allow_archive	gz zip bz2	t
12	web	allow_push	*	t
13	web	baseurl	/	t
14	paths	/	/mnt/hgfs/workspace-python	t
\.


--
-- Name: rhodecode_ui_ui_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('rhodecode_ui_ui_id_seq', 14, true);


--
-- Data for Name: statistics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY statistics (stat_id, repository_id, stat_on_revision, commit_activity, commit_activity_combined, languages) FROM stdin;
\.


--
-- Name: statistics_stat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('statistics_stat_id_seq', 1, false);


--
-- Data for Name: user_email_map; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_email_map (email_id, user_id, email) FROM stdin;
\.


--
-- Name: user_email_map_email_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_email_map_email_id_seq', 1, false);


--
-- Data for Name: user_followings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_followings (user_following_id, user_id, follows_repository_id, follows_user_id, follows_from) FROM stdin;
1	2	1	\N	2013-05-28 20:26:59.905946
2	2	2	\N	2013-05-28 20:26:59.958581
3	2	3	\N	2013-05-28 20:27:00.145566
4	2	4	\N	2013-05-28 20:27:00.184438
5	2	5	\N	2013-05-28 20:27:01.507836
6	2	6	\N	2013-05-28 20:27:01.562696
7	2	7	\N	2013-05-28 20:27:01.630538
8	2	8	\N	2013-05-28 20:27:01.658765
9	2	9	\N	2013-05-28 20:27:01.883077
10	2	10	\N	2013-05-28 20:27:02.410512
11	2	11	\N	2013-05-28 20:27:02.47039
12	2	12	\N	2013-05-28 20:27:02.512861
13	2	13	\N	2013-05-28 20:27:02.705559
14	2	14	\N	2013-05-28 20:27:02.736051
15	2	15	\N	2013-05-28 20:27:02.909458
16	2	16	\N	2013-05-28 20:27:03.058143
17	2	17	\N	2013-05-28 20:27:03.092663
18	2	18	\N	2013-05-28 20:27:03.220556
19	2	19	\N	2013-05-28 20:27:03.401209
20	2	20	\N	2013-05-28 20:27:03.446846
21	2	21	\N	2013-05-28 20:27:03.478718
22	2	22	\N	2013-05-28 20:27:03.625506
23	2	23	\N	2013-05-28 20:27:03.654446
24	2	24	\N	2013-05-28 20:27:03.90204
25	2	25	\N	2013-05-28 20:27:03.935584
26	2	26	\N	2013-05-28 20:27:04.133528
27	2	27	\N	2013-05-28 20:27:04.165426
28	2	28	\N	2013-05-28 20:27:04.227192
29	2	29	\N	2013-05-28 20:27:04.470074
30	2	30	\N	2013-05-28 20:27:04.535036
31	2	31	\N	2013-05-28 20:27:04.56081
32	2	32	\N	2013-05-28 20:27:04.73511
33	2	33	\N	2013-05-28 20:27:04.762367
34	2	34	\N	2013-05-28 20:27:04.882269
35	2	35	\N	2013-05-28 20:27:16.081624
36	2	36	\N	2013-05-28 20:27:16.238074
37	2	37	\N	2013-05-28 20:27:16.490921
38	2	38	\N	2013-05-28 20:27:16.606332
39	2	39	\N	2013-05-28 20:27:16.683877
40	2	40	\N	2013-05-28 20:27:16.772204
41	2	41	\N	2013-05-28 20:27:16.846091
42	2	42	\N	2013-05-28 20:27:16.915625
43	2	43	\N	2013-05-28 20:27:17.000652
44	2	44	\N	2013-05-28 20:27:17.035001
45	2	45	\N	2013-05-28 20:27:17.245544
46	2	46	\N	2013-05-28 20:27:17.412282
47	2	47	\N	2013-05-28 20:27:17.442703
48	2	48	\N	2013-05-28 20:27:17.616299
49	2	49	\N	2013-05-28 20:27:17.694907
50	2	50	\N	2013-05-28 20:27:17.76193
51	2	51	\N	2013-05-28 20:27:17.796316
52	2	52	\N	2013-05-28 20:27:17.911214
53	2	53	\N	2013-05-28 20:27:18.67818
54	2	54	\N	2013-05-28 20:27:18.712023
55	2	55	\N	2013-05-28 20:27:18.837132
56	2	56	\N	2013-05-28 20:27:19.053951
57	2	57	\N	2013-05-28 20:27:19.51609
58	2	58	\N	2013-05-28 20:27:19.543354
59	2	59	\N	2013-05-28 20:27:19.809302
60	2	60	\N	2013-05-28 20:27:19.877469
61	2	61	\N	2013-05-28 20:27:19.908981
62	2	62	\N	2013-05-28 20:27:20.247031
63	2	63	\N	2013-05-28 20:27:20.410876
64	2	64	\N	2013-05-28 20:27:20.506094
65	2	65	\N	2013-05-28 20:27:20.536866
\.


--
-- Name: user_followings_user_following_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_followings_user_following_id_seq', 65, true);


--
-- Data for Name: user_ip_map; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_ip_map (ip_id, user_id, ip_addr, active) FROM stdin;
\.


--
-- Name: user_ip_map_ip_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_ip_map_ip_id_seq', 1, false);


--
-- Data for Name: user_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_logs (user_log_id, user_id, username, repository_id, repository_name, user_ip, action, action_date) FROM stdin;
1	2	marcink	1	RC/mygr/lol		started_following_repo	2013-05-28 20:26:59.900931
2	2	marcink	2	RC/fakeclone		started_following_repo	2013-05-28 20:26:59.955428
3	2	marcink	3	RC/muay		started_following_repo	2013-05-28 20:27:00.125953
4	2	marcink	4	BIG/git		started_following_repo	2013-05-28 20:27:00.181617
5	2	marcink	5	RC/origin-fork		started_following_repo	2013-05-28 20:27:01.466724
6	2	marcink	6	one		started_following_repo	2013-05-28 20:27:01.536732
7	2	marcink	7	rhodecode.bak.1		started_following_repo	2013-05-28 20:27:01.589472
8	2	marcink	8	csa-collins		started_following_repo	2013-05-28 20:27:01.655365
9	2	marcink	9	csa-harmony		started_following_repo	2013-05-28 20:27:01.88057
10	2	marcink	10	RC/ąqweqwe		started_following_repo	2013-05-28 20:27:02.387499
11	2	marcink	11	rhodecode		started_following_repo	2013-05-28 20:27:02.433418
12	2	marcink	12	csa-unity		started_following_repo	2013-05-28 20:27:02.508796
13	2	marcink	13	RC/łęcina		started_following_repo	2013-05-28 20:27:02.674658
14	2	marcink	14	waitress		started_following_repo	2013-05-28 20:27:02.73244
15	2	marcink	15	RC/rc2/test2		started_following_repo	2013-05-28 20:27:02.906659
16	2	marcink	16	RC/origin-fork-fork		started_following_repo	2013-05-28 20:27:03.02717
17	2	marcink	17	RC/rc2/test4		started_following_repo	2013-05-28 20:27:03.090085
18	2	marcink	18	RC/vcs-git		started_following_repo	2013-05-28 20:27:03.218033
19	2	marcink	19	rhodecode-extensions		started_following_repo	2013-05-28 20:27:03.374166
20	2	marcink	20	rhodecode-cli-gist		started_following_repo	2013-05-28 20:27:03.425087
21	2	marcink	21	test.onaut.com		started_following_repo	2013-05-28 20:27:03.473193
22	2	marcink	22	RC/new		started_following_repo	2013-05-28 20:27:03.593153
23	2	marcink	23	csa-aldrin		started_following_repo	2013-05-28 20:27:03.651182
24	2	marcink	24	vcs		started_following_repo	2013-05-28 20:27:03.866907
25	2	marcink	25	csa-prometheus		started_following_repo	2013-05-28 20:27:03.931789
26	2	marcink	26	RC/INRC/trololo		started_following_repo	2013-05-28 20:27:04.108947
27	2	marcink	27	RC/empty-git		started_following_repo	2013-05-28 20:27:04.162816
28	2	marcink	28	csa-salt-states		started_following_repo	2013-05-28 20:27:04.224517
29	2	marcink	29	rhodecode-premium		started_following_repo	2013-05-28 20:27:04.429318
30	2	marcink	30	RC/qweqwe-fork		started_following_repo	2013-05-28 20:27:04.508625
31	2	marcink	31	testrepo-quick		started_following_repo	2013-05-28 20:27:04.558071
32	2	marcink	32	RC/test		started_following_repo	2013-05-28 20:27:04.707963
33	2	marcink	33	remote-salt		started_following_repo	2013-05-28 20:27:04.759601
34	2	marcink	34	BIG/android		started_following_repo	2013-05-28 20:27:04.879601
35	2	marcink	35	DOCS		started_following_repo	2013-05-28 20:27:16.077043
36	2	marcink	36	rhodecode-git		started_following_repo	2013-05-28 20:27:16.235309
37	2	marcink	37	RC/bin-ops		started_following_repo	2013-05-28 20:27:16.474785
38	2	marcink	38	RC/INRC/L2_NEW/lalalal		started_following_repo	2013-05-28 20:27:16.566047
39	2	marcink	39	RC/fork-remote		started_following_repo	2013-05-28 20:27:16.636895
40	2	marcink	40	RC/INRC/L2_NEW/L3/repo_test_move		started_following_repo	2013-05-28 20:27:16.73064
41	2	marcink	41	RC/gogo-fork		started_following_repo	2013-05-28 20:27:16.801352
42	2	marcink	42	quest		started_following_repo	2013-05-28 20:27:16.870218
43	2	marcink	43	RC/foobar		started_following_repo	2013-05-28 20:27:16.94344
44	2	marcink	44	csa-hyperion		started_following_repo	2013-05-28 20:27:17.032368
45	2	marcink	45	RC/git-pull-test		started_following_repo	2013-05-28 20:27:17.242321
46	2	marcink	46	RC/qweqwe-fork2		started_following_repo	2013-05-28 20:27:17.369718
47	2	marcink	47	RC/jap		started_following_repo	2013-05-28 20:27:17.438737
48	2	marcink	48	RC/hg-repo		started_following_repo	2013-05-28 20:27:17.568968
49	2	marcink	49	RC/origin		started_following_repo	2013-05-28 20:27:17.647722
50	2	marcink	50	rhodecode-cli-api		started_following_repo	2013-05-28 20:27:17.720735
51	2	marcink	51	RC/rc2/test3		started_following_repo	2013-05-28 20:27:17.793213
52	2	marcink	52	csa-armstrong		started_following_repo	2013-05-28 20:27:17.908068
53	2	marcink	53	RC/trololo		started_following_repo	2013-05-28 20:27:18.630661
54	2	marcink	54	testrepo-wp		started_following_repo	2013-05-28 20:27:18.707708
55	2	marcink	55	pyramidpypi		started_following_repo	2013-05-28 20:27:18.834547
56	2	marcink	56	salt		started_following_repo	2013-05-28 20:27:19.050625
57	2	marcink	57	RC/lol/haha		started_following_repo	2013-05-28 20:27:19.462058
58	2	marcink	58	csa-io		started_following_repo	2013-05-28 20:27:19.540782
59	2	marcink	59	enc-envelope		started_following_repo	2013-05-28 20:27:19.758453
60	2	marcink	60	RC/gogo2		started_following_repo	2013-05-28 20:27:19.838573
61	2	marcink	61	csa-libcloud		started_following_repo	2013-05-28 20:27:19.904526
62	2	marcink	62	RC/git-test		started_following_repo	2013-05-28 20:27:20.243692
63	2	marcink	63	RC/rc2/test		started_following_repo	2013-05-28 20:27:20.36788
64	2	marcink	64	rhodecode.bak		started_following_repo	2013-05-28 20:27:20.435328
65	2	marcink	65	RC/kiall-nova		started_following_repo	2013-05-28 20:27:20.533474
\.


--
-- Name: user_logs_user_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_logs_user_log_id_seq', 65, true);


--
-- Data for Name: user_repo_group_to_perm; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_repo_group_to_perm (group_to_perm_id, user_id, group_id, permission_id) FROM stdin;
1	1	1	6
2	1	2	6
3	1	3	6
4	1	4	6
5	1	5	6
6	1	6	6
7	1	7	6
8	1	8	6
\.


--
-- Name: user_repo_group_to_perm_group_to_perm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_repo_group_to_perm_group_to_perm_id_seq', 8, true);


--
-- Data for Name: user_to_notification; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_to_notification (user_id, notification_id, read, sent_on) FROM stdin;
\.


--
-- Data for Name: user_to_perm; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_to_perm (user_to_perm_id, user_id, permission_id) FROM stdin;
1	1	15
2	1	11
3	1	13
4	1	2
5	1	6
\.


--
-- Name: user_to_perm_user_to_perm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_to_perm_user_to_perm_id_seq', 5, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users (user_id, username, password, active, admin, firstname, lastname, email, last_login, ldap_dn, api_key, inherit_default_permissions) FROM stdin;
1	default	$2a$10$pgqzrZyjE0YBlVErXftPnu4bMmbkO4BSIPtgPsrEoxM6xBdu.pFyi	t	f	Anonymous	User	anonymous@rhodecode.org	\N	\N	b7e62414df8fe4328b567603d6a409946af4a8f7	t
2	marcink	$2a$10$htEvNjGrB1xEWaXJGrlWee.LB/ZT4.RON.VOfQ9caBSGSLnbHnvz2	t	t	RhodeCode	Admin	marcin@rhodecode.com	\N	\N	1d6f72e5dc6de70d9623f006edb28b8b56b3ebce	t
\.


--
-- Name: users_group_repo_group_to_per_users_group_repo_group_to_per_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_group_repo_group_to_per_users_group_repo_group_to_per_seq', 1, false);


--
-- Data for Name: users_group_repo_group_to_perm; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users_group_repo_group_to_perm (users_group_repo_group_to_perm_id, users_group_id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: users_group_repo_to_perm; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users_group_repo_to_perm (users_group_to_perm_id, users_group_id, permission_id, repository_id) FROM stdin;
\.


--
-- Name: users_group_repo_to_perm_users_group_to_perm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_group_repo_to_perm_users_group_to_perm_id_seq', 1, false);


--
-- Data for Name: users_group_to_perm; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users_group_to_perm (users_group_to_perm_id, users_group_id, permission_id) FROM stdin;
\.


--
-- Name: users_group_to_perm_users_group_to_perm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_group_to_perm_users_group_to_perm_id_seq', 1, false);


--
-- Data for Name: users_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users_groups (users_group_id, users_group_name, users_group_active, users_group_inherit_default_permissions) FROM stdin;
\.


--
-- Data for Name: users_groups_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users_groups_members (users_group_member_id, users_group_id, user_id) FROM stdin;
\.


--
-- Name: users_groups_members_users_group_member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_groups_members_users_group_member_id_seq', 1, false);


--
-- Name: users_groups_users_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_groups_users_group_id_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('users_user_id_seq', 2, true);


--
-- Name: cache_invalidation_cache_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY cache_invalidation
    ADD CONSTRAINT cache_invalidation_cache_key_key UNIQUE (cache_key);


--
-- Name: cache_invalidation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY cache_invalidation
    ADD CONSTRAINT cache_invalidation_pkey PRIMARY KEY (cache_id);


--
-- Name: changeset_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY changeset_comments
    ADD CONSTRAINT changeset_comments_pkey PRIMARY KEY (comment_id);


--
-- Name: changeset_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY changeset_statuses
    ADD CONSTRAINT changeset_statuses_pkey PRIMARY KEY (changeset_status_id);


--
-- Name: changeset_statuses_repo_id_revision_version_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY changeset_statuses
    ADD CONSTRAINT changeset_statuses_repo_id_revision_version_key UNIQUE (repo_id, revision, version);


--
-- Name: db_migrate_version_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY db_migrate_version
    ADD CONSTRAINT db_migrate_version_pkey PRIMARY KEY (repository_id);


--
-- Name: groups_group_name_group_parent_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT groups_group_name_group_parent_id_key UNIQUE (group_name, group_parent_id);


--
-- Name: groups_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT groups_group_name_key UNIQUE (group_name);


--
-- Name: groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (group_id);


--
-- Name: notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (notification_id);


--
-- Name: permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (permission_id);


--
-- Name: pull_request_reviewers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pull_request_reviewers
    ADD CONSTRAINT pull_request_reviewers_pkey PRIMARY KEY (pull_requests_reviewers_id);


--
-- Name: pull_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pull_requests
    ADD CONSTRAINT pull_requests_pkey PRIMARY KEY (pull_request_id);


--
-- Name: repo_to_perm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY repo_to_perm
    ADD CONSTRAINT repo_to_perm_pkey PRIMARY KEY (repo_to_perm_id);


--
-- Name: repo_to_perm_user_id_repository_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY repo_to_perm
    ADD CONSTRAINT repo_to_perm_user_id_repository_id_permission_id_key UNIQUE (user_id, repository_id, permission_id);


--
-- Name: repositories_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY repositories_fields
    ADD CONSTRAINT repositories_fields_pkey PRIMARY KEY (repo_field_id);


--
-- Name: repositories_fields_repository_id_field_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY repositories_fields
    ADD CONSTRAINT repositories_fields_repository_id_field_key_key UNIQUE (repository_id, field_key);


--
-- Name: repositories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY repositories
    ADD CONSTRAINT repositories_pkey PRIMARY KEY (repo_id);


--
-- Name: repositories_repo_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY repositories
    ADD CONSTRAINT repositories_repo_name_key UNIQUE (repo_name);


--
-- Name: rhodecode_settings_app_settings_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rhodecode_settings
    ADD CONSTRAINT rhodecode_settings_app_settings_name_key UNIQUE (app_settings_name);


--
-- Name: rhodecode_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rhodecode_settings
    ADD CONSTRAINT rhodecode_settings_pkey PRIMARY KEY (app_settings_id);


--
-- Name: rhodecode_ui_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rhodecode_ui
    ADD CONSTRAINT rhodecode_ui_pkey PRIMARY KEY (ui_id);


--
-- Name: rhodecode_ui_ui_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rhodecode_ui
    ADD CONSTRAINT rhodecode_ui_ui_key_key UNIQUE (ui_key);


--
-- Name: statistics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY statistics
    ADD CONSTRAINT statistics_pkey PRIMARY KEY (stat_id);


--
-- Name: statistics_repository_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY statistics
    ADD CONSTRAINT statistics_repository_id_key UNIQUE (repository_id);


--
-- Name: user_email_map_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_email_map
    ADD CONSTRAINT user_email_map_email_key UNIQUE (email);


--
-- Name: user_email_map_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_email_map
    ADD CONSTRAINT user_email_map_pkey PRIMARY KEY (email_id);


--
-- Name: user_followings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_followings
    ADD CONSTRAINT user_followings_pkey PRIMARY KEY (user_following_id);


--
-- Name: user_followings_user_id_follows_repository_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_followings
    ADD CONSTRAINT user_followings_user_id_follows_repository_id_key UNIQUE (user_id, follows_repository_id);


--
-- Name: user_followings_user_id_follows_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_followings
    ADD CONSTRAINT user_followings_user_id_follows_user_id_key UNIQUE (user_id, follows_user_id);


--
-- Name: user_ip_map_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_ip_map
    ADD CONSTRAINT user_ip_map_pkey PRIMARY KEY (ip_id);


--
-- Name: user_ip_map_user_id_ip_addr_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_ip_map
    ADD CONSTRAINT user_ip_map_user_id_ip_addr_key UNIQUE (user_id, ip_addr);


--
-- Name: user_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_logs
    ADD CONSTRAINT user_logs_pkey PRIMARY KEY (user_log_id);


--
-- Name: user_repo_group_to_perm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_repo_group_to_perm
    ADD CONSTRAINT user_repo_group_to_perm_pkey PRIMARY KEY (group_to_perm_id);


--
-- Name: user_repo_group_to_perm_user_id_group_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_repo_group_to_perm
    ADD CONSTRAINT user_repo_group_to_perm_user_id_group_id_permission_id_key UNIQUE (user_id, group_id, permission_id);


--
-- Name: user_to_notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_to_notification
    ADD CONSTRAINT user_to_notification_pkey PRIMARY KEY (user_id, notification_id);


--
-- Name: user_to_perm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_to_perm
    ADD CONSTRAINT user_to_perm_pkey PRIMARY KEY (user_to_perm_id);


--
-- Name: user_to_perm_user_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_to_perm
    ADD CONSTRAINT user_to_perm_user_id_permission_id_key UNIQUE (user_id, permission_id);


--
-- Name: users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users_group_repo_group_to_perm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_group_repo_group_to_perm
    ADD CONSTRAINT users_group_repo_group_to_perm_pkey PRIMARY KEY (users_group_repo_group_to_perm_id);


--
-- Name: users_group_repo_group_to_perm_users_group_id_group_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_group_repo_group_to_perm
    ADD CONSTRAINT users_group_repo_group_to_perm_users_group_id_group_id_key UNIQUE (users_group_id, group_id);


--
-- Name: users_group_repo_to_perm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_group_repo_to_perm
    ADD CONSTRAINT users_group_repo_to_perm_pkey PRIMARY KEY (users_group_to_perm_id);


--
-- Name: users_group_repo_to_perm_repository_id_users_group_id_permi_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_group_repo_to_perm
    ADD CONSTRAINT users_group_repo_to_perm_repository_id_users_group_id_permi_key UNIQUE (repository_id, users_group_id, permission_id);


--
-- Name: users_group_to_perm_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_group_to_perm
    ADD CONSTRAINT users_group_to_perm_pkey PRIMARY KEY (users_group_to_perm_id);


--
-- Name: users_group_to_perm_users_group_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_group_to_perm
    ADD CONSTRAINT users_group_to_perm_users_group_id_permission_id_key UNIQUE (users_group_id, permission_id);


--
-- Name: users_groups_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_groups_members
    ADD CONSTRAINT users_groups_members_pkey PRIMARY KEY (users_group_member_id);


--
-- Name: users_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_groups
    ADD CONSTRAINT users_groups_pkey PRIMARY KEY (users_group_id);


--
-- Name: users_groups_users_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users_groups
    ADD CONSTRAINT users_groups_users_group_name_key UNIQUE (users_group_name);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: cc_revision_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX cc_revision_idx ON changeset_comments USING btree (revision);


--
-- Name: cs_revision_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX cs_revision_idx ON changeset_statuses USING btree (revision);


--
-- Name: cs_version_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX cs_version_idx ON changeset_statuses USING btree (version);


--
-- Name: key_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX key_idx ON cache_invalidation USING btree (cache_key);


--
-- Name: notification_type_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX notification_type_idx ON notifications USING btree (type);


--
-- Name: p_perm_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX p_perm_name_idx ON permissions USING btree (permission_name);


--
-- Name: u_email_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX u_email_idx ON users USING btree (email);


--
-- Name: u_username_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX u_username_idx ON users USING btree (username);


--
-- Name: uem_email_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX uem_email_idx ON user_email_map USING btree (email);


--
-- Name: changeset_comments_pull_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_comments
    ADD CONSTRAINT changeset_comments_pull_request_id_fkey FOREIGN KEY (pull_request_id) REFERENCES pull_requests(pull_request_id);


--
-- Name: changeset_comments_repo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_comments
    ADD CONSTRAINT changeset_comments_repo_id_fkey FOREIGN KEY (repo_id) REFERENCES repositories(repo_id);


--
-- Name: changeset_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_comments
    ADD CONSTRAINT changeset_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: changeset_statuses_changeset_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_statuses
    ADD CONSTRAINT changeset_statuses_changeset_comment_id_fkey FOREIGN KEY (changeset_comment_id) REFERENCES changeset_comments(comment_id);


--
-- Name: changeset_statuses_pull_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_statuses
    ADD CONSTRAINT changeset_statuses_pull_request_id_fkey FOREIGN KEY (pull_request_id) REFERENCES pull_requests(pull_request_id);


--
-- Name: changeset_statuses_repo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_statuses
    ADD CONSTRAINT changeset_statuses_repo_id_fkey FOREIGN KEY (repo_id) REFERENCES repositories(repo_id);


--
-- Name: changeset_statuses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY changeset_statuses
    ADD CONSTRAINT changeset_statuses_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: groups_group_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY groups
    ADD CONSTRAINT groups_group_parent_id_fkey FOREIGN KEY (group_parent_id) REFERENCES groups(group_id);


--
-- Name: notifications_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY notifications
    ADD CONSTRAINT notifications_created_by_fkey FOREIGN KEY (created_by) REFERENCES users(user_id);


--
-- Name: pull_request_reviewers_pull_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pull_request_reviewers
    ADD CONSTRAINT pull_request_reviewers_pull_request_id_fkey FOREIGN KEY (pull_request_id) REFERENCES pull_requests(pull_request_id);


--
-- Name: pull_request_reviewers_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pull_request_reviewers
    ADD CONSTRAINT pull_request_reviewers_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: pull_requests_org_repo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pull_requests
    ADD CONSTRAINT pull_requests_org_repo_id_fkey FOREIGN KEY (org_repo_id) REFERENCES repositories(repo_id);


--
-- Name: pull_requests_other_repo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pull_requests
    ADD CONSTRAINT pull_requests_other_repo_id_fkey FOREIGN KEY (other_repo_id) REFERENCES repositories(repo_id);


--
-- Name: pull_requests_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pull_requests
    ADD CONSTRAINT pull_requests_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: repo_to_perm_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repo_to_perm
    ADD CONSTRAINT repo_to_perm_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES permissions(permission_id);


--
-- Name: repo_to_perm_repository_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repo_to_perm
    ADD CONSTRAINT repo_to_perm_repository_id_fkey FOREIGN KEY (repository_id) REFERENCES repositories(repo_id);


--
-- Name: repo_to_perm_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repo_to_perm
    ADD CONSTRAINT repo_to_perm_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: repositories_fields_repository_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repositories_fields
    ADD CONSTRAINT repositories_fields_repository_id_fkey FOREIGN KEY (repository_id) REFERENCES repositories(repo_id);


--
-- Name: repositories_fork_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repositories
    ADD CONSTRAINT repositories_fork_id_fkey FOREIGN KEY (fork_id) REFERENCES repositories(repo_id);


--
-- Name: repositories_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repositories
    ADD CONSTRAINT repositories_group_id_fkey FOREIGN KEY (group_id) REFERENCES groups(group_id);


--
-- Name: repositories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY repositories
    ADD CONSTRAINT repositories_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: statistics_repository_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY statistics
    ADD CONSTRAINT statistics_repository_id_fkey FOREIGN KEY (repository_id) REFERENCES repositories(repo_id);


--
-- Name: user_email_map_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_email_map
    ADD CONSTRAINT user_email_map_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: user_followings_follows_repository_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_followings
    ADD CONSTRAINT user_followings_follows_repository_id_fkey FOREIGN KEY (follows_repository_id) REFERENCES repositories(repo_id);


--
-- Name: user_followings_follows_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_followings
    ADD CONSTRAINT user_followings_follows_user_id_fkey FOREIGN KEY (follows_user_id) REFERENCES users(user_id);


--
-- Name: user_followings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_followings
    ADD CONSTRAINT user_followings_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: user_ip_map_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_ip_map
    ADD CONSTRAINT user_ip_map_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: user_logs_repository_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_logs
    ADD CONSTRAINT user_logs_repository_id_fkey FOREIGN KEY (repository_id) REFERENCES repositories(repo_id);


--
-- Name: user_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_logs
    ADD CONSTRAINT user_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: user_repo_group_to_perm_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_repo_group_to_perm
    ADD CONSTRAINT user_repo_group_to_perm_group_id_fkey FOREIGN KEY (group_id) REFERENCES groups(group_id);


--
-- Name: user_repo_group_to_perm_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_repo_group_to_perm
    ADD CONSTRAINT user_repo_group_to_perm_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES permissions(permission_id);


--
-- Name: user_repo_group_to_perm_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_repo_group_to_perm
    ADD CONSTRAINT user_repo_group_to_perm_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: user_to_notification_notification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_to_notification
    ADD CONSTRAINT user_to_notification_notification_id_fkey FOREIGN KEY (notification_id) REFERENCES notifications(notification_id);


--
-- Name: user_to_notification_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_to_notification
    ADD CONSTRAINT user_to_notification_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: user_to_perm_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_to_perm
    ADD CONSTRAINT user_to_perm_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES permissions(permission_id);


--
-- Name: user_to_perm_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_to_perm
    ADD CONSTRAINT user_to_perm_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: users_group_repo_group_to_perm_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_repo_group_to_perm
    ADD CONSTRAINT users_group_repo_group_to_perm_group_id_fkey FOREIGN KEY (group_id) REFERENCES groups(group_id);


--
-- Name: users_group_repo_group_to_perm_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_repo_group_to_perm
    ADD CONSTRAINT users_group_repo_group_to_perm_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES permissions(permission_id);


--
-- Name: users_group_repo_group_to_perm_users_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_repo_group_to_perm
    ADD CONSTRAINT users_group_repo_group_to_perm_users_group_id_fkey FOREIGN KEY (users_group_id) REFERENCES users_groups(users_group_id);


--
-- Name: users_group_repo_to_perm_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_repo_to_perm
    ADD CONSTRAINT users_group_repo_to_perm_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES permissions(permission_id);


--
-- Name: users_group_repo_to_perm_repository_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_repo_to_perm
    ADD CONSTRAINT users_group_repo_to_perm_repository_id_fkey FOREIGN KEY (repository_id) REFERENCES repositories(repo_id);


--
-- Name: users_group_repo_to_perm_users_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_repo_to_perm
    ADD CONSTRAINT users_group_repo_to_perm_users_group_id_fkey FOREIGN KEY (users_group_id) REFERENCES users_groups(users_group_id);


--
-- Name: users_group_to_perm_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_to_perm
    ADD CONSTRAINT users_group_to_perm_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES permissions(permission_id);


--
-- Name: users_group_to_perm_users_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_group_to_perm
    ADD CONSTRAINT users_group_to_perm_users_group_id_fkey FOREIGN KEY (users_group_id) REFERENCES users_groups(users_group_id);


--
-- Name: users_groups_members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_groups_members
    ADD CONSTRAINT users_groups_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id);


--
-- Name: users_groups_members_users_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users_groups_members
    ADD CONSTRAINT users_groups_members_users_group_id_fkey FOREIGN KEY (users_group_id) REFERENCES users_groups(users_group_id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

