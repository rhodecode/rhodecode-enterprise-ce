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
    fork_id integer,
    group_id integer
);


ALTER TABLE public.repositories OWNER TO postgres;

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
1	1RC/fakeclone	RC/fakeclone	t
2	1RC/muay	RC/muay	f
3	1one	one	f
4	1RC/rc2/test2	RC/rc2/test2	t
5	1RC/rc2/test3	RC/rc2/test3	t
6	1RC/rc2/test4	RC/rc2/test4	t
7	1rhodecode-cli-gist	rhodecode-cli-gist	f
8	1test.onaut.com	test.onaut.com	t
9	1RC/new	RC/new	f
10	1.rc_gist_store/32	.rc_gist_store/32	f
11	1vcs	vcs	f
12	1.rc_gist_store/36	.rc_gist_store/36	f
13	1.rc_gist_store/37	.rc_gist_store/37	f
14	1.rc_gist_store/39	.rc_gist_store/39	f
15	1remote-salt	remote-salt	t
16	1RC/INRC/trololo	RC/INRC/trololo	f
17	1quest	quest	f
18	1csa-hyperion	csa-hyperion	t
19	1rhodecode	rhodecode	f
20	1RC/origin-fork-fork	RC/origin-fork-fork	f
21	1.rc_gist_store/45	.rc_gist_store/45	f
22	1.rc_gist_store/44	.rc_gist_store/44	f
23	1.rc_gist_store/46	.rc_gist_store/46	f
24	1.rc_gist_store/41	.rc_gist_store/41	f
25	1.rc_gist_store/40	.rc_gist_store/40	f
26	1RC/gogo2	RC/gogo2	f
27	1.rc_gist_store/42	.rc_gist_store/42	f
28	1.rc_gist_store/49	.rc_gist_store/49	f
29	1.rc_gist_store/48	.rc_gist_store/48	f
30	1csa-collins	csa-collins	t
31	1.rc_gist_store/54	.rc_gist_store/54	f
32	1.rc_gist_store/55	.rc_gist_store/55	f
33	1.rc_gist_store/52	.rc_gist_store/52	f
34	1.rc_gist_store/53	.rc_gist_store/53	f
35	1.rc_gist_store/50	.rc_gist_store/50	f
36	1.rc_gist_store/51	.rc_gist_store/51	f
37	1rhodecode.bak.1	rhodecode.bak.1	f
38	1BIG/android	BIG/android	t
39	1RC/gogo-fork	RC/gogo-fork	f
40	1RC/mygr/lol	RC/mygr/lol	f
41	1testrepo-wp	testrepo-wp	t
42	1RC/hg-repo	RC/hg-repo	f
43	1testrepo-quick	testrepo-quick	t
44	1RC/bin-ops	RC/bin-ops	f
45	1.rc_gist_store/xFvj6dFqqVK5vfsGP8PU	.rc_gist_store/xFvj6dFqqVK5vfsGP8PU	f
46	1rhodecode-git	rhodecode-git	t
47	1csa-io	csa-io	t
48	1RC/qweqwe-fork	RC/qweqwe-fork	f
49	1csa-libcloud	csa-libcloud	t
50	1waitress	waitress	t
51	1.rc_gist_store/8	.rc_gist_store/8	f
52	1.rc_gist_store/9	.rc_gist_store/9	f
53	1RC/foobar	RC/foobar	f
54	1.rc_gist_store/1	.rc_gist_store/1	f
55	1.rc_gist_store/3	.rc_gist_store/3	f
56	1.rc_gist_store/4	.rc_gist_store/4	f
57	1.rc_gist_store/5	.rc_gist_store/5	f
58	1.rc_gist_store/6	.rc_gist_store/6	f
59	1.rc_gist_store/7	.rc_gist_store/7	f
60	1csa-harmony	csa-harmony	t
61	1RC/łęcina	RC/łęcina	f
62	1rhodecode-extensions	rhodecode-extensions	f
63	1csa-prometheus	csa-prometheus	t
64	1RC/empty-git	RC/empty-git	t
65	1csa-salt-states	csa-salt-states	t
66	1rhodecode-premium	rhodecode-premium	f
67	1RC/qweqwe-fork2	RC/qweqwe-fork2	f
68	1RC/INRC/L2_NEW/lalalal	RC/INRC/L2_NEW/lalalal	f
69	1RC/INRC/L2_NEW/L3/repo_test_move	RC/INRC/L2_NEW/L3/repo_test_move	f
70	1rhodecode.bak	rhodecode.bak	f
71	1RC/jap	RC/jap	t
72	1RC/origin	RC/origin	f
73	1rhodecode-cli-api	rhodecode-cli-api	f
74	1csa-armstrong	csa-armstrong	t
75	1.rc_gist_store/NAsB8cacjxnqdyZ8QUl3	.rc_gist_store/NAsB8cacjxnqdyZ8QUl3	f
76	1RC/lol/haha	RC/lol/haha	f
77	1enc-envelope	enc-envelope	f
78	1.rc_gist_store/43	.rc_gist_store/43	f
79	1RC/test	RC/test	f
80	1BIG/git	BIG/git	t
81	1RC/origin-fork	RC/origin-fork	f
82	1RC/trololo	RC/trololo	f
83	1.rc_gist_store/FLj8GunafFAVBnuTWDxU	.rc_gist_store/FLj8GunafFAVBnuTWDxU	f
84	1RC/ąqweqwe	RC/ąqweqwe	f
85	1csa-unity	csa-unity	t
86	1RC/vcs-git	RC/vcs-git	t
87	1.rc_gist_store/12	.rc_gist_store/12	f
88	1.rc_gist_store/13	.rc_gist_store/13	f
89	1.rc_gist_store/10	.rc_gist_store/10	f
90	1.rc_gist_store/11	.rc_gist_store/11	f
91	1RC/kiall-nova	RC/kiall-nova	t
92	1RC/rc2/test	RC/rc2/test	f
93	1DOCS	DOCS	t
94	1RC/fork-remote	RC/fork-remote	f
95	1RC/git-pull-test	RC/git-pull-test	t
96	1pyramidpypi	pyramidpypi	t
97	1.rc_gist_store/aQpbufbhSac6FyvVHhmS	.rc_gist_store/aQpbufbhSac6FyvVHhmS	f
98	1csa-aldrin	csa-aldrin	t
99	1.rc_gist_store/QL2GhrlKymNmrUJJy5js	.rc_gist_store/QL2GhrlKymNmrUJJy5js	f
100	1RC/git-test	RC/git-test	t
101	1salt	salt	t
\.


--
-- Name: cache_invalidation_cache_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('cache_invalidation_cache_id_seq', 101, true);


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
rhodecode_db_migrations	versions	8
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY groups (group_id, group_name, group_parent_id, group_description, enable_locking) FROM stdin;
1	RC	\N	RC group	f
2	RC/rc2	1	RC/rc2 group	f
3	.rc_gist_store	\N	.rc_gist_store group	f
4	RC/INRC	1	RC/INRC group	f
5	BIG	\N	BIG group	f
6	RC/mygr	1	RC/mygr group	f
7	RC/INRC/L2_NEW	4	RC/INRC/L2_NEW group	f
8	RC/INRC/L2_NEW/L3	7	RC/INRC/L2_NEW/L3 group	f
9	RC/lol	1	RC/lol group	f
\.


--
-- Name: groups_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('groups_group_id_seq', 9, true);


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
66	1	2	66
67	1	2	67
68	1	2	68
69	1	2	69
70	1	2	70
71	1	2	71
72	1	2	72
73	1	2	73
74	1	2	74
75	1	2	75
76	1	2	76
77	1	2	77
78	1	2	78
79	1	2	79
80	1	2	80
81	1	2	81
82	1	2	82
83	1	2	83
84	1	2	84
85	1	2	85
86	1	2	86
87	1	2	87
88	1	2	88
89	1	2	89
90	1	2	90
91	1	2	91
92	1	2	92
93	1	2	93
94	1	2	94
95	1	2	95
96	1	2	96
97	1	2	97
98	1	2	98
99	1	2	99
100	1	2	100
101	1	2	101
\.


--
-- Name: repo_to_perm_repo_to_perm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('repo_to_perm_repo_to_perm_id_seq', 101, true);


--
-- Data for Name: repositories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY repositories (repo_id, repo_name, clone_uri, repo_type, user_id, private, statistics, downloads, description, created_on, updated_on, landing_revision, enable_locking, locked, fork_id, group_id) FROM stdin;
1	RC/fakeclone	http://user@vm/RC/fakeclone	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:07.392436	2013-05-28 20:25:07.39247	tip	f	\N	\N	1
2	RC/muay	\N	hg	2	f	f	f	RC/muay repository	2013-05-28 20:25:07.504925	2013-05-28 20:25:07.504979	tip	f	\N	\N	1
3	one	\N	hg	2	f	f	f	one repository	2013-05-28 20:25:07.536707	2013-05-28 20:25:07.536736	tip	f	\N	\N	\N
4	RC/rc2/test2	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:07.579176	2013-05-28 20:25:07.579209	tip	f	\N	\N	2
5	RC/rc2/test3	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:07.638818	2013-05-28 20:25:07.63884	tip	f	\N	\N	2
6	RC/rc2/test4	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:07.704695	2013-05-28 20:25:07.704732	tip	f	\N	\N	2
7	rhodecode-cli-gist	\N	hg	2	f	f	f	rhodecode-cli-gist repository	2013-05-28 20:25:07.760722	2013-05-28 20:25:07.760749	tip	f	\N	\N	\N
8	test.onaut.com	\N	git	2	f	f	f	Unnamed repository	2013-05-28 20:25:07.788683	2013-05-28 20:25:07.788705	tip	f	\N	\N	\N
9	RC/new	\N	hg	2	f	f	f	RC/new repository	2013-05-28 20:25:07.845443	2013-05-28 20:25:07.845467	tip	f	\N	\N	1
10	.rc_gist_store/32	\N	hg	2	f	f	f	.rc_gist_store/32 repository	2013-05-28 20:25:07.887214	2013-05-28 20:25:07.887238	tip	f	\N	\N	3
11	vcs	\N	hg	2	f	f	f	vcs repository	2013-05-28 20:25:07.913342	2013-05-28 20:25:07.913367	tip	f	\N	\N	\N
12	.rc_gist_store/36	\N	hg	2	f	f	f	.rc_gist_store/36 repository	2013-05-28 20:25:07.943324	2013-05-28 20:25:07.943361	tip	f	\N	\N	3
13	.rc_gist_store/37	\N	hg	2	f	f	f	.rc_gist_store/37 repository	2013-05-28 20:25:07.979896	2013-05-28 20:25:07.979929	tip	f	\N	\N	3
14	.rc_gist_store/39	\N	hg	2	f	f	f	.rc_gist_store/39 repository	2013-05-28 20:25:08.018938	2013-05-28 20:25:08.018965	tip	f	\N	\N	3
15	remote-salt	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:08.047164	2013-05-28 20:25:08.047189	tip	f	\N	\N	\N
16	RC/INRC/trololo	\N	hg	2	f	f	f	RC/INRC/trololo repository	2013-05-28 20:25:08.117849	2013-05-28 20:25:08.117873	tip	f	\N	\N	4
17	quest	\N	hg	2	f	f	f	quest repository	2013-05-28 20:25:08.149575	2013-05-28 20:25:08.149599	tip	f	\N	\N	\N
18	csa-hyperion	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:08.175969	2013-05-28 20:25:08.176001	tip	f	\N	\N	\N
19	rhodecode	\N	hg	2	f	f	f	rhodecode repository	2013-05-28 20:25:08.228453	2013-05-28 20:25:08.228475	tip	f	\N	\N	\N
20	RC/origin-fork-fork	\N	hg	2	f	f	f	RC/origin-fork-fork repository	2013-05-28 20:25:08.25984	2013-05-28 20:25:08.259873	tip	f	\N	\N	1
21	.rc_gist_store/45	\N	hg	2	f	f	f	.rc_gist_store/45 repository	2013-05-28 20:25:08.290796	2013-05-28 20:25:08.290821	tip	f	\N	\N	3
22	.rc_gist_store/44	\N	hg	2	f	f	f	.rc_gist_store/44 repository	2013-05-28 20:25:08.318312	2013-05-28 20:25:08.318334	tip	f	\N	\N	3
23	.rc_gist_store/46	\N	hg	2	f	f	f	.rc_gist_store/46 repository	2013-05-28 20:25:08.349026	2013-05-28 20:25:08.349054	tip	f	\N	\N	3
24	.rc_gist_store/41	\N	hg	2	f	f	f	.rc_gist_store/41 repository	2013-05-28 20:25:08.37987	2013-05-28 20:25:08.379921	tip	f	\N	\N	3
25	.rc_gist_store/40	\N	hg	2	f	f	f	.rc_gist_store/40 repository	2013-05-28 20:25:08.413778	2013-05-28 20:25:08.413809	tip	f	\N	\N	3
26	RC/gogo2	\N	hg	2	f	f	f	RC/gogo2 repository	2013-05-28 20:25:08.455781	2013-05-28 20:25:08.455813	tip	f	\N	\N	1
27	.rc_gist_store/42	\N	hg	2	f	f	f	.rc_gist_store/42 repository	2013-05-28 20:25:08.502679	2013-05-28 20:25:08.502707	tip	f	\N	\N	3
28	.rc_gist_store/49	\N	hg	2	f	f	f	.rc_gist_store/49 repository	2013-05-28 20:25:08.539391	2013-05-28 20:25:08.539419	tip	f	\N	\N	3
29	.rc_gist_store/48	\N	hg	2	f	f	f	.rc_gist_store/48 repository	2013-05-28 20:25:08.568634	2013-05-28 20:25:08.568661	tip	f	\N	\N	3
30	csa-collins	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:08.598715	2013-05-28 20:25:08.59874	tip	f	\N	\N	\N
31	.rc_gist_store/54	\N	hg	2	f	f	f	.rc_gist_store/54 repository	2013-05-28 20:25:08.661033	2013-05-28 20:25:08.66106	tip	f	\N	\N	3
32	.rc_gist_store/55	\N	hg	2	f	f	f	.rc_gist_store/55 repository	2013-05-28 20:25:08.689489	2013-05-28 20:25:08.689512	tip	f	\N	\N	3
33	.rc_gist_store/52	\N	hg	2	f	f	f	.rc_gist_store/52 repository	2013-05-28 20:25:08.716507	2013-05-28 20:25:08.716536	tip	f	\N	\N	3
34	.rc_gist_store/53	\N	hg	2	f	f	f	.rc_gist_store/53 repository	2013-05-28 20:25:08.74462	2013-05-28 20:25:08.744643	tip	f	\N	\N	3
35	.rc_gist_store/50	\N	hg	2	f	f	f	.rc_gist_store/50 repository	2013-05-28 20:25:08.771475	2013-05-28 20:25:08.771498	tip	f	\N	\N	3
36	.rc_gist_store/51	\N	hg	2	f	f	f	.rc_gist_store/51 repository	2013-05-28 20:25:08.804204	2013-05-28 20:25:08.804234	tip	f	\N	\N	3
37	rhodecode.bak.1	\N	hg	2	f	f	f	rhodecode.bak.1 repository	2013-05-28 20:25:08.830393	2013-05-28 20:25:08.830416	tip	f	\N	\N	\N
38	BIG/android	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:08.874702	2013-05-28 20:25:08.874725	tip	f	\N	\N	5
39	RC/gogo-fork	\N	hg	2	f	f	f	RC/gogo-fork repository	2013-05-28 20:25:08.932526	2013-05-28 20:25:08.932559	tip	f	\N	\N	1
40	RC/mygr/lol	\N	hg	2	f	f	f	RC/mygr/lol repository	2013-05-28 20:25:08.97967	2013-05-28 20:25:08.979709	tip	f	\N	\N	6
41	testrepo-wp	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.017161	2013-05-28 20:25:09.017199	tip	f	\N	\N	\N
42	RC/hg-repo	\N	hg	2	f	f	f	RC/hg-repo repository	2013-05-28 20:25:09.080153	2013-05-28 20:25:09.080178	tip	f	\N	\N	1
43	testrepo-quick	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.107095	2013-05-28 20:25:09.107118	tip	f	\N	\N	\N
44	RC/bin-ops	\N	hg	2	f	f	f	RC/bin-ops repository	2013-05-28 20:25:09.165752	2013-05-28 20:25:09.165788	tip	f	\N	\N	1
45	.rc_gist_store/xFvj6dFqqVK5vfsGP8PU	\N	hg	2	f	f	f	.rc_gist_store/xFvj6dFqqVK5vfsGP8PU repository	2013-05-28 20:25:09.195335	2013-05-28 20:25:09.19536	tip	f	\N	\N	3
46	rhodecode-git	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.225975	2013-05-28 20:25:09.225996	tip	f	\N	\N	\N
47	csa-io	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.281133	2013-05-28 20:25:09.281156	tip	f	\N	\N	\N
48	RC/qweqwe-fork	\N	hg	2	f	f	f	RC/qweqwe-fork repository	2013-05-28 20:25:09.342971	2013-05-28 20:25:09.342996	tip	f	\N	\N	1
49	csa-libcloud	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.370819	2013-05-28 20:25:09.370844	tip	f	\N	\N	\N
50	waitress	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.433003	2013-05-28 20:25:09.433038	tip	f	\N	\N	\N
51	.rc_gist_store/8	\N	hg	2	f	f	f	.rc_gist_store/8 repository	2013-05-28 20:25:09.49346	2013-05-28 20:25:09.493492	tip	f	\N	\N	3
52	.rc_gist_store/9	\N	hg	2	f	f	f	.rc_gist_store/9 repository	2013-05-28 20:25:09.533111	2013-05-28 20:25:09.53314	tip	f	\N	\N	3
53	RC/foobar	\N	hg	2	f	f	f	RC/foobar repository	2013-05-28 20:25:09.56286	2013-05-28 20:25:09.562895	tip	f	\N	\N	1
54	.rc_gist_store/1	\N	hg	2	f	f	f	.rc_gist_store/1 repository	2013-05-28 20:25:09.594992	2013-05-28 20:25:09.595017	tip	f	\N	\N	3
55	.rc_gist_store/3	\N	hg	2	f	f	f	.rc_gist_store/3 repository	2013-05-28 20:25:09.625902	2013-05-28 20:25:09.62593	tip	f	\N	\N	3
56	.rc_gist_store/4	\N	hg	2	f	f	f	.rc_gist_store/4 repository	2013-05-28 20:25:09.656929	2013-05-28 20:25:09.656963	tip	f	\N	\N	3
57	.rc_gist_store/5	\N	hg	2	f	f	f	.rc_gist_store/5 repository	2013-05-28 20:25:09.691164	2013-05-28 20:25:09.69119	tip	f	\N	\N	3
58	.rc_gist_store/6	\N	hg	2	f	f	f	.rc_gist_store/6 repository	2013-05-28 20:25:09.722296	2013-05-28 20:25:09.722321	tip	f	\N	\N	3
59	.rc_gist_store/7	\N	hg	2	f	f	f	.rc_gist_store/7 repository	2013-05-28 20:25:09.752556	2013-05-28 20:25:09.752584	tip	f	\N	\N	3
60	csa-harmony	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.781956	2013-05-28 20:25:09.781978	tip	f	\N	\N	\N
61	RC/łęcina	\N	hg	2	f	f	f	RC/łęcina repository	2013-05-28 20:25:09.838047	2013-05-28 20:25:09.83807	tip	f	\N	\N	1
62	rhodecode-extensions	\N	hg	2	f	f	f	rhodecode-extensions repository	2013-05-28 20:25:09.862369	2013-05-28 20:25:09.862395	tip	f	\N	\N	\N
63	csa-prometheus	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.887883	2013-05-28 20:25:09.887905	tip	f	\N	\N	\N
64	RC/empty-git	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:09.947252	2013-05-28 20:25:09.94728	tip	f	\N	\N	1
65	csa-salt-states	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:10.014164	2013-05-28 20:25:10.014188	tip	f	\N	\N	\N
66	rhodecode-premium	\N	hg	2	f	f	f	rhodecode-premium repository	2013-05-28 20:25:10.069134	2013-05-28 20:25:10.069157	tip	f	\N	\N	\N
67	RC/qweqwe-fork2	\N	hg	2	f	f	f	RC/qweqwe-fork2 repository	2013-05-28 20:25:10.101186	2013-05-28 20:25:10.101237	tip	f	\N	\N	1
68	RC/INRC/L2_NEW/lalalal	\N	hg	2	f	f	f	RC/INRC/L2_NEW/lalalal repository	2013-05-28 20:25:10.142571	2013-05-28 20:25:10.142593	tip	f	\N	\N	7
69	RC/INRC/L2_NEW/L3/repo_test_move	\N	hg	2	f	f	f	RC/INRC/L2_NEW/L3/repo_test_move repository	2013-05-28 20:25:10.190116	2013-05-28 20:25:10.190144	tip	f	\N	\N	8
70	rhodecode.bak	\N	hg	2	f	f	f	rhodecode.bak repository	2013-05-28 20:25:10.219036	2013-05-28 20:25:10.219062	tip	f	\N	\N	\N
71	RC/jap	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:10.253039	2013-05-28 20:25:10.253074	tip	f	\N	\N	1
72	RC/origin	\N	hg	2	f	f	f	RC/origin repository	2013-05-28 20:25:10.314832	2013-05-28 20:25:10.314858	tip	f	\N	\N	1
73	rhodecode-cli-api	\N	hg	2	f	f	f	rhodecode-cli-api repository	2013-05-28 20:25:10.340679	2013-05-28 20:25:10.340705	tip	f	\N	\N	\N
74	csa-armstrong	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:10.373473	2013-05-28 20:25:10.373498	tip	f	\N	\N	\N
75	.rc_gist_store/NAsB8cacjxnqdyZ8QUl3	\N	hg	2	f	f	f	.rc_gist_store/NAsB8cacjxnqdyZ8QUl3 repository	2013-05-28 20:25:10.433134	2013-05-28 20:25:10.433157	tip	f	\N	\N	3
76	RC/lol/haha	\N	hg	2	f	f	f	RC/lol/haha repository	2013-05-28 20:25:10.485738	2013-05-28 20:25:10.485774	tip	f	\N	\N	9
77	enc-envelope	\N	hg	2	f	f	f	enc-envelope repository	2013-05-28 20:25:10.522396	2013-05-28 20:25:10.52242	tip	f	\N	\N	\N
78	.rc_gist_store/43	\N	hg	2	f	f	f	.rc_gist_store/43 repository	2013-05-28 20:25:10.55549	2013-05-28 20:25:10.555518	tip	f	\N	\N	3
79	RC/test	\N	hg	2	f	f	f	RC/test repository	2013-05-28 20:25:10.58186	2013-05-28 20:25:10.581884	tip	f	\N	\N	1
80	BIG/git	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:10.613169	2013-05-28 20:25:10.613192	tip	f	\N	\N	5
81	RC/origin-fork	\N	hg	2	f	f	f	RC/origin-fork repository	2013-05-28 20:25:10.66528	2013-05-28 20:25:10.665303	tip	f	\N	\N	1
82	RC/trololo	\N	hg	2	f	f	f	RC/trololo repository	2013-05-28 20:25:10.692546	2013-05-28 20:25:10.692571	tip	f	\N	\N	1
83	.rc_gist_store/FLj8GunafFAVBnuTWDxU	\N	hg	2	f	f	f	.rc_gist_store/FLj8GunafFAVBnuTWDxU repository	2013-05-28 20:25:10.719549	2013-05-28 20:25:10.719575	tip	f	\N	\N	3
84	RC/ąqweqwe	\N	hg	2	f	f	f	RC/ąqweqwe repository	2013-05-28 20:25:10.74739	2013-05-28 20:25:10.747414	tip	f	\N	\N	1
85	csa-unity	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:10.779116	2013-05-28 20:25:10.779141	tip	f	\N	\N	\N
86	RC/vcs-git	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:10.835779	2013-05-28 20:25:10.835804	tip	f	\N	\N	1
87	.rc_gist_store/12	\N	hg	2	f	f	f	.rc_gist_store/12 repository	2013-05-28 20:25:10.893085	2013-05-28 20:25:10.893109	tip	f	\N	\N	3
88	.rc_gist_store/13	\N	hg	2	f	f	f	.rc_gist_store/13 repository	2013-05-28 20:25:10.92266	2013-05-28 20:25:10.922688	tip	f	\N	\N	3
89	.rc_gist_store/10	\N	hg	2	f	f	f	.rc_gist_store/10 repository	2013-05-28 20:25:10.952412	2013-05-28 20:25:10.952444	tip	f	\N	\N	3
90	.rc_gist_store/11	\N	hg	2	f	f	f	.rc_gist_store/11 repository	2013-05-28 20:25:10.991803	2013-05-28 20:25:10.991851	tip	f	\N	\N	3
91	RC/kiall-nova	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:11.027916	2013-05-28 20:25:11.02794	tip	f	\N	\N	1
92	RC/rc2/test	\N	hg	2	f	f	f	RC/rc2/test repository	2013-05-28 20:25:11.082308	2013-05-28 20:25:11.082331	tip	f	\N	\N	2
93	DOCS	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:11.109114	2013-05-28 20:25:11.109139	tip	f	\N	\N	\N
94	RC/fork-remote	\N	hg	2	f	f	f	RC/fork-remote repository	2013-05-28 20:25:11.16158	2013-05-28 20:25:11.161605	tip	f	\N	\N	1
95	RC/git-pull-test	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:11.195729	2013-05-28 20:25:11.195753	tip	f	\N	\N	1
96	pyramidpypi	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:11.247897	2013-05-28 20:25:11.247919	tip	f	\N	\N	\N
97	.rc_gist_store/aQpbufbhSac6FyvVHhmS	\N	hg	2	f	f	f	.rc_gist_store/aQpbufbhSac6FyvVHhmS repository	2013-05-28 20:25:11.304386	2013-05-28 20:25:11.304416	tip	f	\N	\N	3
98	csa-aldrin	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:11.334081	2013-05-28 20:25:11.334104	tip	f	\N	\N	\N
99	.rc_gist_store/QL2GhrlKymNmrUJJy5js	\N	hg	2	f	f	f	.rc_gist_store/QL2GhrlKymNmrUJJy5js repository	2013-05-28 20:25:11.392571	2013-05-28 20:25:11.392603	tip	f	\N	\N	3
100	RC/git-test	\N	git	2	f	f	f	Unnamed repository	2013-05-28 20:25:11.422773	2013-05-28 20:25:11.422798	tip	f	\N	\N	1
101	salt	\N	git	2	f	f	f	Unnamed repository; edit this file 'description' to name the repository.\n	2013-05-28 20:25:11.491206	2013-05-28 20:25:11.491244	tip	f	\N	\N	\N
\.


--
-- Name: repositories_repo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('repositories_repo_id_seq', 101, true);


--
-- Data for Name: rhodecode_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY rhodecode_settings (app_settings_id, app_settings_name, app_settings_value) FROM stdin;
1	realm	RhodeCode authentication
2	title	RhodeCode
3	ga_code	
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
1	2	1	\N	2013-05-28 20:25:07.419366
2	2	2	\N	2013-05-28 20:25:07.523213
3	2	3	\N	2013-05-28 20:25:07.551071
4	2	4	\N	2013-05-28 20:25:07.593417
5	2	5	\N	2013-05-28 20:25:07.652097
6	2	6	\N	2013-05-28 20:25:07.718865
7	2	7	\N	2013-05-28 20:25:07.775955
8	2	8	\N	2013-05-28 20:25:07.802067
9	2	9	\N	2013-05-28 20:25:07.85919
10	2	10	\N	2013-05-28 20:25:07.898708
11	2	11	\N	2013-05-28 20:25:07.928087
12	2	12	\N	2013-05-28 20:25:07.958332
13	2	13	\N	2013-05-28 20:25:07.999131
14	2	14	\N	2013-05-28 20:25:08.03233
15	2	15	\N	2013-05-28 20:25:08.062772
16	2	16	\N	2013-05-28 20:25:08.133488
17	2	17	\N	2013-05-28 20:25:08.16114
18	2	18	\N	2013-05-28 20:25:08.190194
19	2	19	\N	2013-05-28 20:25:08.243763
20	2	20	\N	2013-05-28 20:25:08.276008
21	2	21	\N	2013-05-28 20:25:08.302919
22	2	22	\N	2013-05-28 20:25:08.333401
23	2	23	\N	2013-05-28 20:25:08.364937
24	2	24	\N	2013-05-28 20:25:08.396443
25	2	25	\N	2013-05-28 20:25:08.432066
26	2	26	\N	2013-05-28 20:25:08.475434
27	2	27	\N	2013-05-28 20:25:08.519422
28	2	28	\N	2013-05-28 20:25:08.554142
29	2	29	\N	2013-05-28 20:25:08.582317
30	2	30	\N	2013-05-28 20:25:08.614023
31	2	31	\N	2013-05-28 20:25:08.674443
32	2	32	\N	2013-05-28 20:25:08.702086
33	2	33	\N	2013-05-28 20:25:08.730009
34	2	34	\N	2013-05-28 20:25:08.75688
35	2	35	\N	2013-05-28 20:25:08.785569
36	2	36	\N	2013-05-28 20:25:08.81867
37	2	37	\N	2013-05-28 20:25:08.845372
38	2	38	\N	2013-05-28 20:25:08.887009
39	2	39	\N	2013-05-28 20:25:08.94708
40	2	40	\N	2013-05-28 20:25:08.997848
41	2	41	\N	2013-05-28 20:25:09.03424
42	2	42	\N	2013-05-28 20:25:09.091839
43	2	43	\N	2013-05-28 20:25:09.121068
44	2	44	\N	2013-05-28 20:25:09.177967
45	2	45	\N	2013-05-28 20:25:09.210977
46	2	46	\N	2013-05-28 20:25:09.237728
47	2	47	\N	2013-05-28 20:25:09.297594
48	2	48	\N	2013-05-28 20:25:09.354276
49	2	49	\N	2013-05-28 20:25:09.387242
50	2	50	\N	2013-05-28 20:25:09.447636
51	2	51	\N	2013-05-28 20:25:09.513617
52	2	52	\N	2013-05-28 20:25:09.545837
53	2	53	\N	2013-05-28 20:25:09.577221
54	2	54	\N	2013-05-28 20:25:09.606831
55	2	55	\N	2013-05-28 20:25:09.641289
56	2	56	\N	2013-05-28 20:25:09.673187
57	2	57	\N	2013-05-28 20:25:09.703041
58	2	58	\N	2013-05-28 20:25:09.737676
59	2	59	\N	2013-05-28 20:25:09.767992
60	2	60	\N	2013-05-28 20:25:09.795625
61	2	61	\N	2013-05-28 20:25:09.849362
62	2	62	\N	2013-05-28 20:25:09.875072
63	2	63	\N	2013-05-28 20:25:09.899962
64	2	64	\N	2013-05-28 20:25:09.959371
65	2	65	\N	2013-05-28 20:25:10.027104
66	2	66	\N	2013-05-28 20:25:10.085728
67	2	67	\N	2013-05-28 20:25:10.113237
68	2	68	\N	2013-05-28 20:25:10.153369
69	2	69	\N	2013-05-28 20:25:10.202414
70	2	70	\N	2013-05-28 20:25:10.231925
71	2	71	\N	2013-05-28 20:25:10.272999
72	2	72	\N	2013-05-28 20:25:10.325972
73	2	73	\N	2013-05-28 20:25:10.357303
74	2	74	\N	2013-05-28 20:25:10.386804
75	2	75	\N	2013-05-28 20:25:10.445843
76	2	76	\N	2013-05-28 20:25:10.505361
77	2	77	\N	2013-05-28 20:25:10.534813
78	2	78	\N	2013-05-28 20:25:10.567787
79	2	79	\N	2013-05-28 20:25:10.594885
80	2	80	\N	2013-05-28 20:25:10.625153
81	2	81	\N	2013-05-28 20:25:10.676514
82	2	82	\N	2013-05-28 20:25:10.704862
83	2	83	\N	2013-05-28 20:25:10.732891
84	2	84	\N	2013-05-28 20:25:10.761585
85	2	85	\N	2013-05-28 20:25:10.794418
86	2	86	\N	2013-05-28 20:25:10.849868
87	2	87	\N	2013-05-28 20:25:10.905233
88	2	88	\N	2013-05-28 20:25:10.935564
89	2	89	\N	2013-05-28 20:25:10.965226
90	2	90	\N	2013-05-28 20:25:11.011674
91	2	91	\N	2013-05-28 20:25:11.039829
92	2	92	\N	2013-05-28 20:25:11.094952
93	2	93	\N	2013-05-28 20:25:11.121706
94	2	94	\N	2013-05-28 20:25:11.176407
95	2	95	\N	2013-05-28 20:25:11.20814
96	2	96	\N	2013-05-28 20:25:11.260602
97	2	97	\N	2013-05-28 20:25:11.316663
98	2	98	\N	2013-05-28 20:25:11.34702
99	2	99	\N	2013-05-28 20:25:11.405701
100	2	100	\N	2013-05-28 20:25:11.437031
101	2	101	\N	2013-05-28 20:25:11.508609
\.


--
-- Name: user_followings_user_following_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_followings_user_following_id_seq', 101, true);


--
-- Data for Name: user_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_logs (user_log_id, user_id, username, repository_id, repository_name, user_ip, action, action_date) FROM stdin;
1	2	marcink	1	RC/fakeclone		started_following_repo	2013-05-28 20:25:07.413172
2	2	marcink	2	RC/muay		started_following_repo	2013-05-28 20:25:07.520161
3	2	marcink	3	one		started_following_repo	2013-05-28 20:25:07.548707
4	2	marcink	4	RC/rc2/test2		started_following_repo	2013-05-28 20:25:07.591048
5	2	marcink	5	RC/rc2/test3		started_following_repo	2013-05-28 20:25:07.648472
6	2	marcink	6	RC/rc2/test4		started_following_repo	2013-05-28 20:25:07.715291
7	2	marcink	7	rhodecode-cli-gist		started_following_repo	2013-05-28 20:25:07.773926
8	2	marcink	8	test.onaut.com		started_following_repo	2013-05-28 20:25:07.798491
9	2	marcink	9	RC/new		started_following_repo	2013-05-28 20:25:07.856745
10	2	marcink	10	.rc_gist_store/32		started_following_repo	2013-05-28 20:25:07.896778
11	2	marcink	11	vcs		started_following_repo	2013-05-28 20:25:07.925912
12	2	marcink	12	.rc_gist_store/36		started_following_repo	2013-05-28 20:25:07.956523
13	2	marcink	13	.rc_gist_store/37		started_following_repo	2013-05-28 20:25:07.996439
14	2	marcink	14	.rc_gist_store/39		started_following_repo	2013-05-28 20:25:08.030537
15	2	marcink	15	remote-salt		started_following_repo	2013-05-28 20:25:08.059837
16	2	marcink	16	RC/INRC/trololo		started_following_repo	2013-05-28 20:25:08.130912
17	2	marcink	17	quest		started_following_repo	2013-05-28 20:25:08.159419
18	2	marcink	18	csa-hyperion		started_following_repo	2013-05-28 20:25:08.187182
19	2	marcink	19	rhodecode		started_following_repo	2013-05-28 20:25:08.241777
20	2	marcink	20	RC/origin-fork-fork		started_following_repo	2013-05-28 20:25:08.272993
21	2	marcink	21	.rc_gist_store/45		started_following_repo	2013-05-28 20:25:08.300966
22	2	marcink	22	.rc_gist_store/44		started_following_repo	2013-05-28 20:25:08.33152
23	2	marcink	23	.rc_gist_store/46		started_following_repo	2013-05-28 20:25:08.36291
24	2	marcink	24	.rc_gist_store/41		started_following_repo	2013-05-28 20:25:08.394552
25	2	marcink	25	.rc_gist_store/40		started_following_repo	2013-05-28 20:25:08.42548
26	2	marcink	26	RC/gogo2		started_following_repo	2013-05-28 20:25:08.471727
27	2	marcink	27	.rc_gist_store/42		started_following_repo	2013-05-28 20:25:08.517494
28	2	marcink	28	.rc_gist_store/49		started_following_repo	2013-05-28 20:25:08.552265
29	2	marcink	29	.rc_gist_store/48		started_following_repo	2013-05-28 20:25:08.580457
30	2	marcink	30	csa-collins		started_following_repo	2013-05-28 20:25:08.610418
31	2	marcink	31	.rc_gist_store/54		started_following_repo	2013-05-28 20:25:08.672441
32	2	marcink	32	.rc_gist_store/55		started_following_repo	2013-05-28 20:25:08.700234
33	2	marcink	33	.rc_gist_store/52		started_following_repo	2013-05-28 20:25:08.727752
34	2	marcink	34	.rc_gist_store/53		started_following_repo	2013-05-28 20:25:08.75499
35	2	marcink	35	.rc_gist_store/50		started_following_repo	2013-05-28 20:25:08.783835
36	2	marcink	36	.rc_gist_store/51		started_following_repo	2013-05-28 20:25:08.816881
37	2	marcink	37	rhodecode.bak.1		started_following_repo	2013-05-28 20:25:08.842944
38	2	marcink	38	BIG/android		started_following_repo	2013-05-28 20:25:08.884294
39	2	marcink	39	RC/gogo-fork		started_following_repo	2013-05-28 20:25:08.944917
40	2	marcink	40	RC/mygr/lol		started_following_repo	2013-05-28 20:25:08.99476
41	2	marcink	41	testrepo-wp		started_following_repo	2013-05-28 20:25:09.030696
42	2	marcink	42	RC/hg-repo		started_following_repo	2013-05-28 20:25:09.089719
43	2	marcink	43	testrepo-quick		started_following_repo	2013-05-28 20:25:09.118511
44	2	marcink	44	RC/bin-ops		started_following_repo	2013-05-28 20:25:09.17613
45	2	marcink	45	.rc_gist_store/xFvj6dFqqVK5vfsGP8PU		started_following_repo	2013-05-28 20:25:09.208613
46	2	marcink	46	rhodecode-git		started_following_repo	2013-05-28 20:25:09.235248
47	2	marcink	47	csa-io		started_following_repo	2013-05-28 20:25:09.294126
48	2	marcink	48	RC/qweqwe-fork		started_following_repo	2013-05-28 20:25:09.352407
49	2	marcink	49	csa-libcloud		started_following_repo	2013-05-28 20:25:09.384157
50	2	marcink	50	waitress		started_following_repo	2013-05-28 20:25:09.443826
51	2	marcink	51	.rc_gist_store/8		started_following_repo	2013-05-28 20:25:09.511525
52	2	marcink	52	.rc_gist_store/9		started_following_repo	2013-05-28 20:25:09.543993
53	2	marcink	53	RC/foobar		started_following_repo	2013-05-28 20:25:09.574874
54	2	marcink	54	.rc_gist_store/1		started_following_repo	2013-05-28 20:25:09.605025
55	2	marcink	55	.rc_gist_store/3		started_following_repo	2013-05-28 20:25:09.639417
56	2	marcink	56	.rc_gist_store/4		started_following_repo	2013-05-28 20:25:09.671288
57	2	marcink	57	.rc_gist_store/5		started_following_repo	2013-05-28 20:25:09.70115
58	2	marcink	58	.rc_gist_store/6		started_following_repo	2013-05-28 20:25:09.735455
59	2	marcink	59	.rc_gist_store/7		started_following_repo	2013-05-28 20:25:09.765397
60	2	marcink	60	csa-harmony		started_following_repo	2013-05-28 20:25:09.792266
61	2	marcink	61	RC/łęcina		started_following_repo	2013-05-28 20:25:09.847716
62	2	marcink	62	rhodecode-extensions		started_following_repo	2013-05-28 20:25:09.873349
63	2	marcink	63	csa-prometheus		started_following_repo	2013-05-28 20:25:09.897434
64	2	marcink	64	RC/empty-git		started_following_repo	2013-05-28 20:25:09.956588
65	2	marcink	65	csa-salt-states		started_following_repo	2013-05-28 20:25:10.023676
66	2	marcink	66	rhodecode-premium		started_following_repo	2013-05-28 20:25:10.083925
67	2	marcink	67	RC/qweqwe-fork2		started_following_repo	2013-05-28 20:25:10.11151
68	2	marcink	68	RC/INRC/L2_NEW/lalalal		started_following_repo	2013-05-28 20:25:10.151677
69	2	marcink	69	RC/INRC/L2_NEW/L3/repo_test_move		started_following_repo	2013-05-28 20:25:10.200478
70	2	marcink	70	rhodecode.bak		started_following_repo	2013-05-28 20:25:10.229049
71	2	marcink	71	RC/jap		started_following_repo	2013-05-28 20:25:10.269933
72	2	marcink	72	RC/origin		started_following_repo	2013-05-28 20:25:10.324135
73	2	marcink	73	rhodecode-cli-api		started_following_repo	2013-05-28 20:25:10.354684
74	2	marcink	74	csa-armstrong		started_following_repo	2013-05-28 20:25:10.384192
75	2	marcink	75	.rc_gist_store/NAsB8cacjxnqdyZ8QUl3		started_following_repo	2013-05-28 20:25:10.444031
76	2	marcink	76	RC/lol/haha		started_following_repo	2013-05-28 20:25:10.501665
77	2	marcink	77	enc-envelope		started_following_repo	2013-05-28 20:25:10.532521
78	2	marcink	78	.rc_gist_store/43		started_following_repo	2013-05-28 20:25:10.565719
79	2	marcink	79	RC/test		started_following_repo	2013-05-28 20:25:10.592427
80	2	marcink	80	BIG/git		started_following_repo	2013-05-28 20:25:10.622609
81	2	marcink	81	RC/origin-fork		started_following_repo	2013-05-28 20:25:10.674818
82	2	marcink	82	RC/trololo		started_following_repo	2013-05-28 20:25:10.70267
83	2	marcink	83	.rc_gist_store/FLj8GunafFAVBnuTWDxU		started_following_repo	2013-05-28 20:25:10.730417
84	2	marcink	84	RC/ąqweqwe		started_following_repo	2013-05-28 20:25:10.759771
85	2	marcink	85	csa-unity		started_following_repo	2013-05-28 20:25:10.791604
86	2	marcink	86	RC/vcs-git		started_following_repo	2013-05-28 20:25:10.847105
87	2	marcink	87	.rc_gist_store/12		started_following_repo	2013-05-28 20:25:10.903299
88	2	marcink	88	.rc_gist_store/13		started_following_repo	2013-05-28 20:25:10.93383
89	2	marcink	89	.rc_gist_store/10		started_following_repo	2013-05-28 20:25:10.963388
90	2	marcink	90	.rc_gist_store/11		started_following_repo	2013-05-28 20:25:11.009722
91	2	marcink	91	RC/kiall-nova		started_following_repo	2013-05-28 20:25:11.037156
92	2	marcink	92	RC/rc2/test		started_following_repo	2013-05-28 20:25:11.092773
93	2	marcink	93	DOCS		started_following_repo	2013-05-28 20:25:11.119232
94	2	marcink	94	RC/fork-remote		started_following_repo	2013-05-28 20:25:11.173979
95	2	marcink	95	RC/git-pull-test		started_following_repo	2013-05-28 20:25:11.205569
96	2	marcink	96	pyramidpypi		started_following_repo	2013-05-28 20:25:11.257363
97	2	marcink	97	.rc_gist_store/aQpbufbhSac6FyvVHhmS		started_following_repo	2013-05-28 20:25:11.315047
98	2	marcink	98	csa-aldrin		started_following_repo	2013-05-28 20:25:11.344453
99	2	marcink	99	.rc_gist_store/QL2GhrlKymNmrUJJy5js		started_following_repo	2013-05-28 20:25:11.403828
100	2	marcink	100	RC/git-test		started_following_repo	2013-05-28 20:25:11.433792
101	2	marcink	101	salt		started_following_repo	2013-05-28 20:25:11.505324
\.


--
-- Name: user_logs_user_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_logs_user_log_id_seq', 101, true);


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
9	1	9	6
\.


--
-- Name: user_repo_group_to_perm_group_to_perm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('user_repo_group_to_perm_group_to_perm_id_seq', 9, true);


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
1	default	$2a$10$g6.8mU0wOOc7Srb76XAueumBDyxC0UdrFxW2RJSqR4B7kM616HRm.	t	f	Anonymous	User	anonymous@rhodecode.org	\N	\N	0b73aec3eb88ec4b25dbb00f8126468b5f984022	t
2	marcink	$2a$10$hNQ1Nk0duJbBG8HBqni7Q.HEaH5SWDW.H5fvEv2K4Ikk6wJFMkDeq	t	t	RhodeCode	Admin	marcin@rhodoecode.com	\N	\N	868d314f51262eb43c3c44569e8fa674299ad5a5	t
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
-- Name: r_repo_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX r_repo_name_idx ON repositories USING btree (repo_name);


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

