--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13 (Homebrew)
-- Dumped by pg_dump version 15.13 (Homebrew)

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

--
-- Name: accounttypeenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.accounttypeenum AS ENUM (
    'ASSET',
    'LIABILITY',
    'EQUITY',
    'REVENUE',
    'EXPENSE'
);


ALTER TYPE public.accounttypeenum OWNER TO "user";

--
-- Name: attendancestatus; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.attendancestatus AS ENUM (
    'PRESENT',
    'ABSENT',
    'LATE',
    'HALF_DAY',
    'OVERTIME'
);


ALTER TYPE public.attendancestatus OWNER TO "user";

--
-- Name: cashboxtypeenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.cashboxtypeenum AS ENUM (
    'SALESPERSON',
    'BRANCH',
    'MAIN',
    'PETTY_CASH'
);


ALTER TYPE public.cashboxtypeenum OWNER TO "user";

--
-- Name: cashpaymentmethodenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.cashpaymentmethodenum AS ENUM (
    'CASH',
    'DIGITAL',
    'BANK_TRANSFER',
    'CHECK'
);


ALTER TYPE public.cashpaymentmethodenum OWNER TO "user";

--
-- Name: currencyenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.currencyenum AS ENUM (
    'IQD',
    'USD',
    'RMB'
);


ALTER TYPE public.currencyenum OWNER TO "user";

--
-- Name: employmentstatus; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.employmentstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'TERMINATED',
    'ON_LEAVE'
);


ALTER TYPE public.employmentstatus OWNER TO "user";

--
-- Name: expensecategoryenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.expensecategoryenum AS ENUM (
    'OFFICE_SUPPLIES',
    'TRAVEL',
    'UTILITIES',
    'RENT',
    'INSURANCE',
    'MAINTENANCE',
    'MARKETING',
    'TRAINING',
    'MEALS',
    'TRANSPORTATION',
    'SOFTWARE',
    'EQUIPMENT',
    'CONSULTING',
    'OTHER'
);


ALTER TYPE public.expensecategoryenum OWNER TO "user";

--
-- Name: expensepaymentmethodenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.expensepaymentmethodenum AS ENUM (
    'CASH',
    'BANK_TRANSFER',
    'CREDIT_CARD',
    'CHECK',
    'PETTY_CASH'
);


ALTER TYPE public.expensepaymentmethodenum OWNER TO "user";

--
-- Name: expensestatusenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.expensestatusenum AS ENUM (
    'DRAFT',
    'PENDING',
    'APPROVED',
    'PAID',
    'REJECTED',
    'CANCELLED'
);


ALTER TYPE public.expensestatusenum OWNER TO "user";

--
-- Name: invoicestatusenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.invoicestatusenum AS ENUM (
    'DRAFT',
    'PENDING',
    'PAID',
    'PARTIALLY_PAID',
    'OVERDUE',
    'CANCELLED',
    'REFUNDED'
);


ALTER TYPE public.invoicestatusenum OWNER TO "user";

--
-- Name: invoicetypeenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.invoicetypeenum AS ENUM (
    'SALES',
    'PURCHASE',
    'CREDIT_NOTE',
    'DEBIT_NOTE'
);


ALTER TYPE public.invoicetypeenum OWNER TO "user";

--
-- Name: journaltypeenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.journaltypeenum AS ENUM (
    'GENERAL',
    'SALES',
    'PURCHASE',
    'CASH',
    'BANK'
);


ALTER TYPE public.journaltypeenum OWNER TO "user";

--
-- Name: leavestatus; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.leavestatus AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'CANCELLED'
);


ALTER TYPE public.leavestatus OWNER TO "user";

--
-- Name: leavetype; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.leavetype AS ENUM (
    'ANNUAL',
    'SICK',
    'MATERNITY',
    'PATERNITY',
    'EMERGENCY',
    'UNPAID'
);


ALTER TYPE public.leavetype OWNER TO "user";

--
-- Name: migrationstatusenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.migrationstatusenum AS ENUM (
    'PENDING',
    'IN_PROGRESS',
    'COMPLETED',
    'FAILED',
    'REQUIRES_REVIEW'
);


ALTER TYPE public.migrationstatusenum OWNER TO "user";

--
-- Name: paymentmethodenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.paymentmethodenum AS ENUM (
    'CASH',
    'CARD',
    'MOBILE',
    'CREDIT',
    'VOUCHER'
);


ALTER TYPE public.paymentmethodenum OWNER TO "user";

--
-- Name: paymenttermsenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.paymenttermsenum AS ENUM (
    'IMMEDIATE',
    'NET_7',
    'NET_15',
    'NET_30',
    'NET_60',
    'NET_90',
    'CUSTOM'
);


ALTER TYPE public.paymenttermsenum OWNER TO "user";

--
-- Name: payrollstatus; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.payrollstatus AS ENUM (
    'PENDING',
    'PROCESSED',
    'PAID',
    'CANCELLED'
);


ALTER TYPE public.payrollstatus OWNER TO "user";

--
-- Name: possessionstatusenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.possessionstatusenum AS ENUM (
    'OPEN',
    'CLOSED',
    'SUSPENDED'
);


ALTER TYPE public.possessionstatusenum OWNER TO "user";

--
-- Name: postransactiontypeenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.postransactiontypeenum AS ENUM (
    'SALE',
    'REFUND',
    'EXCHANGE',
    'VOID'
);


ALTER TYPE public.postransactiontypeenum OWNER TO "user";

--
-- Name: regionenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.regionenum AS ENUM (
    'KARBALA',
    'NAJAF',
    'BABEL',
    'BAGHDAD',
    'BASRA',
    'MOSUL',
    'ERBIL',
    'DUHOK',
    'SULAYMANIYAH',
    'KIRKUK',
    'ANBAR',
    'DIYALA',
    'SALAHUDDIN',
    'WASIT',
    'QADISIYYAH',
    'MUTHANNA',
    'DHI_QAR',
    'MAYSAN'
);


ALTER TYPE public.regionenum OWNER TO "user";

--
-- Name: transactionstatusenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.transactionstatusenum AS ENUM (
    'DRAFT',
    'POSTED',
    'CANCELLED'
);


ALTER TYPE public.transactionstatusenum OWNER TO "user";

--
-- Name: transferstatusenum; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.transferstatusenum AS ENUM (
    'PENDING',
    'APPROVED',
    'RECEIVED',
    'REJECTED',
    'CANCELLED'
);


ALTER TYPE public.transferstatusenum OWNER TO "user";

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounting_periods; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.accounting_periods (
    id integer NOT NULL,
    fiscal_year_id integer NOT NULL,
    name_ar character varying(100) NOT NULL,
    name_en character varying(100) NOT NULL,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    is_closed boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.accounting_periods OWNER TO "user";

--
-- Name: accounting_periods_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.accounting_periods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.accounting_periods_id_seq OWNER TO "user";

--
-- Name: accounting_periods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.accounting_periods_id_seq OWNED BY public.accounting_periods.id;


--
-- Name: accounts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.accounts (
    id integer NOT NULL,
    chart_account_id integer NOT NULL,
    currency_id integer NOT NULL,
    branch_id integer,
    balance_debit numeric(15,2) NOT NULL,
    balance_credit numeric(15,2) NOT NULL,
    balance numeric(15,2) NOT NULL,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.accounts OWNER TO "user";

--
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.accounts_id_seq OWNER TO "user";

--
-- Name: accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;


--
-- Name: ai_conversation_messages; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.ai_conversation_messages (
    id integer NOT NULL,
    conversation_id integer,
    message_content text NOT NULL,
    message_type character varying,
    language character varying,
    platform character varying,
    is_from_customer boolean,
    intent character varying,
    confidence_score numeric(5,2),
    created_at timestamp without time zone
);


ALTER TABLE public.ai_conversation_messages OWNER TO "user";

--
-- Name: ai_conversation_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.ai_conversation_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_conversation_messages_id_seq OWNER TO "user";

--
-- Name: ai_conversation_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.ai_conversation_messages_id_seq OWNED BY public.ai_conversation_messages.id;


--
-- Name: ai_conversations; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.ai_conversations (
    id integer NOT NULL,
    customer_id integer,
    customer_phone character varying NOT NULL,
    status character varying,
    created_at timestamp without time zone,
    last_activity timestamp without time zone,
    message_count integer,
    escalated_at timestamp without time zone,
    escalated_reason text
);


ALTER TABLE public.ai_conversations OWNER TO "user";

--
-- Name: ai_conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.ai_conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_conversations_id_seq OWNER TO "user";

--
-- Name: ai_conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.ai_conversations_id_seq OWNED BY public.ai_conversations.id;


--
-- Name: ai_generated_orders; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.ai_generated_orders (
    id integer NOT NULL,
    order_number character varying,
    customer_id integer,
    customer_phone character varying NOT NULL,
    total_amount numeric(15,2),
    delivery_address text,
    payment_method character varying,
    order_items json,
    language character varying,
    notes text,
    status character varying,
    confirmed_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.ai_generated_orders OWNER TO "user";

--
-- Name: ai_generated_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.ai_generated_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_generated_orders_id_seq OWNER TO "user";

--
-- Name: ai_generated_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.ai_generated_orders_id_seq OWNED BY public.ai_generated_orders.id;


--
-- Name: ai_support_tickets; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.ai_support_tickets (
    id integer NOT NULL,
    ticket_number character varying,
    customer_id integer,
    issue_type character varying NOT NULL,
    description text,
    priority character varying,
    language character varying,
    status character varying,
    assigned_to integer,
    resolved_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.ai_support_tickets OWNER TO "user";

--
-- Name: ai_support_tickets_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.ai_support_tickets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_support_tickets_id_seq OWNER TO "user";

--
-- Name: ai_support_tickets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.ai_support_tickets_id_seq OWNED BY public.ai_support_tickets.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO "user";

--
-- Name: attendance_records; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.attendance_records (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    date date NOT NULL,
    check_in_time timestamp without time zone,
    check_out_time timestamp without time zone,
    check_in_latitude double precision,
    check_in_longitude double precision,
    check_out_latitude double precision,
    check_out_longitude double precision,
    check_in_location character varying(200),
    check_out_location character varying(200),
    total_hours double precision,
    regular_hours double precision,
    overtime_hours double precision,
    status public.attendancestatus NOT NULL,
    is_late boolean,
    late_minutes integer,
    notes text,
    manager_notes text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.attendance_records OWNER TO "user";

--
-- Name: attendance_records_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.attendance_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.attendance_records_id_seq OWNER TO "user";

--
-- Name: attendance_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.attendance_records_id_seq OWNED BY public.attendance_records.id;


--
-- Name: branches; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.branches (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    location character varying(255) NOT NULL,
    name_ar character varying(100),
    name_en character varying(100),
    branch_code character varying(20),
    branch_type character varying(50),
    is_active boolean NOT NULL,
    description_ar text,
    description_en text,
    phone character varying(20),
    email character varying(100),
    address_ar text,
    address_en text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.branches OWNER TO "user";

--
-- Name: branches_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.branches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.branches_id_seq OWNER TO "user";

--
-- Name: branches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.branches_id_seq OWNED BY public.branches.id;


--
-- Name: cash_boxes; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.cash_boxes (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    box_type public.cashboxtypeenum NOT NULL,
    branch_id integer NOT NULL,
    user_id integer,
    balance_iqd_cash numeric(15,3) NOT NULL,
    balance_iqd_digital numeric(15,3) NOT NULL,
    balance_usd_cash numeric(15,3) NOT NULL,
    balance_usd_digital numeric(15,3) NOT NULL,
    balance_rmb_cash numeric(15,3) NOT NULL,
    balance_rmb_digital numeric(15,3) NOT NULL,
    is_active boolean NOT NULL,
    description_ar text,
    description_en text,
    last_transaction_date timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    created_by integer
);


ALTER TABLE public.cash_boxes OWNER TO "user";

--
-- Name: cash_boxes_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.cash_boxes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cash_boxes_id_seq OWNER TO "user";

--
-- Name: cash_boxes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.cash_boxes_id_seq OWNED BY public.cash_boxes.id;


--
-- Name: cash_flow_summaries; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.cash_flow_summaries (
    id integer NOT NULL,
    branch_id integer NOT NULL,
    user_id integer,
    summary_date timestamp without time zone NOT NULL,
    summary_type character varying(20) NOT NULL,
    total_receipts_iqd numeric(15,3),
    total_payments_iqd numeric(15,3),
    total_receipts_usd numeric(15,3),
    total_payments_usd numeric(15,3),
    total_receipts_rmb numeric(15,3),
    total_payments_rmb numeric(15,3),
    net_flow_iqd numeric(15,3),
    net_flow_usd numeric(15,3),
    net_flow_rmb numeric(15,3),
    total_transactions integer,
    total_transfers_sent integer,
    total_transfers_received integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.cash_flow_summaries OWNER TO "user";

--
-- Name: cash_flow_summaries_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.cash_flow_summaries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cash_flow_summaries_id_seq OWNER TO "user";

--
-- Name: cash_flow_summaries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.cash_flow_summaries_id_seq OWNED BY public.cash_flow_summaries.id;


--
-- Name: cash_transactions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.cash_transactions (
    id integer NOT NULL,
    transaction_number character varying(100) NOT NULL,
    cash_box_id integer NOT NULL,
    transaction_type character varying(50) NOT NULL,
    payment_method public.cashpaymentmethodenum NOT NULL,
    currency_code character varying(3) NOT NULL,
    amount numeric(15,3) NOT NULL,
    reference_type character varying(50),
    reference_id integer,
    reference_number character varying(100),
    description_ar text,
    description_en text,
    notes text,
    customer_id integer,
    customer_name character varying(255),
    transaction_date timestamp without time zone NOT NULL,
    region public.regionenum,
    location_details character varying(500),
    created_at timestamp without time zone NOT NULL,
    created_by integer
);


ALTER TABLE public.cash_transactions OWNER TO "user";

--
-- Name: cash_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.cash_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cash_transactions_id_seq OWNER TO "user";

--
-- Name: cash_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.cash_transactions_id_seq OWNED BY public.cash_transactions.id;


--
-- Name: cash_transfers; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.cash_transfers (
    id integer NOT NULL,
    transfer_number character varying(100) NOT NULL,
    from_cash_box_id integer NOT NULL,
    to_cash_box_id integer NOT NULL,
    currency_code character varying(3) NOT NULL,
    amount numeric(15,3) NOT NULL,
    payment_method public.cashpaymentmethodenum NOT NULL,
    status public.transferstatusenum NOT NULL,
    description_ar text,
    description_en text,
    transfer_reason character varying(500),
    admin_notes text,
    requested_date timestamp without time zone NOT NULL,
    approved_date timestamp without time zone,
    received_date timestamp without time zone,
    requested_by integer NOT NULL,
    approved_by integer,
    received_by integer,
    transfer_receipt_url character varying(500),
    paper_attachment_url character varying(500),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.cash_transfers OWNER TO "user";

--
-- Name: cash_transfers_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.cash_transfers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cash_transfers_id_seq OWNER TO "user";

--
-- Name: cash_transfers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.cash_transfers_id_seq OWNED BY public.cash_transfers.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    parent_id integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    name_ar character varying(100),
    description_ar text
);


ALTER TABLE public.categories OWNER TO "user";

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_id_seq OWNER TO "user";

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: chart_of_accounts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.chart_of_accounts (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    account_type public.accounttypeenum NOT NULL,
    parent_id integer,
    level integer NOT NULL,
    is_active boolean,
    allow_posting boolean,
    description_ar text,
    description_en text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.chart_of_accounts OWNER TO "user";

--
-- Name: chart_of_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.chart_of_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chart_of_accounts_id_seq OWNER TO "user";

--
-- Name: chart_of_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.chart_of_accounts_id_seq OWNED BY public.chart_of_accounts.id;


--
-- Name: currencies; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.currencies (
    id integer NOT NULL,
    code character varying(3) NOT NULL,
    name_ar character varying(100) NOT NULL,
    name_en character varying(100) NOT NULL,
    symbol character varying(10) NOT NULL,
    exchange_rate numeric(15,6) NOT NULL,
    is_base_currency boolean,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.currencies OWNER TO "user";

--
-- Name: currencies_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.currencies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.currencies_id_seq OWNER TO "user";

--
-- Name: currencies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.currencies_id_seq OWNED BY public.currencies.id;


--
-- Name: customer_price_categories; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.customer_price_categories (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    pricing_list_id integer NOT NULL,
    category character varying NOT NULL,
    effective_date date,
    reason text,
    updated_by integer,
    created_at timestamp without time zone
);


ALTER TABLE public.customer_price_categories OWNER TO "user";

--
-- Name: customer_price_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.customer_price_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.customer_price_categories_id_seq OWNER TO "user";

--
-- Name: customer_price_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.customer_price_categories_id_seq OWNED BY public.customer_price_categories.id;


--
-- Name: customers; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.customers (
    id integer NOT NULL,
    customer_code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    company_name character varying(200),
    phone character varying(20),
    email character varying(255),
    address text,
    city character varying(100),
    country character varying(100),
    tax_number character varying(50),
    credit_limit numeric(12,2),
    payment_terms integer,
    discount_percentage numeric(5,2),
    currency character varying(3),
    portal_language character varying(5),
    salesperson_id integer,
    is_active boolean,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.customers OWNER TO "user";

--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.customers_id_seq OWNER TO "user";

--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.customers_id_seq OWNED BY public.customers.id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    code character varying(10) NOT NULL,
    name_ar character varying(100) NOT NULL,
    name_en character varying(100) NOT NULL,
    description_ar text,
    description_en text,
    head_employee_id integer,
    monthly_budget double precision,
    annual_budget double precision,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.departments OWNER TO "user";

--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.departments_id_seq OWNER TO "user";

--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    employee_code character varying(20) NOT NULL,
    first_name_ar character varying(100) NOT NULL,
    first_name_en character varying(100) NOT NULL,
    last_name_ar character varying(100) NOT NULL,
    last_name_en character varying(100) NOT NULL,
    full_name_ar character varying(200) NOT NULL,
    full_name_en character varying(200) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(20) NOT NULL,
    emergency_contact character varying(20),
    address_ar text,
    address_en text,
    user_id integer,
    department_id integer NOT NULL,
    position_id integer NOT NULL,
    direct_manager_id integer,
    employment_status public.employmentstatus NOT NULL,
    hire_date date NOT NULL,
    termination_date date,
    base_salary double precision NOT NULL,
    currency character varying(3) NOT NULL,
    is_commission_eligible boolean NOT NULL,
    commission_rate double precision NOT NULL,
    working_hours_per_day double precision NOT NULL,
    working_days_per_week integer NOT NULL,
    profile_photo_url character varying(500),
    national_id character varying(50),
    passport_number character varying(50),
    birth_date date,
    gender character varying(10),
    marital_status character varying(20),
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    created_by integer
);


ALTER TABLE public.employees OWNER TO "user";

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employees_id_seq OWNER TO "user";

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: exchange_rates; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.exchange_rates (
    id integer NOT NULL,
    from_currency_id integer NOT NULL,
    to_currency_id integer NOT NULL,
    rate numeric(15,6) NOT NULL,
    date timestamp without time zone NOT NULL,
    is_active boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.exchange_rates OWNER TO "user";

--
-- Name: exchange_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.exchange_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exchange_rates_id_seq OWNER TO "user";

--
-- Name: exchange_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.exchange_rates_id_seq OWNED BY public.exchange_rates.id;


--
-- Name: expense_attachments; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.expense_attachments (
    id integer NOT NULL,
    expense_id integer NOT NULL,
    filename character varying(255) NOT NULL,
    original_filename character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    file_size integer,
    mime_type character varying(100),
    description character varying(200),
    uploaded_by_id integer NOT NULL,
    uploaded_at timestamp without time zone
);


ALTER TABLE public.expense_attachments OWNER TO "user";

--
-- Name: expense_attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.expense_attachments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expense_attachments_id_seq OWNER TO "user";

--
-- Name: expense_attachments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.expense_attachments_id_seq OWNED BY public.expense_attachments.id;


--
-- Name: expense_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.expense_items (
    id integer NOT NULL,
    expense_id integer NOT NULL,
    description character varying(200) NOT NULL,
    quantity numeric(10,3),
    unit_price numeric(15,3) NOT NULL,
    amount numeric(15,3) NOT NULL,
    product_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.expense_items OWNER TO "user";

--
-- Name: expense_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.expense_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expense_items_id_seq OWNER TO "user";

--
-- Name: expense_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.expense_items_id_seq OWNED BY public.expense_items.id;


--
-- Name: expenses; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.expenses (
    id integer NOT NULL,
    expense_number character varying(50) NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    category public.expensecategoryenum NOT NULL,
    amount numeric(15,3) NOT NULL,
    currency_id integer NOT NULL,
    tax_amount numeric(15,3),
    total_amount numeric(15,3) NOT NULL,
    expense_date timestamp without time zone NOT NULL,
    due_date timestamp without time zone,
    payment_date timestamp without time zone,
    status public.expensestatusenum,
    payment_method public.expensepaymentmethodenum,
    user_id integer NOT NULL,
    approved_by_id integer,
    supplier_id integer,
    branch_id integer,
    account_id integer,
    receipt_number character varying(100),
    reference character varying(100),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by_id integer,
    updated_by_id integer
);


ALTER TABLE public.expenses OWNER TO "user";

--
-- Name: expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.expenses_id_seq OWNER TO "user";

--
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.expenses_id_seq OWNED BY public.expenses.id;


--
-- Name: fiscal_years; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.fiscal_years (
    id integer NOT NULL,
    name_ar character varying(100) NOT NULL,
    name_en character varying(100) NOT NULL,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    is_current boolean,
    is_closed boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.fiscal_years OWNER TO "user";

--
-- Name: fiscal_years_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.fiscal_years_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fiscal_years_id_seq OWNER TO "user";

--
-- Name: fiscal_years_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.fiscal_years_id_seq OWNED BY public.fiscal_years.id;


--
-- Name: hr_dashboard_metrics; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.hr_dashboard_metrics (
    id integer NOT NULL,
    metric_date date NOT NULL,
    total_employees integer,
    active_employees integer,
    new_hires_month integer,
    terminations_month integer,
    average_attendance_rate double precision,
    total_late_arrivals integer,
    total_overtime_hours double precision,
    pending_leave_requests integer,
    approved_leaves_month integer,
    total_payroll_amount double precision,
    average_salary double precision,
    total_overtime_cost double precision,
    pending_reviews integer,
    completed_reviews_month integer,
    average_performance_rating double precision,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.hr_dashboard_metrics OWNER TO "user";

--
-- Name: hr_dashboard_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.hr_dashboard_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hr_dashboard_metrics_id_seq OWNER TO "user";

--
-- Name: hr_dashboard_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.hr_dashboard_metrics_id_seq OWNED BY public.hr_dashboard_metrics.id;


--
-- Name: inventory_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.inventory_items (
    id integer NOT NULL,
    product_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    quantity_on_hand numeric(15,3),
    quantity_reserved numeric(15,3),
    quantity_ordered numeric(15,3),
    last_cost numeric(10,2),
    average_cost numeric(10,2),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.inventory_items OWNER TO "user";

--
-- Name: inventory_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.inventory_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventory_items_id_seq OWNER TO "user";

--
-- Name: inventory_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.inventory_items_id_seq OWNED BY public.inventory_items.id;


--
-- Name: invoice_payments; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.invoice_payments (
    id integer NOT NULL,
    payment_number character varying(100) NOT NULL,
    sales_invoice_id integer,
    purchase_invoice_id integer,
    payment_date date NOT NULL,
    amount numeric(15,2) NOT NULL,
    currency_id integer NOT NULL,
    exchange_rate numeric(10,4) NOT NULL,
    payment_method character varying(50) NOT NULL,
    reference_number character varying(100),
    bank_account character varying(100),
    check_number character varying(50),
    check_date date,
    notes text,
    created_by integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.invoice_payments OWNER TO "user";

--
-- Name: invoice_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.invoice_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invoice_payments_id_seq OWNER TO "user";

--
-- Name: invoice_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.invoice_payments_id_seq OWNED BY public.invoice_payments.id;


--
-- Name: item_categories; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.item_categories (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    description_ar text,
    description_en text,
    parent_id integer,
    level integer,
    sort_order integer,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.item_categories OWNER TO "user";

--
-- Name: item_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.item_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.item_categories_id_seq OWNER TO "user";

--
-- Name: item_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.item_categories_id_seq OWNED BY public.item_categories.id;


--
-- Name: journal_entries; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.journal_entries (
    id integer NOT NULL,
    journal_id integer NOT NULL,
    currency_id integer NOT NULL,
    branch_id integer,
    entry_number character varying(50) NOT NULL,
    reference character varying(100),
    reference_type character varying(50),
    reference_id integer,
    entry_date timestamp without time zone NOT NULL,
    posting_date timestamp without time zone,
    description_ar text,
    description_en text,
    total_debit numeric(15,2) NOT NULL,
    total_credit numeric(15,2) NOT NULL,
    status public.transactionstatusenum NOT NULL,
    posted_by integer,
    posted_at timestamp without time zone,
    created_by integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.journal_entries OWNER TO "user";

--
-- Name: journal_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.journal_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journal_entries_id_seq OWNER TO "user";

--
-- Name: journal_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.journal_entries_id_seq OWNED BY public.journal_entries.id;


--
-- Name: journal_lines; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.journal_lines (
    id integer NOT NULL,
    journal_entry_id integer NOT NULL,
    account_id integer NOT NULL,
    line_number integer NOT NULL,
    description_ar text,
    description_en text,
    debit_amount numeric(15,2) NOT NULL,
    credit_amount numeric(15,2) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.journal_lines OWNER TO "user";

--
-- Name: journal_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.journal_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journal_lines_id_seq OWNER TO "user";

--
-- Name: journal_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.journal_lines_id_seq OWNED BY public.journal_lines.id;


--
-- Name: journals; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.journals (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    journal_type public.journaltypeenum NOT NULL,
    is_active boolean,
    description_ar text,
    description_en text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.journals OWNER TO "user";

--
-- Name: journals_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.journals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.journals_id_seq OWNER TO "user";

--
-- Name: journals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.journals_id_seq OWNED BY public.journals.id;


--
-- Name: leave_requests; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.leave_requests (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    leave_type public.leavetype NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    total_days integer NOT NULL,
    reason text NOT NULL,
    supporting_documents text,
    status public.leavestatus NOT NULL,
    requested_by integer NOT NULL,
    reviewed_by integer,
    approved_by integer,
    request_date timestamp without time zone NOT NULL,
    review_date timestamp without time zone,
    approval_date timestamp without time zone,
    employee_comments text,
    manager_comments text,
    hr_comments text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.leave_requests OWNER TO "user";

--
-- Name: leave_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.leave_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.leave_requests_id_seq OWNER TO "user";

--
-- Name: leave_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.leave_requests_id_seq OWNED BY public.leave_requests.id;


--
-- Name: migration_batches; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.migration_batches (
    id integer NOT NULL,
    batch_number character varying(50) NOT NULL,
    batch_name character varying(255) NOT NULL,
    description text,
    status public.migrationstatusenum NOT NULL,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    total_entities integer,
    total_records integer,
    successful_records integer,
    failed_records integer,
    source_system character varying(100),
    migration_config text,
    error_log text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    created_by integer
);


ALTER TABLE public.migration_batches OWNER TO "user";

--
-- Name: migration_batches_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.migration_batches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.migration_batches_id_seq OWNER TO "user";

--
-- Name: migration_batches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.migration_batches_id_seq OWNED BY public.migration_batches.id;


--
-- Name: migration_customers; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.migration_customers (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    email character varying(255),
    phone character varying(20),
    mobile character varying(20),
    address_ar text,
    address_en text,
    city character varying(100),
    region character varying(100),
    postal_code character varying(20),
    country character varying(100),
    tax_number character varying(50),
    currency public.currencyenum NOT NULL,
    credit_limit numeric(15,3),
    payment_terms character varying(100),
    price_list_id integer,
    salesperson_id integer,
    assigned_region character varying(100),
    outstanding_receivable numeric(15,3),
    is_active boolean NOT NULL,
    zoho_customer_id character varying(100),
    zoho_deposit_account character varying(255),
    zoho_last_sync timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.migration_customers OWNER TO "user";

--
-- Name: migration_customers_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.migration_customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.migration_customers_id_seq OWNER TO "user";

--
-- Name: migration_customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.migration_customers_id_seq OWNED BY public.migration_customers.id;


--
-- Name: migration_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.migration_items (
    id integer NOT NULL,
    code character varying(100) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    description_ar text,
    description_en text,
    category_id integer,
    brand character varying(100),
    model character varying(100),
    specifications text,
    unit_of_measure character varying(50),
    cost_price_usd numeric(15,3),
    cost_price_iqd numeric(15,3),
    selling_price_usd numeric(15,3),
    selling_price_iqd numeric(15,3),
    track_inventory boolean,
    reorder_level numeric(10,3),
    reorder_quantity numeric(10,3),
    weight numeric(10,3),
    dimensions character varying(100),
    is_active boolean NOT NULL,
    is_serialized boolean,
    is_batch_tracked boolean,
    zoho_item_id character varying(100),
    zoho_last_sync timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    created_by integer
);


ALTER TABLE public.migration_items OWNER TO "user";

--
-- Name: migration_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.migration_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.migration_items_id_seq OWNER TO "user";

--
-- Name: migration_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.migration_items_id_seq OWNED BY public.migration_items.id;


--
-- Name: migration_records; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.migration_records (
    id integer NOT NULL,
    batch_id integer NOT NULL,
    entity_type character varying(100) NOT NULL,
    source_id character varying(100) NOT NULL,
    source_data text,
    target_id integer,
    status public.migrationstatusenum NOT NULL,
    processed_at timestamp without time zone,
    error_message text,
    retry_count integer,
    requires_manual_review boolean,
    manual_review_notes text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.migration_records OWNER TO "user";

--
-- Name: migration_records_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.migration_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.migration_records_id_seq OWNER TO "user";

--
-- Name: migration_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.migration_records_id_seq OWNED BY public.migration_records.id;


--
-- Name: migration_stock; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.migration_stock (
    id integer NOT NULL,
    item_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    quantity_on_hand numeric(12,3) NOT NULL,
    quantity_reserved numeric(12,3) NOT NULL,
    quantity_available numeric(12,3) NOT NULL,
    average_cost numeric(15,3),
    last_cost numeric(15,3),
    reorder_level numeric(10,3),
    reorder_quantity numeric(10,3),
    max_stock_level numeric(10,3),
    last_movement_date timestamp without time zone,
    last_movement_type character varying(50),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.migration_stock OWNER TO "user";

--
-- Name: migration_stock_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.migration_stock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.migration_stock_id_seq OWNER TO "user";

--
-- Name: migration_stock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.migration_stock_id_seq OWNED BY public.migration_stock.id;


--
-- Name: migration_vendors; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.migration_vendors (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    email character varying(255),
    phone character varying(20),
    contact_person character varying(255),
    address_ar text,
    address_en text,
    city character varying(100),
    country character varying(100),
    tax_number character varying(50),
    currency public.currencyenum NOT NULL,
    payment_terms character varying(100),
    outstanding_payable numeric(15,3),
    is_active boolean NOT NULL,
    zoho_vendor_id character varying(100),
    zoho_last_sync timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.migration_vendors OWNER TO "user";

--
-- Name: migration_vendors_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.migration_vendors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.migration_vendors_id_seq OWNER TO "user";

--
-- Name: migration_vendors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.migration_vendors_id_seq OWNED BY public.migration_vendors.id;


--
-- Name: money_transfers; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.money_transfers (
    id integer NOT NULL,
    transfer_uuid character varying(36),
    salesperson_id integer NOT NULL,
    salesperson_name character varying(100) NOT NULL,
    amount_usd double precision NOT NULL,
    amount_iqd double precision NOT NULL,
    exchange_rate double precision NOT NULL,
    gross_sales double precision NOT NULL,
    commission_rate double precision,
    calculated_commission double precision NOT NULL,
    claimed_commission double precision NOT NULL,
    commission_verified boolean,
    transfer_platform character varying(50) NOT NULL,
    platform_reference character varying(100),
    transfer_fee double precision,
    transfer_datetime timestamp without time zone NOT NULL,
    gps_latitude double precision,
    gps_longitude double precision,
    location_name character varying(200),
    receipt_photo_url character varying(500),
    receipt_verified boolean,
    status character varying(20),
    money_received boolean,
    received_datetime timestamp without time zone,
    is_suspicious boolean,
    fraud_alert_reason text,
    manager_approval_required boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.money_transfers OWNER TO "user";

--
-- Name: money_transfers_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.money_transfers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.money_transfers_id_seq OWNER TO "user";

--
-- Name: money_transfers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.money_transfers_id_seq OWNED BY public.money_transfers.id;


--
-- Name: payroll_records; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.payroll_records (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    payroll_month integer NOT NULL,
    payroll_year integer NOT NULL,
    pay_period_start date NOT NULL,
    pay_period_end date NOT NULL,
    base_salary double precision NOT NULL,
    commission_amount double precision NOT NULL,
    overtime_amount double precision NOT NULL,
    bonus_amount double precision NOT NULL,
    allowances double precision NOT NULL,
    gross_salary double precision NOT NULL,
    tax_deduction double precision NOT NULL,
    social_security double precision NOT NULL,
    insurance_deduction double precision NOT NULL,
    loan_deduction double precision NOT NULL,
    other_deductions double precision NOT NULL,
    total_deductions double precision NOT NULL,
    net_salary double precision NOT NULL,
    working_days integer NOT NULL,
    actual_working_days integer NOT NULL,
    total_hours_worked double precision NOT NULL,
    overtime_hours double precision NOT NULL,
    payment_method character varying(50),
    bank_account character varying(50),
    payment_date date,
    payment_reference character varying(100),
    status public.payrollstatus NOT NULL,
    notes text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    created_by integer,
    approved_by integer,
    approved_at timestamp without time zone
);


ALTER TABLE public.payroll_records OWNER TO "user";

--
-- Name: payroll_records_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.payroll_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.payroll_records_id_seq OWNER TO "user";

--
-- Name: payroll_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.payroll_records_id_seq OWNED BY public.payroll_records.id;


--
-- Name: performance_reviews; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.performance_reviews (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    review_period_start date NOT NULL,
    review_period_end date NOT NULL,
    review_type character varying(50) NOT NULL,
    overall_rating double precision NOT NULL,
    technical_skills double precision,
    communication_skills double precision,
    teamwork double precision,
    leadership double precision,
    punctuality double precision,
    productivity double precision,
    goals_achieved text,
    goals_missed text,
    new_goals text,
    employee_self_assessment text,
    manager_feedback text,
    hr_comments text,
    development_plan text,
    salary_increase_recommended boolean,
    recommended_increase_amount double precision,
    recommended_increase_percentage double precision,
    is_completed boolean,
    employee_acknowledged boolean,
    review_date date NOT NULL,
    employee_acknowledgment_date timestamp without time zone,
    reviewed_by integer NOT NULL,
    hr_reviewed_by integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.performance_reviews OWNER TO "user";

--
-- Name: performance_reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.performance_reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.performance_reviews_id_seq OWNER TO "user";

--
-- Name: performance_reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.performance_reviews_id_seq OWNED BY public.performance_reviews.id;


--
-- Name: pos_discounts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pos_discounts (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    discount_type character varying(20) NOT NULL,
    discount_value numeric(15,2) NOT NULL,
    min_amount numeric(15,2),
    max_amount numeric(15,2),
    min_quantity integer,
    applicable_products text,
    applicable_categories text,
    valid_from timestamp without time zone,
    valid_to timestamp without time zone,
    usage_limit integer,
    usage_count integer,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.pos_discounts OWNER TO "user";

--
-- Name: pos_discounts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pos_discounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pos_discounts_id_seq OWNER TO "user";

--
-- Name: pos_discounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pos_discounts_id_seq OWNED BY public.pos_discounts.id;


--
-- Name: pos_payments; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pos_payments (
    id integer NOT NULL,
    transaction_id integer NOT NULL,
    payment_method public.paymentmethodenum NOT NULL,
    amount numeric(15,2) NOT NULL,
    card_type character varying(50),
    card_last_four character varying(4),
    approval_code character varying(50),
    reference_number character varying(100),
    mobile_number character varying(20),
    mobile_provider character varying(50),
    mobile_reference character varying(100),
    credit_reference character varying(100),
    voucher_code character varying(100),
    voucher_type character varying(50),
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE public.pos_payments OWNER TO "user";

--
-- Name: pos_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pos_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pos_payments_id_seq OWNER TO "user";

--
-- Name: pos_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pos_payments_id_seq OWNED BY public.pos_payments.id;


--
-- Name: pos_promotions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pos_promotions (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    description_ar text,
    description_en text,
    promotion_type character varying(50) NOT NULL,
    rules text,
    valid_from timestamp without time zone,
    valid_to timestamp without time zone,
    usage_limit integer,
    usage_count integer,
    priority integer,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.pos_promotions OWNER TO "user";

--
-- Name: pos_promotions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pos_promotions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pos_promotions_id_seq OWNER TO "user";

--
-- Name: pos_promotions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pos_promotions_id_seq OWNED BY public.pos_promotions.id;


--
-- Name: pos_sessions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pos_sessions (
    id integer NOT NULL,
    session_number character varying(50) NOT NULL,
    terminal_id integer NOT NULL,
    currency_id integer NOT NULL,
    user_id integer NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone,
    status public.possessionstatusenum NOT NULL,
    opening_cash_amount numeric(15,2) NOT NULL,
    opening_notes text,
    closing_cash_amount numeric(15,2),
    closing_card_amount numeric(15,2),
    closing_mobile_amount numeric(15,2),
    closing_total_amount numeric(15,2),
    closing_notes text,
    total_sales numeric(15,2),
    total_refunds numeric(15,2),
    total_discounts numeric(15,2),
    total_tax numeric(15,2),
    transaction_count integer,
    closed_by integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.pos_sessions OWNER TO "user";

--
-- Name: pos_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pos_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pos_sessions_id_seq OWNER TO "user";

--
-- Name: pos_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pos_sessions_id_seq OWNED BY public.pos_sessions.id;


--
-- Name: pos_terminals; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pos_terminals (
    id integer NOT NULL,
    terminal_code character varying(50) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    branch_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    receipt_printer character varying(255),
    barcode_scanner character varying(255),
    cash_drawer character varying(255),
    display character varying(255),
    default_tax_rate numeric(5,2),
    allow_discount boolean,
    max_discount_percent numeric(5,2),
    allow_negative_stock boolean,
    auto_print_receipt boolean,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.pos_terminals OWNER TO "user";

--
-- Name: pos_terminals_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pos_terminals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pos_terminals_id_seq OWNER TO "user";

--
-- Name: pos_terminals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pos_terminals_id_seq OWNED BY public.pos_terminals.id;


--
-- Name: pos_transaction_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pos_transaction_items (
    id integer NOT NULL,
    transaction_id integer NOT NULL,
    product_id integer NOT NULL,
    line_number integer NOT NULL,
    quantity numeric(10,3) NOT NULL,
    unit_price numeric(15,2) NOT NULL,
    discount_amount numeric(15,2) NOT NULL,
    discount_percent numeric(5,2) NOT NULL,
    tax_amount numeric(15,2) NOT NULL,
    tax_percent numeric(5,2) NOT NULL,
    line_total numeric(15,2) NOT NULL,
    notes text,
    created_at timestamp without time zone
);


ALTER TABLE public.pos_transaction_items OWNER TO "user";

--
-- Name: pos_transaction_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pos_transaction_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pos_transaction_items_id_seq OWNER TO "user";

--
-- Name: pos_transaction_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pos_transaction_items_id_seq OWNED BY public.pos_transaction_items.id;


--
-- Name: pos_transactions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pos_transactions (
    id integer NOT NULL,
    transaction_number character varying(50) NOT NULL,
    terminal_id integer NOT NULL,
    session_id integer NOT NULL,
    customer_id integer,
    sales_order_id integer,
    transaction_type public.postransactiontypeenum NOT NULL,
    transaction_date timestamp without time zone NOT NULL,
    subtotal numeric(15,2) NOT NULL,
    discount_amount numeric(15,2) NOT NULL,
    discount_percent numeric(5,2) NOT NULL,
    tax_amount numeric(15,2) NOT NULL,
    tax_percent numeric(5,2) NOT NULL,
    total_amount numeric(15,2) NOT NULL,
    amount_paid numeric(15,2) NOT NULL,
    change_amount numeric(15,2) NOT NULL,
    receipt_number character varying(50),
    notes text,
    void_reason character varying(255),
    voided_at timestamp without time zone,
    voided_by integer,
    cashier_id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.pos_transactions OWNER TO "user";

--
-- Name: pos_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pos_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pos_transactions_id_seq OWNER TO "user";

--
-- Name: pos_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pos_transactions_id_seq OWNED BY public.pos_transactions.id;


--
-- Name: positions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.positions (
    id integer NOT NULL,
    code character varying(10) NOT NULL,
    title_ar character varying(100) NOT NULL,
    title_en character varying(100) NOT NULL,
    description_ar text,
    description_en text,
    min_salary double precision NOT NULL,
    max_salary double precision NOT NULL,
    level integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.positions OWNER TO "user";

--
-- Name: positions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.positions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.positions_id_seq OWNER TO "user";

--
-- Name: positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.positions_id_seq OWNED BY public.positions.id;


--
-- Name: price_history; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.price_history (
    id integer NOT NULL,
    product_id integer NOT NULL,
    pricing_list_id integer NOT NULL,
    old_price numeric(15,2) NOT NULL,
    new_price numeric(15,2) NOT NULL,
    update_type character varying NOT NULL,
    notes text,
    updated_by integer,
    created_at timestamp without time zone
);


ALTER TABLE public.price_history OWNER TO "user";

--
-- Name: price_history_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.price_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.price_history_id_seq OWNER TO "user";

--
-- Name: price_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.price_history_id_seq OWNED BY public.price_history.id;


--
-- Name: price_list_categories; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.price_list_categories (
    id integer NOT NULL,
    pricing_list_id integer NOT NULL,
    customer_category character varying NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.price_list_categories OWNER TO "user";

--
-- Name: price_list_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.price_list_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.price_list_categories_id_seq OWNER TO "user";

--
-- Name: price_list_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.price_list_categories_id_seq OWNED BY public.price_list_categories.id;


--
-- Name: price_list_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.price_list_items (
    id integer NOT NULL,
    price_list_id integer NOT NULL,
    item_id integer NOT NULL,
    unit_price numeric(15,3) NOT NULL,
    discount_percentage numeric(5,2),
    minimum_quantity numeric(10,3),
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.price_list_items OWNER TO "user";

--
-- Name: price_list_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.price_list_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.price_list_items_id_seq OWNER TO "user";

--
-- Name: price_list_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.price_list_items_id_seq OWNED BY public.price_list_items.id;


--
-- Name: price_lists; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.price_lists (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name_ar character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    description_ar text,
    description_en text,
    currency public.currencyenum NOT NULL,
    is_default boolean,
    is_active boolean NOT NULL,
    effective_from timestamp without time zone,
    effective_to timestamp without time zone,
    zoho_price_list_id character varying(100),
    zoho_last_sync timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    created_by integer
);


ALTER TABLE public.price_lists OWNER TO "user";

--
-- Name: price_lists_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.price_lists_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.price_lists_id_seq OWNER TO "user";

--
-- Name: price_lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.price_lists_id_seq OWNED BY public.price_lists.id;


--
-- Name: price_negotiation_requests; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.price_negotiation_requests (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    product_id integer NOT NULL,
    current_price numeric(15,2) NOT NULL,
    requested_price numeric(15,2) NOT NULL,
    quantity integer NOT NULL,
    justification text,
    status character varying,
    valid_until date,
    approved_by integer,
    approved_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.price_negotiation_requests OWNER TO "user";

--
-- Name: price_negotiation_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.price_negotiation_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.price_negotiation_requests_id_seq OWNER TO "user";

--
-- Name: price_negotiation_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.price_negotiation_requests_id_seq OWNED BY public.price_negotiation_requests.id;


--
-- Name: pricing_lists; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.pricing_lists (
    id integer NOT NULL,
    name character varying NOT NULL,
    price_list_type character varying NOT NULL,
    description text,
    minimum_order_value numeric(15,2),
    discount_percentage numeric(5,2),
    is_active boolean,
    valid_from date,
    valid_to date,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.pricing_lists OWNER TO "user";

--
-- Name: pricing_lists_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.pricing_lists_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pricing_lists_id_seq OWNER TO "user";

--
-- Name: pricing_lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.pricing_lists_id_seq OWNED BY public.pricing_lists.id;


--
-- Name: product_prices; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.product_prices (
    id integer NOT NULL,
    product_id integer NOT NULL,
    pricing_list_id integer NOT NULL,
    price numeric(15,2) NOT NULL,
    discount_percentage numeric(5,2),
    minimum_quantity integer,
    is_negotiable boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.product_prices OWNER TO "user";

--
-- Name: product_prices_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.product_prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.product_prices_id_seq OWNER TO "user";

--
-- Name: product_prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.product_prices_id_seq OWNED BY public.product_prices.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.products (
    id integer NOT NULL,
    sku character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    category_id integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    cost_price numeric(10,2),
    unit_of_measure character varying(50) NOT NULL,
    min_stock_level integer,
    max_stock_level integer,
    reorder_point integer,
    barcode character varying(100),
    is_active boolean,
    is_trackable boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    name_ar character varying(200),
    description_ar text,
    image_url character varying(500),
    images json,
    videos json,
    weight numeric(10,3),
    dimensions json,
    color character varying(50),
    size character varying(50),
    brand character varying(100),
    model character varying(100),
    is_digital boolean,
    is_featured boolean,
    meta_title character varying(200),
    meta_description text,
    tags json
);


ALTER TABLE public.products OWNER TO "user";

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.products_id_seq OWNER TO "user";

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: purchase_invoice_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.purchase_invoice_items (
    id integer NOT NULL,
    invoice_id integer NOT NULL,
    product_id integer NOT NULL,
    purchase_item_id integer,
    quantity numeric(15,3) NOT NULL,
    unit_cost numeric(10,2) NOT NULL,
    discount_percentage numeric(5,2),
    discount_amount numeric(10,2),
    line_total numeric(12,2) NOT NULL,
    description text,
    notes text
);


ALTER TABLE public.purchase_invoice_items OWNER TO "user";

--
-- Name: purchase_invoice_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.purchase_invoice_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.purchase_invoice_items_id_seq OWNER TO "user";

--
-- Name: purchase_invoice_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.purchase_invoice_items_id_seq OWNED BY public.purchase_invoice_items.id;


--
-- Name: purchase_invoices; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.purchase_invoices (
    id integer NOT NULL,
    invoice_number character varying(100) NOT NULL,
    supplier_invoice_number character varying(100),
    supplier_id integer NOT NULL,
    purchase_order_id integer,
    branch_id integer NOT NULL,
    warehouse_id integer,
    invoice_date date NOT NULL,
    due_date date NOT NULL,
    received_date date,
    currency_id integer NOT NULL,
    exchange_rate numeric(10,4) NOT NULL,
    invoice_type public.invoicetypeenum NOT NULL,
    status public.invoicestatusenum NOT NULL,
    payment_terms public.paymenttermsenum NOT NULL,
    subtotal numeric(15,2) NOT NULL,
    discount_percentage numeric(5,2),
    discount_amount numeric(15,2),
    tax_percentage numeric(5,2),
    tax_amount numeric(15,2),
    shipping_amount numeric(15,2),
    total_amount numeric(15,2) NOT NULL,
    paid_amount numeric(15,2),
    notes text,
    internal_notes text,
    payment_method character varying(50),
    reference_number character varying(100),
    created_by integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    received_at timestamp with time zone,
    cancelled_at timestamp with time zone
);


ALTER TABLE public.purchase_invoices OWNER TO "user";

--
-- Name: purchase_invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.purchase_invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.purchase_invoices_id_seq OWNER TO "user";

--
-- Name: purchase_invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.purchase_invoices_id_seq OWNED BY public.purchase_invoices.id;


--
-- Name: purchase_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.purchase_items (
    id integer NOT NULL,
    purchase_order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity numeric(15,3) NOT NULL,
    unit_cost numeric(10,2) NOT NULL,
    discount_percentage numeric(5,2),
    discount_amount numeric(10,2),
    line_total numeric(12,2) NOT NULL,
    received_quantity numeric(15,3),
    notes text
);


ALTER TABLE public.purchase_items OWNER TO "user";

--
-- Name: purchase_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.purchase_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.purchase_items_id_seq OWNER TO "user";

--
-- Name: purchase_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.purchase_items_id_seq OWNED BY public.purchase_items.id;


--
-- Name: purchase_orders; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.purchase_orders (
    id integer NOT NULL,
    order_number character varying(50) NOT NULL,
    supplier_id integer NOT NULL,
    branch_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    order_date date NOT NULL,
    expected_delivery_date date,
    actual_delivery_date date,
    status character varying(50),
    payment_status character varying(50),
    payment_method character varying(50),
    subtotal numeric(12,2),
    discount_percentage numeric(5,2),
    discount_amount numeric(12,2),
    tax_percentage numeric(5,2),
    tax_amount numeric(12,2),
    total_amount numeric(12,2),
    paid_amount numeric(12,2),
    notes text,
    created_by integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.purchase_orders OWNER TO "user";

--
-- Name: purchase_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.purchase_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.purchase_orders_id_seq OWNER TO "user";

--
-- Name: purchase_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.purchase_orders_id_seq OWNED BY public.purchase_orders.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.roles OWNER TO "user";

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO "user";

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: sales_invoice_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.sales_invoice_items (
    id integer NOT NULL,
    invoice_id integer NOT NULL,
    product_id integer NOT NULL,
    sales_item_id integer,
    quantity numeric(15,3) NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    discount_percentage numeric(5,2),
    discount_amount numeric(10,2),
    line_total numeric(12,2) NOT NULL,
    description text,
    notes text
);


ALTER TABLE public.sales_invoice_items OWNER TO "user";

--
-- Name: sales_invoice_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.sales_invoice_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sales_invoice_items_id_seq OWNER TO "user";

--
-- Name: sales_invoice_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.sales_invoice_items_id_seq OWNED BY public.sales_invoice_items.id;


--
-- Name: sales_invoices; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.sales_invoices (
    id integer NOT NULL,
    invoice_number character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    sales_order_id integer,
    branch_id integer NOT NULL,
    warehouse_id integer,
    invoice_date date NOT NULL,
    due_date date NOT NULL,
    currency_id integer NOT NULL,
    exchange_rate numeric(10,4) NOT NULL,
    invoice_type public.invoicetypeenum NOT NULL,
    status public.invoicestatusenum NOT NULL,
    payment_terms public.paymenttermsenum NOT NULL,
    subtotal numeric(15,2) NOT NULL,
    discount_percentage numeric(5,2),
    discount_amount numeric(15,2),
    tax_percentage numeric(5,2),
    tax_amount numeric(15,2),
    shipping_amount numeric(15,2),
    total_amount numeric(15,2) NOT NULL,
    paid_amount numeric(15,2),
    notes text,
    internal_notes text,
    payment_method character varying(50),
    reference_number character varying(100),
    is_recurring boolean,
    recurring_frequency character varying(20),
    parent_invoice_id integer,
    created_by integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    issued_at timestamp with time zone,
    cancelled_at timestamp with time zone
);


ALTER TABLE public.sales_invoices OWNER TO "user";

--
-- Name: sales_invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.sales_invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sales_invoices_id_seq OWNER TO "user";

--
-- Name: sales_invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.sales_invoices_id_seq OWNED BY public.sales_invoices.id;


--
-- Name: sales_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.sales_items (
    id integer NOT NULL,
    sales_order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity numeric(15,3) NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    discount_percentage numeric(5,2),
    discount_amount numeric(10,2),
    line_total numeric(12,2) NOT NULL,
    delivered_quantity numeric(15,3),
    notes text
);


ALTER TABLE public.sales_items OWNER TO "user";

--
-- Name: sales_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.sales_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sales_items_id_seq OWNER TO "user";

--
-- Name: sales_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.sales_items_id_seq OWNED BY public.sales_items.id;


--
-- Name: sales_orders; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.sales_orders (
    id integer NOT NULL,
    order_number character varying(50) NOT NULL,
    customer_id integer NOT NULL,
    branch_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    order_date date NOT NULL,
    expected_delivery_date date,
    actual_delivery_date date,
    status character varying(50),
    payment_status character varying(50),
    payment_method character varying(50),
    subtotal numeric(12,2),
    discount_percentage numeric(5,2),
    discount_amount numeric(12,2),
    tax_percentage numeric(5,2),
    tax_amount numeric(12,2),
    total_amount numeric(12,2),
    paid_amount numeric(12,2),
    notes text,
    created_by integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.sales_orders OWNER TO "user";

--
-- Name: sales_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.sales_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sales_orders_id_seq OWNER TO "user";

--
-- Name: sales_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.sales_orders_id_seq OWNED BY public.sales_orders.id;


--
-- Name: salesperson_regions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.salesperson_regions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    region public.regionenum NOT NULL,
    is_primary boolean NOT NULL,
    is_active boolean NOT NULL,
    assigned_date timestamp without time zone NOT NULL,
    created_at timestamp without time zone NOT NULL,
    assigned_by integer
);


ALTER TABLE public.salesperson_regions OWNER TO "user";

--
-- Name: salesperson_regions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.salesperson_regions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.salesperson_regions_id_seq OWNER TO "user";

--
-- Name: salesperson_regions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.salesperson_regions_id_seq OWNED BY public.salesperson_regions.id;


--
-- Name: stock_movements; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.stock_movements (
    id integer NOT NULL,
    inventory_item_id integer NOT NULL,
    movement_type character varying(50) NOT NULL,
    reference_type character varying(50),
    reference_id integer,
    quantity numeric(15,3) NOT NULL,
    unit_cost numeric(10,2),
    notes text,
    created_by integer NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.stock_movements OWNER TO "user";

--
-- Name: stock_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.stock_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.stock_movements_id_seq OWNER TO "user";

--
-- Name: stock_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.stock_movements_id_seq OWNED BY public.stock_movements.id;


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.suppliers (
    id integer NOT NULL,
    supplier_code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    company_name character varying(200),
    phone character varying(20),
    email character varying(255),
    address text,
    city character varying(100),
    country character varying(100),
    tax_number character varying(50),
    payment_terms integer,
    is_active boolean,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.suppliers OWNER TO "user";

--
-- Name: suppliers_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.suppliers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.suppliers_id_seq OWNER TO "user";

--
-- Name: suppliers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.suppliers_id_seq OWNED BY public.suppliers.id;


--
-- Name: transfer_platforms; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.transfer_platforms (
    id integer NOT NULL,
    platform_name character varying(50) NOT NULL,
    platform_code character varying(10) NOT NULL,
    has_api boolean,
    api_endpoint character varying(200),
    is_active boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.transfer_platforms OWNER TO "user";

--
-- Name: transfer_platforms_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.transfer_platforms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transfer_platforms_id_seq OWNER TO "user";

--
-- Name: transfer_platforms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.transfer_platforms_id_seq OWNED BY public.transfer_platforms.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    role_id integer NOT NULL,
    branch_id integer NOT NULL,
    employee_code character varying(20),
    phone character varying(20),
    is_salesperson boolean NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    last_login timestamp without time zone
);


ALTER TABLE public.users OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.warehouses (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    branch_id integer NOT NULL
);


ALTER TABLE public.warehouses OWNER TO "user";

--
-- Name: warehouses_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.warehouses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.warehouses_id_seq OWNER TO "user";

--
-- Name: warehouses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.warehouses_id_seq OWNED BY public.warehouses.id;


--
-- Name: whatsapp_auto_responses; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.whatsapp_auto_responses (
    id integer NOT NULL,
    triggers json,
    response_text text NOT NULL,
    language character varying,
    active boolean,
    usage_count integer,
    created_at timestamp without time zone
);


ALTER TABLE public.whatsapp_auto_responses OWNER TO "user";

--
-- Name: whatsapp_auto_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.whatsapp_auto_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.whatsapp_auto_responses_id_seq OWNER TO "user";

--
-- Name: whatsapp_auto_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.whatsapp_auto_responses_id_seq OWNED BY public.whatsapp_auto_responses.id;


--
-- Name: whatsapp_broadcasts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.whatsapp_broadcasts (
    id integer NOT NULL,
    broadcast_id character varying,
    template_name character varying NOT NULL,
    language character varying,
    total_recipients integer,
    sent_count integer,
    failed_count integer,
    status character varying,
    created_at timestamp without time zone,
    completed_at timestamp without time zone
);


ALTER TABLE public.whatsapp_broadcasts OWNER TO "user";

--
-- Name: whatsapp_broadcasts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.whatsapp_broadcasts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.whatsapp_broadcasts_id_seq OWNER TO "user";

--
-- Name: whatsapp_broadcasts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.whatsapp_broadcasts_id_seq OWNED BY public.whatsapp_broadcasts.id;


--
-- Name: whatsapp_messages; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.whatsapp_messages (
    id integer NOT NULL,
    phone_number character varying NOT NULL,
    message_type character varying NOT NULL,
    content text,
    direction character varying NOT NULL,
    language character varying,
    whatsapp_message_id character varying,
    media_url character varying,
    delivery_status character varying,
    api_response json,
    status_updated_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.whatsapp_messages OWNER TO "user";

--
-- Name: whatsapp_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.whatsapp_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.whatsapp_messages_id_seq OWNER TO "user";

--
-- Name: whatsapp_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.whatsapp_messages_id_seq OWNED BY public.whatsapp_messages.id;


--
-- Name: accounting_periods id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accounting_periods ALTER COLUMN id SET DEFAULT nextval('public.accounting_periods_id_seq'::regclass);


--
-- Name: accounts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);


--
-- Name: ai_conversation_messages id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_conversation_messages ALTER COLUMN id SET DEFAULT nextval('public.ai_conversation_messages_id_seq'::regclass);


--
-- Name: ai_conversations id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_conversations ALTER COLUMN id SET DEFAULT nextval('public.ai_conversations_id_seq'::regclass);


--
-- Name: ai_generated_orders id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_generated_orders ALTER COLUMN id SET DEFAULT nextval('public.ai_generated_orders_id_seq'::regclass);


--
-- Name: ai_support_tickets id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_support_tickets ALTER COLUMN id SET DEFAULT nextval('public.ai_support_tickets_id_seq'::regclass);


--
-- Name: attendance_records id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.attendance_records ALTER COLUMN id SET DEFAULT nextval('public.attendance_records_id_seq'::regclass);


--
-- Name: branches id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.branches ALTER COLUMN id SET DEFAULT nextval('public.branches_id_seq'::regclass);


--
-- Name: cash_boxes id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_boxes ALTER COLUMN id SET DEFAULT nextval('public.cash_boxes_id_seq'::regclass);


--
-- Name: cash_flow_summaries id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_flow_summaries ALTER COLUMN id SET DEFAULT nextval('public.cash_flow_summaries_id_seq'::regclass);


--
-- Name: cash_transactions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transactions ALTER COLUMN id SET DEFAULT nextval('public.cash_transactions_id_seq'::regclass);


--
-- Name: cash_transfers id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transfers ALTER COLUMN id SET DEFAULT nextval('public.cash_transfers_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: chart_of_accounts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.chart_of_accounts ALTER COLUMN id SET DEFAULT nextval('public.chart_of_accounts_id_seq'::regclass);


--
-- Name: currencies id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.currencies ALTER COLUMN id SET DEFAULT nextval('public.currencies_id_seq'::regclass);


--
-- Name: customer_price_categories id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.customer_price_categories ALTER COLUMN id SET DEFAULT nextval('public.customer_price_categories_id_seq'::regclass);


--
-- Name: customers id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.customers ALTER COLUMN id SET DEFAULT nextval('public.customers_id_seq'::regclass);


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: exchange_rates id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exchange_rates ALTER COLUMN id SET DEFAULT nextval('public.exchange_rates_id_seq'::regclass);


--
-- Name: expense_attachments id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expense_attachments ALTER COLUMN id SET DEFAULT nextval('public.expense_attachments_id_seq'::regclass);


--
-- Name: expense_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expense_items ALTER COLUMN id SET DEFAULT nextval('public.expense_items_id_seq'::regclass);


--
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.expenses_id_seq'::regclass);


--
-- Name: fiscal_years id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.fiscal_years ALTER COLUMN id SET DEFAULT nextval('public.fiscal_years_id_seq'::regclass);


--
-- Name: hr_dashboard_metrics id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.hr_dashboard_metrics ALTER COLUMN id SET DEFAULT nextval('public.hr_dashboard_metrics_id_seq'::regclass);


--
-- Name: inventory_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory_items ALTER COLUMN id SET DEFAULT nextval('public.inventory_items_id_seq'::regclass);


--
-- Name: invoice_payments id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_payments ALTER COLUMN id SET DEFAULT nextval('public.invoice_payments_id_seq'::regclass);


--
-- Name: item_categories id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.item_categories ALTER COLUMN id SET DEFAULT nextval('public.item_categories_id_seq'::regclass);


--
-- Name: journal_entries id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries ALTER COLUMN id SET DEFAULT nextval('public.journal_entries_id_seq'::regclass);


--
-- Name: journal_lines id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_lines ALTER COLUMN id SET DEFAULT nextval('public.journal_lines_id_seq'::regclass);


--
-- Name: journals id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journals ALTER COLUMN id SET DEFAULT nextval('public.journals_id_seq'::regclass);


--
-- Name: leave_requests id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.leave_requests ALTER COLUMN id SET DEFAULT nextval('public.leave_requests_id_seq'::regclass);


--
-- Name: migration_batches id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_batches ALTER COLUMN id SET DEFAULT nextval('public.migration_batches_id_seq'::regclass);


--
-- Name: migration_customers id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_customers ALTER COLUMN id SET DEFAULT nextval('public.migration_customers_id_seq'::regclass);


--
-- Name: migration_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_items ALTER COLUMN id SET DEFAULT nextval('public.migration_items_id_seq'::regclass);


--
-- Name: migration_records id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_records ALTER COLUMN id SET DEFAULT nextval('public.migration_records_id_seq'::regclass);


--
-- Name: migration_stock id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_stock ALTER COLUMN id SET DEFAULT nextval('public.migration_stock_id_seq'::regclass);


--
-- Name: migration_vendors id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_vendors ALTER COLUMN id SET DEFAULT nextval('public.migration_vendors_id_seq'::regclass);


--
-- Name: money_transfers id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.money_transfers ALTER COLUMN id SET DEFAULT nextval('public.money_transfers_id_seq'::regclass);


--
-- Name: payroll_records id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.payroll_records ALTER COLUMN id SET DEFAULT nextval('public.payroll_records_id_seq'::regclass);


--
-- Name: performance_reviews id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.performance_reviews ALTER COLUMN id SET DEFAULT nextval('public.performance_reviews_id_seq'::regclass);


--
-- Name: pos_discounts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_discounts ALTER COLUMN id SET DEFAULT nextval('public.pos_discounts_id_seq'::regclass);


--
-- Name: pos_payments id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_payments ALTER COLUMN id SET DEFAULT nextval('public.pos_payments_id_seq'::regclass);


--
-- Name: pos_promotions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_promotions ALTER COLUMN id SET DEFAULT nextval('public.pos_promotions_id_seq'::regclass);


--
-- Name: pos_sessions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_sessions ALTER COLUMN id SET DEFAULT nextval('public.pos_sessions_id_seq'::regclass);


--
-- Name: pos_terminals id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_terminals ALTER COLUMN id SET DEFAULT nextval('public.pos_terminals_id_seq'::regclass);


--
-- Name: pos_transaction_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transaction_items ALTER COLUMN id SET DEFAULT nextval('public.pos_transaction_items_id_seq'::regclass);


--
-- Name: pos_transactions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transactions ALTER COLUMN id SET DEFAULT nextval('public.pos_transactions_id_seq'::regclass);


--
-- Name: positions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.positions ALTER COLUMN id SET DEFAULT nextval('public.positions_id_seq'::regclass);


--
-- Name: price_history id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_history ALTER COLUMN id SET DEFAULT nextval('public.price_history_id_seq'::regclass);


--
-- Name: price_list_categories id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_list_categories ALTER COLUMN id SET DEFAULT nextval('public.price_list_categories_id_seq'::regclass);


--
-- Name: price_list_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_list_items ALTER COLUMN id SET DEFAULT nextval('public.price_list_items_id_seq'::regclass);


--
-- Name: price_lists id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_lists ALTER COLUMN id SET DEFAULT nextval('public.price_lists_id_seq'::regclass);


--
-- Name: price_negotiation_requests id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_negotiation_requests ALTER COLUMN id SET DEFAULT nextval('public.price_negotiation_requests_id_seq'::regclass);


--
-- Name: pricing_lists id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pricing_lists ALTER COLUMN id SET DEFAULT nextval('public.pricing_lists_id_seq'::regclass);


--
-- Name: product_prices id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.product_prices ALTER COLUMN id SET DEFAULT nextval('public.product_prices_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: purchase_invoice_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoice_items ALTER COLUMN id SET DEFAULT nextval('public.purchase_invoice_items_id_seq'::regclass);


--
-- Name: purchase_invoices id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoices ALTER COLUMN id SET DEFAULT nextval('public.purchase_invoices_id_seq'::regclass);


--
-- Name: purchase_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_items ALTER COLUMN id SET DEFAULT nextval('public.purchase_items_id_seq'::regclass);


--
-- Name: purchase_orders id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_orders ALTER COLUMN id SET DEFAULT nextval('public.purchase_orders_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: sales_invoice_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoice_items ALTER COLUMN id SET DEFAULT nextval('public.sales_invoice_items_id_seq'::regclass);


--
-- Name: sales_invoices id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices ALTER COLUMN id SET DEFAULT nextval('public.sales_invoices_id_seq'::regclass);


--
-- Name: sales_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_items ALTER COLUMN id SET DEFAULT nextval('public.sales_items_id_seq'::regclass);


--
-- Name: sales_orders id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_orders ALTER COLUMN id SET DEFAULT nextval('public.sales_orders_id_seq'::regclass);


--
-- Name: salesperson_regions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.salesperson_regions ALTER COLUMN id SET DEFAULT nextval('public.salesperson_regions_id_seq'::regclass);


--
-- Name: stock_movements id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.stock_movements ALTER COLUMN id SET DEFAULT nextval('public.stock_movements_id_seq'::regclass);


--
-- Name: suppliers id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.suppliers ALTER COLUMN id SET DEFAULT nextval('public.suppliers_id_seq'::regclass);


--
-- Name: transfer_platforms id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.transfer_platforms ALTER COLUMN id SET DEFAULT nextval('public.transfer_platforms_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: warehouses id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.warehouses ALTER COLUMN id SET DEFAULT nextval('public.warehouses_id_seq'::regclass);


--
-- Name: whatsapp_auto_responses id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.whatsapp_auto_responses ALTER COLUMN id SET DEFAULT nextval('public.whatsapp_auto_responses_id_seq'::regclass);


--
-- Name: whatsapp_broadcasts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.whatsapp_broadcasts ALTER COLUMN id SET DEFAULT nextval('public.whatsapp_broadcasts_id_seq'::regclass);


--
-- Name: whatsapp_messages id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.whatsapp_messages ALTER COLUMN id SET DEFAULT nextval('public.whatsapp_messages_id_seq'::regclass);


--
-- Data for Name: accounting_periods; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.accounting_periods (id, fiscal_year_id, name_ar, name_en, start_date, end_date, is_closed, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.accounts (id, chart_account_id, currency_id, branch_id, balance_debit, balance_credit, balance, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: ai_conversation_messages; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.ai_conversation_messages (id, conversation_id, message_content, message_type, language, platform, is_from_customer, intent, confidence_score, created_at) FROM stdin;
\.


--
-- Data for Name: ai_conversations; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.ai_conversations (id, customer_id, customer_phone, status, created_at, last_activity, message_count, escalated_at, escalated_reason) FROM stdin;
\.


--
-- Data for Name: ai_generated_orders; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.ai_generated_orders (id, order_number, customer_id, customer_phone, total_amount, delivery_address, payment_method, order_items, language, notes, status, confirmed_at, created_at) FROM stdin;
\.


--
-- Data for Name: ai_support_tickets; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.ai_support_tickets (id, ticket_number, customer_id, issue_type, description, priority, language, status, assigned_to, resolved_at, created_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.alembic_version (version_num) FROM stdin;
700e3f25897c
\.


--
-- Data for Name: attendance_records; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.attendance_records (id, employee_id, date, check_in_time, check_out_time, check_in_latitude, check_in_longitude, check_out_latitude, check_out_longitude, check_in_location, check_out_location, total_hours, regular_hours, overtime_hours, status, is_late, late_minutes, notes, manager_notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: branches; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.branches (id, name, location, name_ar, name_en, branch_code, branch_type, is_active, description_ar, description_en, phone, email, address_ar, address_en, created_at, updated_at) FROM stdin;
1	فرع بغداد الرئيسي	Baghdad, Iraq	فرع بغداد الرئيسي	Baghdad Main Branch	BGD-001	MAIN_BRANCH	t	\N	\N	+964-1-7765432	baghdad@tsh.com	الكرادة، شارع أبو نواس، بغداد، العراق	Karrada, Abu Nawas Street, Baghdad, Iraq	2025-07-02 15:32:57.326587	2025-07-02 15:32:57.327201
2	فرع البصرة	Basra, Iraq	فرع البصرة	Basra Branch	BSR-001	REGIONAL_BRANCH	t	\N	\N	+964-40-123456	basra@tsh.com	الحارثية، البصرة، العراق	Al-Hartha, Basra, Iraq	2025-07-02 15:32:57.330874	2025-07-02 15:32:57.331038
3	فرع أربيل	Erbil, Kurdistan Region	فرع أربيل	Erbil Branch	ERB-001	REGIONAL_BRANCH	t	\N	\N	+964-66-234567	erbil@tsh.com	أربيل، إقليم كردستان، العراق	Erbil, Kurdistan Region, Iraq	2025-07-02 15:32:57.332779	2025-07-02 15:32:57.332911
4	فرع النجف	Najaf, Iraq	فرع النجف	Najaf Branch	NJF-001	REGIONAL_BRANCH	t	\N	\N	+964-33-345678	najaf@tsh.com	النجف الأشرف، العراق	Najaf Al-Ashraf, Iraq	2025-07-02 15:32:57.33462	2025-07-02 15:32:57.334773
5	Main Wholesale Branch	Main Wholesale Location, Baghdad, Iraq	\N	\N	\N	\N	t	\N	\N	\N	\N	\N	\N	2025-07-02 17:39:47.968089	2025-07-02 17:39:47.968092
6	TSH Dora Branch	Dora District, Baghdad, Iraq	\N	\N	\N	\N	t	\N	\N	\N	\N	\N	\N	2025-07-02 17:39:47.970459	2025-07-02 17:39:47.97046
\.


--
-- Data for Name: cash_boxes; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.cash_boxes (id, code, name_ar, name_en, box_type, branch_id, user_id, balance_iqd_cash, balance_iqd_digital, balance_usd_cash, balance_usd_digital, balance_rmb_cash, balance_rmb_digital, is_active, description_ar, description_en, last_transaction_date, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: cash_flow_summaries; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.cash_flow_summaries (id, branch_id, user_id, summary_date, summary_type, total_receipts_iqd, total_payments_iqd, total_receipts_usd, total_payments_usd, total_receipts_rmb, total_payments_rmb, net_flow_iqd, net_flow_usd, net_flow_rmb, total_transactions, total_transfers_sent, total_transfers_received, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cash_transactions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.cash_transactions (id, transaction_number, cash_box_id, transaction_type, payment_method, currency_code, amount, reference_type, reference_id, reference_number, description_ar, description_en, notes, customer_id, customer_name, transaction_date, region, location_details, created_at, created_by) FROM stdin;
\.


--
-- Data for Name: cash_transfers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.cash_transfers (id, transfer_number, from_cash_box_id, to_cash_box_id, currency_code, amount, payment_method, status, description_ar, description_en, transfer_reason, admin_notes, requested_date, approved_date, received_date, requested_by, approved_by, received_by, transfer_receipt_url, paper_attachment_url, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.categories (id, name, description, parent_id, is_active, created_at, updated_at, name_ar, description_ar) FROM stdin;
1	منتجات عامة	فئة افتراضية للمنتجات	\N	t	2025-07-02 20:41:37.662321+03	\N	\N	\N
\.


--
-- Data for Name: chart_of_accounts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.chart_of_accounts (id, code, name_ar, name_en, account_type, parent_id, level, is_active, allow_posting, description_ar, description_en, created_at, updated_at) FROM stdin;
1	1000	الأصول	Assets	ASSET	\N	1	t	t	\N	\N	2025-07-01 19:44:16.056264	2025-07-01 19:44:16.056265
2	2000	الخصوم	Liabilities	LIABILITY	\N	1	t	t	\N	\N	2025-07-01 19:44:16.056266	2025-07-01 19:44:16.056266
3	3000	حقوق الملكية	Equity	EQUITY	\N	1	t	t	\N	\N	2025-07-01 19:44:16.056266	2025-07-01 19:44:16.056267
4	4000	الإيرادات	Revenue	REVENUE	\N	1	t	t	\N	\N	2025-07-01 19:44:16.056267	2025-07-01 19:44:16.056267
5	5000	المصروفات	Expenses	EXPENSE	\N	1	t	t	\N	\N	2025-07-01 19:44:16.056267	2025-07-01 19:44:16.056267
\.


--
-- Data for Name: currencies; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.currencies (id, code, name_ar, name_en, symbol, exchange_rate, is_base_currency, is_active, created_at, updated_at) FROM stdin;
1	USD	الدولار الأمريكي	US Dollar	$	1.000000	t	t	2025-07-01 19:43:16.412388	2025-07-01 19:43:16.412389
2	IQD	الدينار العراقي	Iraqi Dinar	د.ع	1320.000000	f	t	2025-07-01 19:43:16.414464	2025-07-01 19:43:16.414465
\.


--
-- Data for Name: customer_price_categories; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.customer_price_categories (id, customer_id, pricing_list_id, category, effective_date, reason, updated_by, created_at) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.customers (id, customer_code, name, company_name, phone, email, address, city, country, tax_number, credit_limit, payment_terms, discount_percentage, currency, portal_language, salesperson_id, is_active, notes, created_at, updated_at) FROM stdin;
1	CUST-0001	شركة بغداد للإلكترونيات	Baghdad Electronics Corporation	+964-1-7777777	info@baghdad-electronics.iq	الكرادة الشرقية، شارع أبو نواس	بغداد	العراق	TAX-BGD-001	75000.00	30	12.00	IQD	ar	\N	t	موزع معتمد للأجهزة الإلكترونية والكهربائية	2025-07-02 17:40:36.116181+03	\N
2	CUST-0002	مؤسسة أربيل التجارية	Erbil Trading Establishment	+964-66-2222222	sales@erbil-trading.com	وسط المدينة، شارع الستين متر	أربيل	العراق	TAX-ERB-002	100000.00	45	15.00	USD	ar	\N	t	شركة استيراد وتصدير	2025-07-02 17:40:36.132914+03	\N
3	CUST-0003	شركة البصرة للخدمات النفطية	Basra Oil Services Ltd.	+964-40-5555555	procurement@basra-oil.iq	المنطقة الصناعية، البصرة	البصرة	العراق	TAX-BSR-003	200000.00	60	8.00	USD	ar	\N	t	مورد خدمات الصناعة النفطية	2025-07-02 17:40:36.1355+03	\N
4	ALLY-0004	تحالف الشركات التقنية	Technology Alliance Consortium	+964-53-8888888	partners@tech-alliance.iq	منطقة التكنولوجيا، السليمانية	السليمانية	العراق	TAX-ALLY-001	500000.00	90	25.00	USD	ar	\N	t	شريك استراتيجي في التكنولوجيا والابتكار	2025-07-02 17:40:36.137279+03	\N
5	ALLY-0005	تحالف المقاولين العراقيين	Iraqi Contractors Alliance	+964-33-9999999	info@contractors-alliance.iq	المنطقة الصناعية، النجف	النجف	العراق	TAX-ALLY-002	300000.00	120	20.00	IQD	ar	\N	t	تحالف مقاولين للمشاريع الكبيرة	2025-07-02 17:40:36.139453+03	\N
6	CONS-0006	أحمد محمد علي	\N	+964-770-1234567	ahmed.ali@gmail.com	حي الجادرية، بغداد	بغداد	العراق	\N	5000.00	7	5.00	IQD	ar	\N	t	عميل فردي - مستهلك	2025-07-02 17:40:36.141941+03	\N
7	CONS-0007	فاطمة حسن محمود	\N	+964-780-2345678	fatima.hassan@yahoo.com	حي الأندلس، بغداد	بغداد	العراق	\N	3000.00	7	3.00	IQD	ar	\N	t	عميلة فردية - مستهلكة	2025-07-02 17:40:36.144316+03	\N
8	CONS-0008	محمد عمار الكردي	\N	+964-750-3456789	mohammed.kurdi@hotmail.com	حي عنكاوا، أربيل	أربيل	العراق	\N	8000.00	14	7.00	USD	ar	\N	t	عميل فردي من إقليم كردستان	2025-07-02 17:40:36.146131+03	\N
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.departments (id, code, name_ar, name_en, description_ar, description_en, head_employee_id, monthly_budget, annual_budget, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.employees (id, employee_code, first_name_ar, first_name_en, last_name_ar, last_name_en, full_name_ar, full_name_en, email, phone, emergency_contact, address_ar, address_en, user_id, department_id, position_id, direct_manager_id, employment_status, hire_date, termination_date, base_salary, currency, is_commission_eligible, commission_rate, working_hours_per_day, working_days_per_week, profile_photo_url, national_id, passport_number, birth_date, gender, marital_status, is_active, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: exchange_rates; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.exchange_rates (id, from_currency_id, to_currency_id, rate, date, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: expense_attachments; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.expense_attachments (id, expense_id, filename, original_filename, file_path, file_size, mime_type, description, uploaded_by_id, uploaded_at) FROM stdin;
\.


--
-- Data for Name: expense_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.expense_items (id, expense_id, description, quantity, unit_price, amount, product_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.expenses (id, expense_number, title, description, category, amount, currency_id, tax_amount, total_amount, expense_date, due_date, payment_date, status, payment_method, user_id, approved_by_id, supplier_id, branch_id, account_id, receipt_number, reference, notes, created_at, updated_at, created_by_id, updated_by_id) FROM stdin;
\.


--
-- Data for Name: fiscal_years; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.fiscal_years (id, name_ar, name_en, start_date, end_date, is_current, is_closed, created_at, updated_at) FROM stdin;
1	السنة المالية 2025	Fiscal Year 2025	2025-01-01 00:00:00	2025-12-31 00:00:00	t	f	2025-07-01 19:44:16.058839	2025-07-01 19:44:16.05884
\.


--
-- Data for Name: hr_dashboard_metrics; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.hr_dashboard_metrics (id, metric_date, total_employees, active_employees, new_hires_month, terminations_month, average_attendance_rate, total_late_arrivals, total_overtime_hours, pending_leave_requests, approved_leaves_month, total_payroll_amount, average_salary, total_overtime_cost, pending_reviews, completed_reviews_month, average_performance_rating, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: inventory_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.inventory_items (id, product_id, warehouse_id, quantity_on_hand, quantity_reserved, quantity_ordered, last_cost, average_cost, created_at, updated_at) FROM stdin;
13	1	1	387.000	36.000	60.000	143.24	142.89	2025-07-02 20:44:33.758821+03	\N
14	1	2	454.000	21.000	56.000	118.85	56.07	2025-07-02 20:44:33.758821+03	\N
15	2	1	461.000	31.000	49.000	186.00	55.29	2025-07-02 20:44:33.758821+03	\N
16	2	2	101.000	49.000	33.000	124.84	123.94	2025-07-02 20:44:33.758821+03	\N
17	3	1	270.000	28.000	39.000	37.28	191.22	2025-07-02 20:44:33.758821+03	\N
18	3	2	331.000	14.000	49.000	167.79	39.72	2025-07-02 20:44:33.758821+03	\N
19	4	1	357.000	10.000	7.000	73.20	17.99	2025-07-02 20:44:33.758821+03	\N
20	4	2	424.000	49.000	24.000	61.33	11.57	2025-07-02 20:44:33.758821+03	\N
21	5	1	79.000	18.000	27.000	162.45	28.00	2025-07-02 20:44:33.758821+03	\N
22	5	2	345.000	11.000	64.000	162.71	93.12	2025-07-02 20:44:33.758821+03	\N
23	6	1	404.000	28.000	46.000	71.79	171.67	2025-07-02 20:44:33.758821+03	\N
24	6	2	475.000	48.000	68.000	173.33	30.89	2025-07-02 20:44:33.758821+03	\N
\.


--
-- Data for Name: invoice_payments; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.invoice_payments (id, payment_number, sales_invoice_id, purchase_invoice_id, payment_date, amount, currency_id, exchange_rate, payment_method, reference_number, bank_account, check_number, check_date, notes, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: item_categories; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.item_categories (id, code, name_ar, name_en, description_ar, description_en, parent_id, level, sort_order, is_active, created_at, updated_at) FROM stdin;
1	ELECTRONICS	الإلكترونيات	Electronics	الأجهزة الإلكترونية والكهربائية	Electronic and electrical devices	\N	1	10	t	2025-07-02 17:39:37.067897	2025-07-02 17:39:37.067901
2	COMPUTERS	أجهزة الكمبيوتر	Computers	أجهزة الكمبيوتر المحمولة والمكتبية	Laptops, desktops and computer systems	1	2	11	t	2025-07-02 17:39:37.067901	2025-07-02 17:39:37.067901
3	MOBILE	الهواتف المحمولة	Mobile Phones	الهواتف الذكية والأجهزة اللوحية	Smartphones and tablets	1	2	12	t	2025-07-02 17:39:37.067902	2025-07-02 17:39:37.067902
4	ACCESSORIES	الإكسسوارات	Accessories	إكسسوارات الكمبيوتر والهواتف	Computer and phone accessories	\N	1	20	t	2025-07-02 17:39:37.067902	2025-07-02 17:39:37.067902
5	NETWORKING	الشبكات	Networking	معدات الشبكات والاتصالات	Network and communication equipment	\N	1	30	t	2025-07-02 17:39:37.067903	2025-07-02 17:39:37.067903
\.


--
-- Data for Name: journal_entries; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.journal_entries (id, journal_id, currency_id, branch_id, entry_number, reference, reference_type, reference_id, entry_date, posting_date, description_ar, description_en, total_debit, total_credit, status, posted_by, posted_at, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: journal_lines; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.journal_lines (id, journal_entry_id, account_id, line_number, description_ar, description_en, debit_amount, credit_amount, created_at) FROM stdin;
\.


--
-- Data for Name: journals; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.journals (id, code, name_ar, name_en, journal_type, is_active, description_ar, description_en, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: leave_requests; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.leave_requests (id, employee_id, leave_type, start_date, end_date, total_days, reason, supporting_documents, status, requested_by, reviewed_by, approved_by, request_date, review_date, approval_date, employee_comments, manager_comments, hr_comments, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: migration_batches; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.migration_batches (id, batch_number, batch_name, description, status, start_time, end_time, total_entities, total_records, successful_records, failed_records, source_system, migration_config, error_log, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: migration_customers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.migration_customers (id, code, name_ar, name_en, email, phone, mobile, address_ar, address_en, city, region, postal_code, country, tax_number, currency, credit_limit, payment_terms, price_list_id, salesperson_id, assigned_region, outstanding_receivable, is_active, zoho_customer_id, zoho_deposit_account, zoho_last_sync, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: migration_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.migration_items (id, code, name_ar, name_en, description_ar, description_en, category_id, brand, model, specifications, unit_of_measure, cost_price_usd, cost_price_iqd, selling_price_usd, selling_price_iqd, track_inventory, reorder_level, reorder_quantity, weight, dimensions, is_active, is_serialized, is_batch_tracked, zoho_item_id, zoho_last_sync, created_at, updated_at, created_by) FROM stdin;
1	LAP-001	لاب توب ديل XPS 13	Dell XPS 13 Laptop	لاب توب ديل عالي الأداء بمعالج Intel Core i7	High-performance Dell laptop with Intel Core i7 processor	2	Dell	XPS 13	\N	PCS	800.000	1056000.000	1200.000	1584000.000	t	5.000	10.000	1.200	30.2 x 19.9 x 1.4 cm	t	f	f	\N	\N	2025-07-02 17:39:37.082414	2025-07-02 17:39:37.082417	\N
2	PHN-001	آيفون 15 برو	iPhone 15 Pro	هاتف آبل الذكي الجديد بتقنية A17 Pro	Latest Apple smartphone with A17 Pro chip	3	Apple	iPhone 15 Pro	\N	PCS	900.000	1188000.000	1399.000	1846680.000	t	3.000	5.000	0.187	14.67 x 7.09 x 0.83 cm	t	f	f	\N	\N	2025-07-02 17:39:37.082417	2025-07-02 17:39:37.082417	\N
3	MON-001	شاشة سامسونج 27 بوصة	Samsung 27" Monitor	شاشة سامسونج عالية الدقة 4K	Samsung 4K high-resolution monitor	1	Samsung	M7 27"	\N	PCS	250.000	330000.000	399.000	526680.000	t	2.000	5.000	4.500	61.2 x 36.3 x 20.6 cm	t	f	f	\N	\N	2025-07-02 17:39:37.082418	2025-07-02 17:39:37.082418	\N
4	ACC-001	ماوس لاسلكي لوجيتك	Logitech Wireless Mouse	ماوس لاسلكي عالي الدقة من لوجيتك	High-precision wireless mouse from Logitech	4	Logitech	MX Master 3S	\N	PCS	15.000	19800.000	29.990	39587.000	t	10.000	20.000	0.141	12.4 x 8.4 x 5.1 cm	t	f	f	\N	\N	2025-07-02 17:39:37.082418	2025-07-02 17:39:37.082419	\N
5	NET-001	راوتر TP-Link	TP-Link Router	راوتر لاسلكي عالي السرعة	High-speed wireless router	5	TP-Link	Archer AX50	\N	PCS	75.000	99000.000	129.000	170280.000	t	5.000	10.000	0.680	26.0 x 13.5 x 3.8 cm	t	f	f	\N	\N	2025-07-02 17:39:37.082419	2025-07-02 17:39:37.082419	\N
6	CBL-001	كابل USB-C	USB-C Cable	كابل USB-C عالي الجودة طول متر واحد	High-quality USB-C cable 1 meter length	4	Anker	PowerLine III	\N	PCS	5.000	6600.000	12.990	17147.000	t	20.000	50.000	0.050	100 cm length	t	f	f	\N	\N	2025-07-02 17:39:37.08242	2025-07-02 17:39:37.08242	\N
\.


--
-- Data for Name: migration_records; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.migration_records (id, batch_id, entity_type, source_id, source_data, target_id, status, processed_at, error_message, retry_count, requires_manual_review, manual_review_notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: migration_stock; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.migration_stock (id, item_id, warehouse_id, quantity_on_hand, quantity_reserved, quantity_available, average_cost, last_cost, reorder_level, reorder_quantity, max_stock_level, last_movement_date, last_movement_type, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: migration_vendors; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.migration_vendors (id, code, name_ar, name_en, email, phone, contact_person, address_ar, address_en, city, country, tax_number, currency, payment_terms, outstanding_payable, is_active, zoho_vendor_id, zoho_last_sync, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: money_transfers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.money_transfers (id, transfer_uuid, salesperson_id, salesperson_name, amount_usd, amount_iqd, exchange_rate, gross_sales, commission_rate, calculated_commission, claimed_commission, commission_verified, transfer_platform, platform_reference, transfer_fee, transfer_datetime, gps_latitude, gps_longitude, location_name, receipt_photo_url, receipt_verified, status, money_received, received_datetime, is_suspicious, fraud_alert_reason, manager_approval_required, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: payroll_records; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.payroll_records (id, employee_id, payroll_month, payroll_year, pay_period_start, pay_period_end, base_salary, commission_amount, overtime_amount, bonus_amount, allowances, gross_salary, tax_deduction, social_security, insurance_deduction, loan_deduction, other_deductions, total_deductions, net_salary, working_days, actual_working_days, total_hours_worked, overtime_hours, payment_method, bank_account, payment_date, payment_reference, status, notes, created_at, updated_at, created_by, approved_by, approved_at) FROM stdin;
\.


--
-- Data for Name: performance_reviews; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.performance_reviews (id, employee_id, review_period_start, review_period_end, review_type, overall_rating, technical_skills, communication_skills, teamwork, leadership, punctuality, productivity, goals_achieved, goals_missed, new_goals, employee_self_assessment, manager_feedback, hr_comments, development_plan, salary_increase_recommended, recommended_increase_amount, recommended_increase_percentage, is_completed, employee_acknowledged, review_date, employee_acknowledgment_date, reviewed_by, hr_reviewed_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: pos_discounts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pos_discounts (id, code, name_ar, name_en, discount_type, discount_value, min_amount, max_amount, min_quantity, applicable_products, applicable_categories, valid_from, valid_to, usage_limit, usage_count, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: pos_payments; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pos_payments (id, transaction_id, payment_method, amount, card_type, card_last_four, approval_code, reference_number, mobile_number, mobile_provider, mobile_reference, credit_reference, voucher_code, voucher_type, notes, created_at) FROM stdin;
\.


--
-- Data for Name: pos_promotions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pos_promotions (id, code, name_ar, name_en, description_ar, description_en, promotion_type, rules, valid_from, valid_to, usage_limit, usage_count, priority, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: pos_sessions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pos_sessions (id, session_number, terminal_id, currency_id, user_id, start_time, end_time, status, opening_cash_amount, opening_notes, closing_cash_amount, closing_card_amount, closing_mobile_amount, closing_total_amount, closing_notes, total_sales, total_refunds, total_discounts, total_tax, transaction_count, closed_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: pos_terminals; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pos_terminals (id, terminal_code, name_ar, name_en, branch_id, warehouse_id, receipt_printer, barcode_scanner, cash_drawer, display, default_tax_rate, allow_discount, max_discount_percent, allow_negative_stock, auto_print_receipt, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: pos_transaction_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pos_transaction_items (id, transaction_id, product_id, line_number, quantity, unit_price, discount_amount, discount_percent, tax_amount, tax_percent, line_total, notes, created_at) FROM stdin;
\.


--
-- Data for Name: pos_transactions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pos_transactions (id, transaction_number, terminal_id, session_id, customer_id, sales_order_id, transaction_type, transaction_date, subtotal, discount_amount, discount_percent, tax_amount, tax_percent, total_amount, amount_paid, change_amount, receipt_number, notes, void_reason, voided_at, voided_by, cashier_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: positions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.positions (id, code, title_ar, title_en, description_ar, description_en, min_salary, max_salary, level, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: price_history; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.price_history (id, product_id, pricing_list_id, old_price, new_price, update_type, notes, updated_by, created_at) FROM stdin;
\.


--
-- Data for Name: price_list_categories; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.price_list_categories (id, pricing_list_id, customer_category, created_at) FROM stdin;
\.


--
-- Data for Name: price_list_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.price_list_items (id, price_list_id, item_id, unit_price, discount_percentage, minimum_quantity, is_active, created_at, updated_at) FROM stdin;
1	1	1	146.320	0.00	2.000	t	2025-07-02 17:45:26.173332	2025-07-02 17:45:26.173335
2	1	2	30.570	0.00	7.000	t	2025-07-02 17:45:26.173335	2025-07-02 17:45:26.173336
3	1	3	29.880	0.00	10.000	t	2025-07-02 17:45:26.173336	2025-07-02 17:45:26.173336
4	1	4	89.810	0.00	10.000	t	2025-07-02 17:45:26.173336	2025-07-02 17:45:26.173336
5	1	5	254.950	0.00	10.000	t	2025-07-02 17:45:26.173337	2025-07-02 17:45:26.173337
6	2	1	137.450	0.00	5.000	t	2025-07-02 17:45:26.173337	2025-07-02 17:45:26.173337
7	2	2	135.160	0.00	3.000	t	2025-07-02 17:45:26.173337	2025-07-02 17:45:26.173337
8	2	3	227.350	0.00	9.000	t	2025-07-02 17:45:26.173338	2025-07-02 17:45:26.173338
9	2	4	89.150	0.00	6.000	t	2025-07-02 17:45:26.173338	2025-07-02 17:45:26.173338
10	2	5	168.620	0.00	3.000	t	2025-07-02 17:45:26.173338	2025-07-02 17:45:26.173338
11	3	1	316.450	0.00	4.000	t	2025-07-02 17:45:26.173339	2025-07-02 17:45:26.173339
12	3	2	215.220	0.00	7.000	t	2025-07-02 17:45:26.173339	2025-07-02 17:45:26.173339
13	3	3	56.880	0.00	1.000	t	2025-07-02 17:45:26.173339	2025-07-02 17:45:26.173339
14	3	4	115.020	0.00	5.000	t	2025-07-02 17:45:26.17334	2025-07-02 17:45:26.17334
15	3	5	79.330	0.00	5.000	t	2025-07-02 17:45:26.17334	2025-07-02 17:45:26.17334
\.


--
-- Data for Name: price_lists; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.price_lists (id, code, name_ar, name_en, description_ar, description_en, currency, is_default, is_active, effective_from, effective_to, zoho_price_list_id, zoho_last_sync, created_at, updated_at, created_by) FROM stdin;
1	RETAIL	قائمة أسعار التجزئة	Retail Price List	قائمة الأسعار الأساسية للعملاء	Basic price list for customers	USD	f	t	\N	\N	\N	\N	2025-07-02 17:45:26.166421	2025-07-02 17:45:26.166424	\N
2	WHOLESALE	قائمة أسعار الجملة	Wholesale Price List	قائمة أسعار خاصة لعملاء الجملة	Special price list for wholesale customers	USD	f	t	\N	\N	\N	\N	2025-07-02 17:45:26.166424	2025-07-02 17:45:26.166424	\N
3	PREMIUM	قائمة الأسعار المميزة	Premium Price List	قائمة أسعار للعملاء المميزين	Price list for premium customers	USD	f	t	\N	\N	\N	\N	2025-07-02 17:45:26.166425	2025-07-02 17:45:26.166425	\N
\.


--
-- Data for Name: price_negotiation_requests; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.price_negotiation_requests (id, customer_id, product_id, current_price, requested_price, quantity, justification, status, valid_until, approved_by, approved_at, created_at) FROM stdin;
\.


--
-- Data for Name: pricing_lists; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.pricing_lists (id, name, price_list_type, description, minimum_order_value, discount_percentage, is_active, valid_from, valid_to, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: product_prices; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.product_prices (id, product_id, pricing_list_id, price, discount_percentage, minimum_quantity, is_negotiable, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.products (id, sku, name, description, category_id, unit_price, cost_price, unit_of_measure, min_stock_level, max_stock_level, reorder_point, barcode, is_active, is_trackable, created_at, updated_at, name_ar, description_ar, image_url, images, videos, weight, dimensions, color, size, brand, model, is_digital, is_featured, meta_title, meta_description, tags) FROM stdin;
1	LAP-001	Dell XPS 13 Laptop	High-performance Dell laptop with Intel Core i7 processor	1	1200.00	800.00	PCS	0	\N	5	\N	t	t	2025-07-02 20:44:02.376299+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2	PHN-001	iPhone 15 Pro	Latest Apple smartphone with A17 Pro chip	1	1399.00	900.00	PCS	0	\N	3	\N	t	t	2025-07-02 20:44:02.376299+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3	MON-001	Samsung 27" Monitor	Samsung 4K high-resolution monitor	1	399.00	250.00	PCS	0	\N	2	\N	t	t	2025-07-02 20:44:02.376299+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4	ACC-001	Logitech Wireless Mouse	High-precision wireless mouse from Logitech	1	29.99	15.00	PCS	0	\N	10	\N	t	t	2025-07-02 20:44:02.376299+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
5	NET-001	TP-Link Router	High-speed wireless router	1	129.00	75.00	PCS	0	\N	5	\N	t	t	2025-07-02 20:44:02.376299+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6	CBL-001	USB-C Cable	High-quality USB-C cable 1 meter length	1	12.99	5.00	PCS	0	\N	20	\N	t	t	2025-07-02 20:44:02.376299+03	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7	TEST-NEW-001	Test Updated Product	\N	1	75.00	\N	PCS	0	\N	0	\N	f	t	2025-07-03 19:40:14.091318+03	2025-07-03 19:40:27.308581+03	\N	\N	\N	[]	[]	\N	null	\N	\N	\N	\N	f	f	\N	\N	[]
8	TEST-CLICK-001	Test Click Product Updated	\N	1	30.00	\N	PCS	0	\N	0	\N	f	t	2025-07-03 19:46:35.4994+03	2025-07-03 19:46:47.669021+03	\N	\N	\N	[]	[]	\N	null	\N	\N	\N	\N	f	f	\N	\N	[]
9	TEST-CLICK-UI-001	Test Click UI Product Updated	\N	1	35.00	\N	PCS	0	\N	0	\N	f	t	2025-07-03 19:53:19.77526+03	2025-07-03 19:53:33.283125+03	\N	\N	\N	[]	[]	\N	null	\N	\N	\N	\N	f	f	\N	\N	[]
\.


--
-- Data for Name: purchase_invoice_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.purchase_invoice_items (id, invoice_id, product_id, purchase_item_id, quantity, unit_cost, discount_percentage, discount_amount, line_total, description, notes) FROM stdin;
\.


--
-- Data for Name: purchase_invoices; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.purchase_invoices (id, invoice_number, supplier_invoice_number, supplier_id, purchase_order_id, branch_id, warehouse_id, invoice_date, due_date, received_date, currency_id, exchange_rate, invoice_type, status, payment_terms, subtotal, discount_percentage, discount_amount, tax_percentage, tax_amount, shipping_amount, total_amount, paid_amount, notes, internal_notes, payment_method, reference_number, created_by, created_at, updated_at, received_at, cancelled_at) FROM stdin;
\.


--
-- Data for Name: purchase_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.purchase_items (id, purchase_order_id, product_id, quantity, unit_cost, discount_percentage, discount_amount, line_total, received_quantity, notes) FROM stdin;
\.


--
-- Data for Name: purchase_orders; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.purchase_orders (id, order_number, supplier_id, branch_id, warehouse_id, order_date, expected_delivery_date, actual_delivery_date, status, payment_status, payment_method, subtotal, discount_percentage, discount_amount, tax_percentage, tax_amount, total_amount, paid_amount, notes, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.roles (id, name) FROM stdin;
1	Admin
2	Manager
3	Employee
4	Travel Salesperson
5	Partner Salesman
6	Retailerman
7	Accountant
8	HR Specialist
9	Warehouse Staff
\.


--
-- Data for Name: sales_invoice_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.sales_invoice_items (id, invoice_id, product_id, sales_item_id, quantity, unit_price, discount_percentage, discount_amount, line_total, description, notes) FROM stdin;
\.


--
-- Data for Name: sales_invoices; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.sales_invoices (id, invoice_number, customer_id, sales_order_id, branch_id, warehouse_id, invoice_date, due_date, currency_id, exchange_rate, invoice_type, status, payment_terms, subtotal, discount_percentage, discount_amount, tax_percentage, tax_amount, shipping_amount, total_amount, paid_amount, notes, internal_notes, payment_method, reference_number, is_recurring, recurring_frequency, parent_invoice_id, created_by, created_at, updated_at, issued_at, cancelled_at) FROM stdin;
\.


--
-- Data for Name: sales_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.sales_items (id, sales_order_id, product_id, quantity, unit_price, discount_percentage, discount_amount, line_total, delivered_quantity, notes) FROM stdin;
\.


--
-- Data for Name: sales_orders; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.sales_orders (id, order_number, customer_id, branch_id, warehouse_id, order_date, expected_delivery_date, actual_delivery_date, status, payment_status, payment_method, subtotal, discount_percentage, discount_amount, tax_percentage, tax_amount, total_amount, paid_amount, notes, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: salesperson_regions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.salesperson_regions (id, user_id, region, is_primary, is_active, assigned_date, created_at, assigned_by) FROM stdin;
\.


--
-- Data for Name: stock_movements; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.stock_movements (id, inventory_item_id, movement_type, reference_type, reference_id, quantity, unit_cost, notes, created_by, created_at) FROM stdin;
1	16	ADJUSTMENT	SALE	38	-3.000	164.91	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
2	13	IN	SALE	24	65.000	19.00	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
3	15	ADJUSTMENT	SALE	4	-4.000	122.53	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
4	15	ADJUSTMENT	PURCHASE	33	-20.000	115.25	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
5	14	ADJUSTMENT	SALE	21	15.000	87.77	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
6	13	IN	SALE	57	96.000	105.38	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
7	16	ADJUSTMENT	ADJUSTMENT	73	18.000	109.78	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
8	23	ADJUSTMENT	PURCHASE	50	-11.000	33.61	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
9	21	OUT	TRANSFER	99	-27.000	16.70	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
10	16	IN	SALE	61	21.000	23.87	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
11	20	IN	ADJUSTMENT	40	43.000	13.47	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
12	15	IN	ADJUSTMENT	58	89.000	117.94	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
13	22	OUT	SALE	60	-5.000	12.76	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
14	18	OUT	SALE	85	-24.000	137.28	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
15	17	ADJUSTMENT	SALE	83	-1.000	133.38	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
16	19	ADJUSTMENT	SALE	72	9.000	12.48	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
17	17	OUT	PURCHASE	69	-24.000	141.81	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
18	21	OUT	SALE	90	-36.000	134.49	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
19	15	OUT	SALE	10	-47.000	11.25	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
20	22	ADJUSTMENT	PURCHASE	8	-10.000	194.49	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
21	16	OUT	ADJUSTMENT	32	-14.000	177.81	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
22	21	ADJUSTMENT	TRANSFER	13	-8.000	82.44	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
23	13	OUT	TRANSFER	60	-29.000	186.04	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
24	23	ADJUSTMENT	SALE	6	-12.000	62.72	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
25	20	ADJUSTMENT	SALE	6	-19.000	61.17	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
26	16	ADJUSTMENT	TRANSFER	8	-18.000	71.92	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
27	24	OUT	ADJUSTMENT	27	-7.000	17.99	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
28	18	IN	TRANSFER	36	46.000	190.53	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
29	17	OUT	TRANSFER	87	-25.000	179.73	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
30	22	ADJUSTMENT	ADJUSTMENT	12	-16.000	37.23	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
31	24	OUT	SALE	15	-7.000	46.63	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
32	14	IN	ADJUSTMENT	17	97.000	18.87	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
33	14	ADJUSTMENT	PURCHASE	8	-3.000	155.65	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
34	14	ADJUSTMENT	PURCHASE	87	-1.000	10.87	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
35	13	OUT	PURCHASE	100	-18.000	13.84	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
36	19	OUT	ADJUSTMENT	56	-21.000	77.91	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
37	15	OUT	ADJUSTMENT	66	-45.000	50.60	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
38	14	OUT	TRANSFER	34	-38.000	187.63	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
39	14	ADJUSTMENT	SALE	7	9.000	178.62	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
40	23	ADJUSTMENT	TRANSFER	58	-13.000	142.32	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
41	24	OUT	ADJUSTMENT	91	-5.000	87.69	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
42	20	IN	TRANSFER	98	81.000	70.19	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
43	23	OUT	PURCHASE	87	-31.000	63.15	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
44	21	IN	ADJUSTMENT	81	94.000	14.40	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
45	13	IN	ADJUSTMENT	64	61.000	101.48	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
46	14	OUT	ADJUSTMENT	40	-22.000	90.62	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
47	14	ADJUSTMENT	SALE	80	11.000	17.82	حركة ADJUSTMENT توضيحية	1	2025-07-02 20:44:33.774062+03
48	22	IN	TRANSFER	8	19.000	143.96	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
49	15	IN	ADJUSTMENT	90	58.000	41.77	حركة IN توضيحية	1	2025-07-02 20:44:33.774062+03
50	13	OUT	TRANSFER	56	-22.000	56.41	حركة OUT توضيحية	1	2025-07-02 20:44:33.774062+03
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.suppliers (id, supplier_code, name, company_name, phone, email, address, city, country, tax_number, payment_terms, is_active, notes, created_at, updated_at) FROM stdin;
1	SUPP-0001	شركة المواد الخام الدولية	International Raw Materials Co.	+964-1-5555555	supply@rawmaterials-intl.com	المنطقة الصناعية، بغداد	بغداد	العراق	TAX-SUPP-001	30	t	مورد المواد الخام والمستلزمات الصناعية	2025-07-02 17:40:36.147891+03	\N
2	SUPP-0002	مؤسسة الأجهزة المتقدمة	Advanced Equipment Enterprise	+964-66-3333333	info@advanced-equipment.iq	شارع الجامعة، أربيل	أربيل	العراق	TAX-SUPP-002	45	t	مورد الأجهزة والمعدات المتخصصة	2025-07-02 17:40:36.152589+03	\N
\.


--
-- Data for Name: transfer_platforms; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.transfer_platforms (id, platform_name, platform_code, has_api, api_endpoint, is_active, created_at) FROM stdin;
1	ALTaif Bank	ALT	f	\N	t	2025-07-05 22:43:30.19771
2	ZAIN Cash	ZAIN	t	https://api.zaincash.iq	t	2025-07-05 22:43:30.19771
3	SuperQi	SUPER	t	https://api.superqi.com	t	2025-07-05 22:43:30.19771
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.users (id, name, email, password, role_id, branch_id, employee_code, phone, is_salesperson, is_active, created_at, updated_at, last_login) FROM stdin;
1	أحمد السالمي	ahmed.salemi@tsh.com	$2b$12$6jYbBx1p9E2yZ1M6Ytgg2eB1IrFFgmPkmO4QsiHnIWnEvkIUve8s6	4	3	TSP-001	+964-770-1234567	t	t	2025-07-02 15:35:16.04692	2025-07-02 15:35:16.047727	\N
2	فاطمة الكاظمي	fatima.kazemi@tsh.com	$2b$12$o4yGinrXrPZRVpt1A8zhRetpnIodLZ42JoLq.X7ViXW69Q3PPGcDu	4	4	TSP-002	+964-770-2345678	t	t	2025-07-02 15:35:16.22557	2025-07-02 15:35:16.225855	\N
3	محمد الربيعي	mohammed.rabiee@tsh.com	$2b$12$p2k.PE7YxwJZhirXqxz/mODjwppKu.AgDt67b6IDk.uLiHfD3nioa	4	4	TSP-003	+964-770-3456789	t	t	2025-07-02 15:35:16.396161	2025-07-02 15:35:16.396431	\N
4	زينب العلوي	zeinab.alawi@tsh.com	$2b$12$Pcx0QJbEe7VPf05OMMDgWup0yOz79G52F9DBjSHV0GvNsE/ul2D7.	4	2	TSP-004	+964-770-4567890	t	t	2025-07-02 15:35:16.566845	2025-07-02 15:35:16.567104	\N
5	عماد الشمري	emad.shamari@tsh.com	$2b$12$NC3fd7IBla/T5K5k9fHyQuQxsQ.ciKoBrqJI.gHDwA6D12/sSIkC.	5	1	PSM-001	+964-771-1234567	t	t	2025-07-02 15:35:16.738272	2025-07-02 15:35:16.738543	\N
6	نور الدين محسن	nooraldin.mohsen@tsh.com	$2b$12$ID/7Aka/5wNxM1es95zS..AL7v6LIbeePLT0RIyKRGFTeWXkD9y/a	5	3	PSM-002	+964-771-2345678	t	t	2025-07-02 15:35:16.908406	2025-07-02 15:35:16.908664	\N
7	سعاد الموسوي	suaad.mousawi@tsh.com	$2b$12$TIn7tCB5Mz8pXTshGlyRY.F0FXfpHg56ZydJOWHRYBavSPYeLWAa2	5	3	PSM-003	+964-771-3456789	t	t	2025-07-02 15:35:17.0793	2025-07-02 15:35:17.079577	\N
8	خالد البصري	khaled.basri@tsh.com	$2b$12$52Aii2lVAF3A.zIcFQLD4.lNOhXJ2tC6iMDIbXTZBtw1BbuItK3qS	6	2	RTM-001	+964-772-1234567	t	t	2025-07-02 15:35:17.24993	2025-07-02 15:35:17.250182	\N
9	مريم الأنصاري	mariam.ansari@tsh.com	$2b$12$ZqGC4AjQ.4iAn1nlA1jlq.mz4AkFWb.7SbtgKKM/GD35Fs6X8dt8O	6	2	RTM-002	+964-772-2345678	t	t	2025-07-02 15:35:17.419297	2025-07-02 15:35:17.41957	\N
10	يوسف الطائي	yousif.taee@tsh.com	$2b$12$nbF.GXdysa1BUae53uOdn.PrapOV.ohDkoHS9xL7IZsPXzYStTm9O	6	2	RTM-003	+964-772-3456789	t	t	2025-07-02 15:35:17.590331	2025-07-02 15:35:17.5906	\N
11	عبد الله الحسيني	abdullah.hussaini@tsh.com	$2b$12$LXAB/xM8UTvgVnxe17Sb4.5elVx4Mvk5w4rrRUEOk5dMEGh/ldmvq	2	4	MGR-001	+964-773-1234567	f	t	2025-07-02 15:35:17.760565	2025-07-02 15:35:17.760852	\N
12	أسماء الجبوري	asmaa.juboori@tsh.com	$2b$12$U2xykyk3fFt9QpSETQlfA.kOJtH6KogKxweBUMgezMCmS.sJg6K0.	7	2	ACC-001	+964-773-2345678	f	t	2025-07-02 15:35:17.931396	2025-07-02 15:35:17.931678	\N
13	حسام الدليمي	hussam.dalimi@tsh.com	$2b$12$YhUYykTe6fPNn1OgSA89geI/KXfgeipL8XIAC5ZpKqjaV2fnBfxy6	3	1	EMP-001	+964-773-3456789	f	t	2025-07-02 15:35:18.101644	2025-07-02 15:35:18.101932	\N
14	رشا النعيمي	rasha.naeemi@tsh.com	$2b$12$zLgXhCRnFl.4GUIpWAji8u6TI5XwJxlCkg8bbg9sKVhicO2zXIn4C	8	3	HRS-001	+964-773-4567890	f	t	2025-07-02 15:35:18.272366	2025-07-02 15:35:18.272636	\N
15	علي الماجدي	ali.majidi@tsh.com	$2b$12$cwKJmSg4tdMiQNZYp/1Ux..g6EPF15pN8hriueZ9os4RETmTVCyl6	3	1	EMP-002	+964-774-1234567	f	t	2025-07-02 15:35:18.442313	2025-07-02 15:35:18.4426	\N
16	ليلى السلطاني	layla.sultani@tsh.com	$2b$12$ZYDXk2rMx86s1FVQWDgtpOJDfn33KD5tCksilCZPu9SPGPdWwsYFm	2	4	MGR-002	+964-774-2345678	f	t	2025-07-02 15:35:18.613499	2025-07-02 15:35:18.613779	\N
17	Ahmed Kareem	ahmed.kareem@tsh.com	$2b$12$4SL2YN9hgOp2ZTtsdbVteuT3U0E.wUy0kFuqXPTtt3pVBXzgdoJw.	4	5	\N	\N	f	t	2025-07-02 17:39:48.163693	2025-07-02 17:39:48.163696	\N
18	Ayad Fadel	ayad.fadel@tsh.com	$2b$12$tpqdqjhMYuqOx5CuKA425.gStdQE3EZx4fRDJ5Wm4ZgoRky.YqogO	4	5	\N	\N	f	t	2025-07-02 17:39:48.333109	2025-07-02 17:39:48.333111	\N
19	Haider Adnan	haider.adnan@tsh.com	$2b$12$X1z5z7xbrQohd2c8HQ9RPeHFN5wSY4EggBMOFka7LgMtOuQe2C1mq	4	6	\N	\N	f	t	2025-07-02 17:39:48.505512	2025-07-02 17:39:48.505514	\N
20	Ayoob Myser	ayoob.myser@tsh.com	$2b$12$ybyzsvI41HUeti12RgNOi.i.hIB6EQ2tt02FRwFtkc9YKLANNnyGq	4	6	\N	\N	f	t	2025-07-02 17:39:48.6761	2025-07-02 17:39:48.676103	\N
21	Hussien Hgran	hussien.hgran@tsh.com	$2b$12$kT47Wq71WVpzX5LD0S.gr.azG7F/dbAkmShNYrpVRwK4Mr97cDiXm	4	5	\N	\N	f	t	2025-07-02 17:39:48.845295	2025-07-02 17:39:48.845297	\N
22	TSH Admin	admin@tsh.com	$2b$12$/7MA0uuBSaVR.vOzjLF6ku9lVvM22OXrJdPMLnxyJ3Okn3GtnfkzW	1	5	\N	\N	f	t	2025-07-02 17:39:49.015492	2025-07-02 17:39:49.015494	\N
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.warehouses (id, name, branch_id) FROM stdin;
1	Main Wholesale Warehouse	5
2	TSH Dora Storage	6
\.


--
-- Data for Name: whatsapp_auto_responses; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.whatsapp_auto_responses (id, triggers, response_text, language, active, usage_count, created_at) FROM stdin;
\.


--
-- Data for Name: whatsapp_broadcasts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.whatsapp_broadcasts (id, broadcast_id, template_name, language, total_recipients, sent_count, failed_count, status, created_at, completed_at) FROM stdin;
\.


--
-- Data for Name: whatsapp_messages; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.whatsapp_messages (id, phone_number, message_type, content, direction, language, whatsapp_message_id, media_url, delivery_status, api_response, status_updated_at, created_at) FROM stdin;
\.


--
-- Name: accounting_periods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.accounting_periods_id_seq', 1, false);


--
-- Name: accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.accounts_id_seq', 1, false);


--
-- Name: ai_conversation_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.ai_conversation_messages_id_seq', 1, false);


--
-- Name: ai_conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.ai_conversations_id_seq', 1, false);


--
-- Name: ai_generated_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.ai_generated_orders_id_seq', 1, false);


--
-- Name: ai_support_tickets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.ai_support_tickets_id_seq', 1, false);


--
-- Name: attendance_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.attendance_records_id_seq', 1, false);


--
-- Name: branches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.branches_id_seq', 6, true);


--
-- Name: cash_boxes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.cash_boxes_id_seq', 1, false);


--
-- Name: cash_flow_summaries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.cash_flow_summaries_id_seq', 1, false);


--
-- Name: cash_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.cash_transactions_id_seq', 1, false);


--
-- Name: cash_transfers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.cash_transfers_id_seq', 1, false);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.categories_id_seq', 1, true);


--
-- Name: chart_of_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.chart_of_accounts_id_seq', 5, true);


--
-- Name: currencies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.currencies_id_seq', 2, true);


--
-- Name: customer_price_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.customer_price_categories_id_seq', 1, false);


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.customers_id_seq', 8, true);


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.departments_id_seq', 1, false);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.employees_id_seq', 1, false);


--
-- Name: exchange_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.exchange_rates_id_seq', 1, false);


--
-- Name: expense_attachments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.expense_attachments_id_seq', 1, false);


--
-- Name: expense_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.expense_items_id_seq', 1, false);


--
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.expenses_id_seq', 1, false);


--
-- Name: fiscal_years_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.fiscal_years_id_seq', 1, true);


--
-- Name: hr_dashboard_metrics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.hr_dashboard_metrics_id_seq', 1, false);


--
-- Name: inventory_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.inventory_items_id_seq', 24, true);


--
-- Name: invoice_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.invoice_payments_id_seq', 1, false);


--
-- Name: item_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.item_categories_id_seq', 5, true);


--
-- Name: journal_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.journal_entries_id_seq', 1, false);


--
-- Name: journal_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.journal_lines_id_seq', 1, false);


--
-- Name: journals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.journals_id_seq', 1, false);


--
-- Name: leave_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.leave_requests_id_seq', 1, false);


--
-- Name: migration_batches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.migration_batches_id_seq', 1, false);


--
-- Name: migration_customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.migration_customers_id_seq', 1, false);


--
-- Name: migration_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.migration_items_id_seq', 6, true);


--
-- Name: migration_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.migration_records_id_seq', 1, false);


--
-- Name: migration_stock_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.migration_stock_id_seq', 1, false);


--
-- Name: migration_vendors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.migration_vendors_id_seq', 1, false);


--
-- Name: money_transfers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.money_transfers_id_seq', 1, false);


--
-- Name: payroll_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.payroll_records_id_seq', 1, false);


--
-- Name: performance_reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.performance_reviews_id_seq', 1, false);


--
-- Name: pos_discounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pos_discounts_id_seq', 1, false);


--
-- Name: pos_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pos_payments_id_seq', 1, false);


--
-- Name: pos_promotions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pos_promotions_id_seq', 1, false);


--
-- Name: pos_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pos_sessions_id_seq', 1, false);


--
-- Name: pos_terminals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pos_terminals_id_seq', 1, false);


--
-- Name: pos_transaction_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pos_transaction_items_id_seq', 1, false);


--
-- Name: pos_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pos_transactions_id_seq', 1, false);


--
-- Name: positions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.positions_id_seq', 1, false);


--
-- Name: price_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.price_history_id_seq', 1, false);


--
-- Name: price_list_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.price_list_categories_id_seq', 1, false);


--
-- Name: price_list_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.price_list_items_id_seq', 15, true);


--
-- Name: price_lists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.price_lists_id_seq', 3, true);


--
-- Name: price_negotiation_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.price_negotiation_requests_id_seq', 1, false);


--
-- Name: pricing_lists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.pricing_lists_id_seq', 1, false);


--
-- Name: product_prices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.product_prices_id_seq', 1, false);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.products_id_seq', 9, true);


--
-- Name: purchase_invoice_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.purchase_invoice_items_id_seq', 1, false);


--
-- Name: purchase_invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.purchase_invoices_id_seq', 1, false);


--
-- Name: purchase_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.purchase_items_id_seq', 1, false);


--
-- Name: purchase_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.purchase_orders_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.roles_id_seq', 9, true);


--
-- Name: sales_invoice_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.sales_invoice_items_id_seq', 1, false);


--
-- Name: sales_invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.sales_invoices_id_seq', 1, false);


--
-- Name: sales_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.sales_items_id_seq', 1, false);


--
-- Name: sales_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.sales_orders_id_seq', 1, false);


--
-- Name: salesperson_regions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.salesperson_regions_id_seq', 1, false);


--
-- Name: stock_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.stock_movements_id_seq', 50, true);


--
-- Name: suppliers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.suppliers_id_seq', 2, true);


--
-- Name: transfer_platforms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.transfer_platforms_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.users_id_seq', 22, true);


--
-- Name: warehouses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.warehouses_id_seq', 2, true);


--
-- Name: whatsapp_auto_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.whatsapp_auto_responses_id_seq', 1, false);


--
-- Name: whatsapp_broadcasts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.whatsapp_broadcasts_id_seq', 1, false);


--
-- Name: whatsapp_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.whatsapp_messages_id_seq', 1, false);


--
-- Name: accounting_periods accounting_periods_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accounting_periods
    ADD CONSTRAINT accounting_periods_pkey PRIMARY KEY (id);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: ai_conversation_messages ai_conversation_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_conversation_messages
    ADD CONSTRAINT ai_conversation_messages_pkey PRIMARY KEY (id);


--
-- Name: ai_conversations ai_conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_conversations
    ADD CONSTRAINT ai_conversations_pkey PRIMARY KEY (id);


--
-- Name: ai_generated_orders ai_generated_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_generated_orders
    ADD CONSTRAINT ai_generated_orders_pkey PRIMARY KEY (id);


--
-- Name: ai_support_tickets ai_support_tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_support_tickets
    ADD CONSTRAINT ai_support_tickets_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attendance_records attendance_records_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.attendance_records
    ADD CONSTRAINT attendance_records_pkey PRIMARY KEY (id);


--
-- Name: branches branches_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_pkey PRIMARY KEY (id);


--
-- Name: cash_boxes cash_boxes_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_boxes
    ADD CONSTRAINT cash_boxes_pkey PRIMARY KEY (id);


--
-- Name: cash_flow_summaries cash_flow_summaries_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_flow_summaries
    ADD CONSTRAINT cash_flow_summaries_pkey PRIMARY KEY (id);


--
-- Name: cash_transactions cash_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transactions
    ADD CONSTRAINT cash_transactions_pkey PRIMARY KEY (id);


--
-- Name: cash_transfers cash_transfers_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transfers
    ADD CONSTRAINT cash_transfers_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: chart_of_accounts chart_of_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT chart_of_accounts_pkey PRIMARY KEY (id);


--
-- Name: currencies currencies_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.currencies
    ADD CONSTRAINT currencies_pkey PRIMARY KEY (id);


--
-- Name: customer_price_categories customer_price_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.customer_price_categories
    ADD CONSTRAINT customer_price_categories_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: employees employees_national_id_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_national_id_key UNIQUE (national_id);


--
-- Name: employees employees_passport_number_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_passport_number_key UNIQUE (passport_number);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: exchange_rates exchange_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_pkey PRIMARY KEY (id);


--
-- Name: expense_attachments expense_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expense_attachments
    ADD CONSTRAINT expense_attachments_pkey PRIMARY KEY (id);


--
-- Name: expense_items expense_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expense_items
    ADD CONSTRAINT expense_items_pkey PRIMARY KEY (id);


--
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- Name: fiscal_years fiscal_years_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.fiscal_years
    ADD CONSTRAINT fiscal_years_pkey PRIMARY KEY (id);


--
-- Name: hr_dashboard_metrics hr_dashboard_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.hr_dashboard_metrics
    ADD CONSTRAINT hr_dashboard_metrics_pkey PRIMARY KEY (id);


--
-- Name: inventory_items inventory_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_pkey PRIMARY KEY (id);


--
-- Name: invoice_payments invoice_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_payments
    ADD CONSTRAINT invoice_payments_pkey PRIMARY KEY (id);


--
-- Name: item_categories item_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.item_categories
    ADD CONSTRAINT item_categories_pkey PRIMARY KEY (id);


--
-- Name: journal_entries journal_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_pkey PRIMARY KEY (id);


--
-- Name: journal_lines journal_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_lines
    ADD CONSTRAINT journal_lines_pkey PRIMARY KEY (id);


--
-- Name: journals journals_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journals
    ADD CONSTRAINT journals_pkey PRIMARY KEY (id);


--
-- Name: leave_requests leave_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_pkey PRIMARY KEY (id);


--
-- Name: migration_batches migration_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_batches
    ADD CONSTRAINT migration_batches_pkey PRIMARY KEY (id);


--
-- Name: migration_customers migration_customers_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_customers
    ADD CONSTRAINT migration_customers_pkey PRIMARY KEY (id);


--
-- Name: migration_items migration_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_items
    ADD CONSTRAINT migration_items_pkey PRIMARY KEY (id);


--
-- Name: migration_records migration_records_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_records
    ADD CONSTRAINT migration_records_pkey PRIMARY KEY (id);


--
-- Name: migration_stock migration_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_stock
    ADD CONSTRAINT migration_stock_pkey PRIMARY KEY (id);


--
-- Name: migration_vendors migration_vendors_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_vendors
    ADD CONSTRAINT migration_vendors_pkey PRIMARY KEY (id);


--
-- Name: money_transfers money_transfers_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.money_transfers
    ADD CONSTRAINT money_transfers_pkey PRIMARY KEY (id);


--
-- Name: money_transfers money_transfers_transfer_uuid_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.money_transfers
    ADD CONSTRAINT money_transfers_transfer_uuid_key UNIQUE (transfer_uuid);


--
-- Name: payroll_records payroll_records_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.payroll_records
    ADD CONSTRAINT payroll_records_pkey PRIMARY KEY (id);


--
-- Name: performance_reviews performance_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.performance_reviews
    ADD CONSTRAINT performance_reviews_pkey PRIMARY KEY (id);


--
-- Name: pos_discounts pos_discounts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_discounts
    ADD CONSTRAINT pos_discounts_pkey PRIMARY KEY (id);


--
-- Name: pos_payments pos_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_payments
    ADD CONSTRAINT pos_payments_pkey PRIMARY KEY (id);


--
-- Name: pos_promotions pos_promotions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_promotions
    ADD CONSTRAINT pos_promotions_pkey PRIMARY KEY (id);


--
-- Name: pos_sessions pos_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_sessions
    ADD CONSTRAINT pos_sessions_pkey PRIMARY KEY (id);


--
-- Name: pos_terminals pos_terminals_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_terminals
    ADD CONSTRAINT pos_terminals_pkey PRIMARY KEY (id);


--
-- Name: pos_transaction_items pos_transaction_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transaction_items
    ADD CONSTRAINT pos_transaction_items_pkey PRIMARY KEY (id);


--
-- Name: pos_transactions pos_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transactions
    ADD CONSTRAINT pos_transactions_pkey PRIMARY KEY (id);


--
-- Name: positions positions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.positions
    ADD CONSTRAINT positions_pkey PRIMARY KEY (id);


--
-- Name: price_history price_history_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_pkey PRIMARY KEY (id);


--
-- Name: price_list_categories price_list_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_list_categories
    ADD CONSTRAINT price_list_categories_pkey PRIMARY KEY (id);


--
-- Name: price_list_items price_list_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_list_items
    ADD CONSTRAINT price_list_items_pkey PRIMARY KEY (id);


--
-- Name: price_lists price_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_lists
    ADD CONSTRAINT price_lists_pkey PRIMARY KEY (id);


--
-- Name: price_negotiation_requests price_negotiation_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_negotiation_requests
    ADD CONSTRAINT price_negotiation_requests_pkey PRIMARY KEY (id);


--
-- Name: pricing_lists pricing_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pricing_lists
    ADD CONSTRAINT pricing_lists_pkey PRIMARY KEY (id);


--
-- Name: product_prices product_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.product_prices
    ADD CONSTRAINT product_prices_pkey PRIMARY KEY (id);


--
-- Name: products products_barcode_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_barcode_key UNIQUE (barcode);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: purchase_invoice_items purchase_invoice_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoice_items
    ADD CONSTRAINT purchase_invoice_items_pkey PRIMARY KEY (id);


--
-- Name: purchase_invoices purchase_invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoices
    ADD CONSTRAINT purchase_invoices_pkey PRIMARY KEY (id);


--
-- Name: purchase_items purchase_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_pkey PRIMARY KEY (id);


--
-- Name: purchase_orders purchase_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_orders
    ADD CONSTRAINT purchase_orders_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sales_invoice_items sales_invoice_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoice_items
    ADD CONSTRAINT sales_invoice_items_pkey PRIMARY KEY (id);


--
-- Name: sales_invoices sales_invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices
    ADD CONSTRAINT sales_invoices_pkey PRIMARY KEY (id);


--
-- Name: sales_items sales_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_items
    ADD CONSTRAINT sales_items_pkey PRIMARY KEY (id);


--
-- Name: sales_orders sales_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_pkey PRIMARY KEY (id);


--
-- Name: salesperson_regions salesperson_regions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.salesperson_regions
    ADD CONSTRAINT salesperson_regions_pkey PRIMARY KEY (id);


--
-- Name: stock_movements stock_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_pkey PRIMARY KEY (id);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);


--
-- Name: transfer_platforms transfer_platforms_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.transfer_platforms
    ADD CONSTRAINT transfer_platforms_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: whatsapp_auto_responses whatsapp_auto_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.whatsapp_auto_responses
    ADD CONSTRAINT whatsapp_auto_responses_pkey PRIMARY KEY (id);


--
-- Name: whatsapp_broadcasts whatsapp_broadcasts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.whatsapp_broadcasts
    ADD CONSTRAINT whatsapp_broadcasts_pkey PRIMARY KEY (id);


--
-- Name: whatsapp_messages whatsapp_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.whatsapp_messages
    ADD CONSTRAINT whatsapp_messages_pkey PRIMARY KEY (id);


--
-- Name: idx_customer_region; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_customer_region ON public.migration_customers USING btree (region);


--
-- Name: idx_customer_salesperson; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_customer_salesperson ON public.migration_customers USING btree (salesperson_id);


--
-- Name: idx_customer_zoho; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_customer_zoho ON public.migration_customers USING btree (zoho_customer_id);


--
-- Name: idx_item_brand_model; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_item_brand_model ON public.migration_items USING btree (brand, model);


--
-- Name: idx_item_category; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_item_category ON public.migration_items USING btree (category_id);


--
-- Name: idx_item_zoho; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_item_zoho ON public.migration_items USING btree (zoho_item_id);


--
-- Name: idx_migration_record_batch_entity; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_migration_record_batch_entity ON public.migration_records USING btree (batch_id, entity_type);


--
-- Name: idx_migration_record_entity_source; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_migration_record_entity_source ON public.migration_records USING btree (entity_type, source_id);


--
-- Name: idx_migration_record_status; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_migration_record_status ON public.migration_records USING btree (status);


--
-- Name: idx_price_list_item; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_price_list_item ON public.price_list_items USING btree (price_list_id, item_id);


--
-- Name: idx_stock_item; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_stock_item ON public.migration_stock USING btree (item_id);


--
-- Name: idx_stock_item_warehouse; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_stock_item_warehouse ON public.migration_stock USING btree (item_id, warehouse_id);


--
-- Name: idx_stock_warehouse; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_stock_warehouse ON public.migration_stock USING btree (warehouse_id);


--
-- Name: idx_vendor_zoho; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX idx_vendor_zoho ON public.migration_vendors USING btree (zoho_vendor_id);


--
-- Name: ix_accounting_periods_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_accounting_periods_id ON public.accounting_periods USING btree (id);


--
-- Name: ix_accounts_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_accounts_id ON public.accounts USING btree (id);


--
-- Name: ix_ai_conversation_messages_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_ai_conversation_messages_id ON public.ai_conversation_messages USING btree (id);


--
-- Name: ix_ai_conversations_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_ai_conversations_id ON public.ai_conversations USING btree (id);


--
-- Name: ix_ai_generated_orders_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_ai_generated_orders_id ON public.ai_generated_orders USING btree (id);


--
-- Name: ix_ai_generated_orders_order_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_ai_generated_orders_order_number ON public.ai_generated_orders USING btree (order_number);


--
-- Name: ix_ai_support_tickets_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_ai_support_tickets_id ON public.ai_support_tickets USING btree (id);


--
-- Name: ix_ai_support_tickets_ticket_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_ai_support_tickets_ticket_number ON public.ai_support_tickets USING btree (ticket_number);


--
-- Name: ix_attendance_records_date; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_attendance_records_date ON public.attendance_records USING btree (date);


--
-- Name: ix_attendance_records_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_attendance_records_id ON public.attendance_records USING btree (id);


--
-- Name: ix_branches_branch_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_branches_branch_code ON public.branches USING btree (branch_code);


--
-- Name: ix_branches_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_branches_id ON public.branches USING btree (id);


--
-- Name: ix_branches_name; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_branches_name ON public.branches USING btree (name);


--
-- Name: ix_cash_boxes_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_cash_boxes_code ON public.cash_boxes USING btree (code);


--
-- Name: ix_cash_boxes_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_cash_boxes_id ON public.cash_boxes USING btree (id);


--
-- Name: ix_cash_flow_summaries_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_cash_flow_summaries_id ON public.cash_flow_summaries USING btree (id);


--
-- Name: ix_cash_transactions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_cash_transactions_id ON public.cash_transactions USING btree (id);


--
-- Name: ix_cash_transactions_transaction_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_cash_transactions_transaction_number ON public.cash_transactions USING btree (transaction_number);


--
-- Name: ix_cash_transfers_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_cash_transfers_id ON public.cash_transfers USING btree (id);


--
-- Name: ix_cash_transfers_transfer_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_cash_transfers_transfer_number ON public.cash_transfers USING btree (transfer_number);


--
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_categories_id ON public.categories USING btree (id);


--
-- Name: ix_categories_name; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_categories_name ON public.categories USING btree (name);


--
-- Name: ix_chart_of_accounts_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_chart_of_accounts_code ON public.chart_of_accounts USING btree (code);


--
-- Name: ix_chart_of_accounts_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_chart_of_accounts_id ON public.chart_of_accounts USING btree (id);


--
-- Name: ix_currencies_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_currencies_code ON public.currencies USING btree (code);


--
-- Name: ix_currencies_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_currencies_id ON public.currencies USING btree (id);


--
-- Name: ix_customer_price_categories_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_customer_price_categories_id ON public.customer_price_categories USING btree (id);


--
-- Name: ix_customers_customer_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_customers_customer_code ON public.customers USING btree (customer_code);


--
-- Name: ix_customers_email; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_customers_email ON public.customers USING btree (email);


--
-- Name: ix_customers_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_customers_id ON public.customers USING btree (id);


--
-- Name: ix_customers_name; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_customers_name ON public.customers USING btree (name);


--
-- Name: ix_customers_phone; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_customers_phone ON public.customers USING btree (phone);


--
-- Name: ix_departments_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_departments_code ON public.departments USING btree (code);


--
-- Name: ix_departments_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_departments_id ON public.departments USING btree (id);


--
-- Name: ix_departments_name_ar; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_departments_name_ar ON public.departments USING btree (name_ar);


--
-- Name: ix_departments_name_en; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_departments_name_en ON public.departments USING btree (name_en);


--
-- Name: ix_employees_email; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_employees_email ON public.employees USING btree (email);


--
-- Name: ix_employees_employee_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_employees_employee_code ON public.employees USING btree (employee_code);


--
-- Name: ix_employees_full_name_ar; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_employees_full_name_ar ON public.employees USING btree (full_name_ar);


--
-- Name: ix_employees_full_name_en; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_employees_full_name_en ON public.employees USING btree (full_name_en);


--
-- Name: ix_employees_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_employees_id ON public.employees USING btree (id);


--
-- Name: ix_exchange_rates_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_exchange_rates_id ON public.exchange_rates USING btree (id);


--
-- Name: ix_expense_attachments_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_expense_attachments_id ON public.expense_attachments USING btree (id);


--
-- Name: ix_expense_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_expense_items_id ON public.expense_items USING btree (id);


--
-- Name: ix_expenses_expense_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_expenses_expense_number ON public.expenses USING btree (expense_number);


--
-- Name: ix_expenses_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_expenses_id ON public.expenses USING btree (id);


--
-- Name: ix_fiscal_years_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_fiscal_years_id ON public.fiscal_years USING btree (id);


--
-- Name: ix_hr_dashboard_metrics_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_hr_dashboard_metrics_id ON public.hr_dashboard_metrics USING btree (id);


--
-- Name: ix_hr_dashboard_metrics_metric_date; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_hr_dashboard_metrics_metric_date ON public.hr_dashboard_metrics USING btree (metric_date);


--
-- Name: ix_inventory_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_inventory_items_id ON public.inventory_items USING btree (id);


--
-- Name: ix_invoice_payments_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_invoice_payments_id ON public.invoice_payments USING btree (id);


--
-- Name: ix_invoice_payments_payment_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_invoice_payments_payment_number ON public.invoice_payments USING btree (payment_number);


--
-- Name: ix_item_categories_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_item_categories_code ON public.item_categories USING btree (code);


--
-- Name: ix_item_categories_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_item_categories_id ON public.item_categories USING btree (id);


--
-- Name: ix_journal_entries_entry_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_journal_entries_entry_number ON public.journal_entries USING btree (entry_number);


--
-- Name: ix_journal_entries_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_journal_entries_id ON public.journal_entries USING btree (id);


--
-- Name: ix_journal_lines_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_journal_lines_id ON public.journal_lines USING btree (id);


--
-- Name: ix_journals_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_journals_code ON public.journals USING btree (code);


--
-- Name: ix_journals_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_journals_id ON public.journals USING btree (id);


--
-- Name: ix_leave_requests_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_leave_requests_id ON public.leave_requests USING btree (id);


--
-- Name: ix_migration_batches_batch_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_migration_batches_batch_number ON public.migration_batches USING btree (batch_number);


--
-- Name: ix_migration_batches_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_batches_id ON public.migration_batches USING btree (id);


--
-- Name: ix_migration_customers_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_migration_customers_code ON public.migration_customers USING btree (code);


--
-- Name: ix_migration_customers_email; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_customers_email ON public.migration_customers USING btree (email);


--
-- Name: ix_migration_customers_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_customers_id ON public.migration_customers USING btree (id);


--
-- Name: ix_migration_customers_zoho_customer_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_customers_zoho_customer_id ON public.migration_customers USING btree (zoho_customer_id);


--
-- Name: ix_migration_items_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_migration_items_code ON public.migration_items USING btree (code);


--
-- Name: ix_migration_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_items_id ON public.migration_items USING btree (id);


--
-- Name: ix_migration_items_zoho_item_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_items_zoho_item_id ON public.migration_items USING btree (zoho_item_id);


--
-- Name: ix_migration_records_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_records_id ON public.migration_records USING btree (id);


--
-- Name: ix_migration_stock_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_stock_id ON public.migration_stock USING btree (id);


--
-- Name: ix_migration_vendors_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_migration_vendors_code ON public.migration_vendors USING btree (code);


--
-- Name: ix_migration_vendors_email; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_vendors_email ON public.migration_vendors USING btree (email);


--
-- Name: ix_migration_vendors_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_vendors_id ON public.migration_vendors USING btree (id);


--
-- Name: ix_migration_vendors_zoho_vendor_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_migration_vendors_zoho_vendor_id ON public.migration_vendors USING btree (zoho_vendor_id);


--
-- Name: ix_money_transfers_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_money_transfers_id ON public.money_transfers USING btree (id);


--
-- Name: ix_payroll_records_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_payroll_records_id ON public.payroll_records USING btree (id);


--
-- Name: ix_performance_reviews_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_performance_reviews_id ON public.performance_reviews USING btree (id);


--
-- Name: ix_pos_discounts_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_pos_discounts_code ON public.pos_discounts USING btree (code);


--
-- Name: ix_pos_discounts_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_pos_discounts_id ON public.pos_discounts USING btree (id);


--
-- Name: ix_pos_payments_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_pos_payments_id ON public.pos_payments USING btree (id);


--
-- Name: ix_pos_promotions_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_pos_promotions_code ON public.pos_promotions USING btree (code);


--
-- Name: ix_pos_promotions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_pos_promotions_id ON public.pos_promotions USING btree (id);


--
-- Name: ix_pos_sessions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_pos_sessions_id ON public.pos_sessions USING btree (id);


--
-- Name: ix_pos_sessions_session_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_pos_sessions_session_number ON public.pos_sessions USING btree (session_number);


--
-- Name: ix_pos_terminals_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_pos_terminals_id ON public.pos_terminals USING btree (id);


--
-- Name: ix_pos_terminals_terminal_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_pos_terminals_terminal_code ON public.pos_terminals USING btree (terminal_code);


--
-- Name: ix_pos_transaction_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_pos_transaction_items_id ON public.pos_transaction_items USING btree (id);


--
-- Name: ix_pos_transactions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_pos_transactions_id ON public.pos_transactions USING btree (id);


--
-- Name: ix_pos_transactions_transaction_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_pos_transactions_transaction_number ON public.pos_transactions USING btree (transaction_number);


--
-- Name: ix_positions_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_positions_code ON public.positions USING btree (code);


--
-- Name: ix_positions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_positions_id ON public.positions USING btree (id);


--
-- Name: ix_positions_title_ar; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_positions_title_ar ON public.positions USING btree (title_ar);


--
-- Name: ix_positions_title_en; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_positions_title_en ON public.positions USING btree (title_en);


--
-- Name: ix_price_history_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_price_history_id ON public.price_history USING btree (id);


--
-- Name: ix_price_list_categories_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_price_list_categories_id ON public.price_list_categories USING btree (id);


--
-- Name: ix_price_list_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_price_list_items_id ON public.price_list_items USING btree (id);


--
-- Name: ix_price_lists_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_price_lists_code ON public.price_lists USING btree (code);


--
-- Name: ix_price_lists_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_price_lists_id ON public.price_lists USING btree (id);


--
-- Name: ix_price_lists_zoho_price_list_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_price_lists_zoho_price_list_id ON public.price_lists USING btree (zoho_price_list_id);


--
-- Name: ix_price_negotiation_requests_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_price_negotiation_requests_id ON public.price_negotiation_requests USING btree (id);


--
-- Name: ix_pricing_lists_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_pricing_lists_id ON public.pricing_lists USING btree (id);


--
-- Name: ix_product_prices_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_product_prices_id ON public.product_prices USING btree (id);


--
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_products_id ON public.products USING btree (id);


--
-- Name: ix_products_name; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_products_name ON public.products USING btree (name);


--
-- Name: ix_products_name_ar; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_products_name_ar ON public.products USING btree (name_ar);


--
-- Name: ix_products_sku; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_products_sku ON public.products USING btree (sku);


--
-- Name: ix_purchase_invoice_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_invoice_items_id ON public.purchase_invoice_items USING btree (id);


--
-- Name: ix_purchase_invoices_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_invoices_id ON public.purchase_invoices USING btree (id);


--
-- Name: ix_purchase_invoices_invoice_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_purchase_invoices_invoice_number ON public.purchase_invoices USING btree (invoice_number);


--
-- Name: ix_purchase_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_items_id ON public.purchase_items USING btree (id);


--
-- Name: ix_purchase_orders_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_orders_id ON public.purchase_orders USING btree (id);


--
-- Name: ix_purchase_orders_order_date; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_orders_order_date ON public.purchase_orders USING btree (order_date);


--
-- Name: ix_purchase_orders_order_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_purchase_orders_order_number ON public.purchase_orders USING btree (order_number);


--
-- Name: ix_purchase_orders_payment_status; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_orders_payment_status ON public.purchase_orders USING btree (payment_status);


--
-- Name: ix_purchase_orders_status; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_orders_status ON public.purchase_orders USING btree (status);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_sales_invoice_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_sales_invoice_items_id ON public.sales_invoice_items USING btree (id);


--
-- Name: ix_sales_invoices_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_sales_invoices_id ON public.sales_invoices USING btree (id);


--
-- Name: ix_sales_invoices_invoice_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_sales_invoices_invoice_number ON public.sales_invoices USING btree (invoice_number);


--
-- Name: ix_sales_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_sales_items_id ON public.sales_items USING btree (id);


--
-- Name: ix_sales_orders_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_sales_orders_id ON public.sales_orders USING btree (id);


--
-- Name: ix_sales_orders_order_date; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_sales_orders_order_date ON public.sales_orders USING btree (order_date);


--
-- Name: ix_sales_orders_order_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_sales_orders_order_number ON public.sales_orders USING btree (order_number);


--
-- Name: ix_sales_orders_payment_status; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_sales_orders_payment_status ON public.sales_orders USING btree (payment_status);


--
-- Name: ix_sales_orders_status; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_sales_orders_status ON public.sales_orders USING btree (status);


--
-- Name: ix_salesperson_regions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_salesperson_regions_id ON public.salesperson_regions USING btree (id);


--
-- Name: ix_stock_movements_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_stock_movements_id ON public.stock_movements USING btree (id);


--
-- Name: ix_suppliers_email; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_suppliers_email ON public.suppliers USING btree (email);


--
-- Name: ix_suppliers_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_suppliers_id ON public.suppliers USING btree (id);


--
-- Name: ix_suppliers_name; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_suppliers_name ON public.suppliers USING btree (name);


--
-- Name: ix_suppliers_phone; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_suppliers_phone ON public.suppliers USING btree (phone);


--
-- Name: ix_suppliers_supplier_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_suppliers_supplier_code ON public.suppliers USING btree (supplier_code);


--
-- Name: ix_transfer_platforms_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_transfer_platforms_id ON public.transfer_platforms USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_employee_code; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_users_employee_code ON public.users USING btree (employee_code);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_name; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_users_name ON public.users USING btree (name);


--
-- Name: ix_warehouses_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_warehouses_id ON public.warehouses USING btree (id);


--
-- Name: ix_warehouses_name; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_warehouses_name ON public.warehouses USING btree (name);


--
-- Name: ix_whatsapp_auto_responses_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_whatsapp_auto_responses_id ON public.whatsapp_auto_responses USING btree (id);


--
-- Name: ix_whatsapp_broadcasts_broadcast_id; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_whatsapp_broadcasts_broadcast_id ON public.whatsapp_broadcasts USING btree (broadcast_id);


--
-- Name: ix_whatsapp_broadcasts_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_whatsapp_broadcasts_id ON public.whatsapp_broadcasts USING btree (id);


--
-- Name: ix_whatsapp_messages_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_whatsapp_messages_id ON public.whatsapp_messages USING btree (id);


--
-- Name: ix_whatsapp_messages_phone_number; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_whatsapp_messages_phone_number ON public.whatsapp_messages USING btree (phone_number);


--
-- Name: ix_whatsapp_messages_whatsapp_message_id; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_whatsapp_messages_whatsapp_message_id ON public.whatsapp_messages USING btree (whatsapp_message_id);


--
-- Name: accounting_periods accounting_periods_fiscal_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accounting_periods
    ADD CONSTRAINT accounting_periods_fiscal_year_id_fkey FOREIGN KEY (fiscal_year_id) REFERENCES public.fiscal_years(id);


--
-- Name: accounts accounts_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: accounts accounts_chart_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_chart_account_id_fkey FOREIGN KEY (chart_account_id) REFERENCES public.chart_of_accounts(id);


--
-- Name: accounts accounts_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currencies(id);


--
-- Name: ai_conversation_messages ai_conversation_messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_conversation_messages
    ADD CONSTRAINT ai_conversation_messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.ai_conversations(id);


--
-- Name: ai_conversations ai_conversations_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_conversations
    ADD CONSTRAINT ai_conversations_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: ai_generated_orders ai_generated_orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_generated_orders
    ADD CONSTRAINT ai_generated_orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: ai_support_tickets ai_support_tickets_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_support_tickets
    ADD CONSTRAINT ai_support_tickets_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id);


--
-- Name: ai_support_tickets ai_support_tickets_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ai_support_tickets
    ADD CONSTRAINT ai_support_tickets_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: attendance_records attendance_records_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.attendance_records
    ADD CONSTRAINT attendance_records_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: cash_boxes cash_boxes_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_boxes
    ADD CONSTRAINT cash_boxes_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: cash_boxes cash_boxes_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_boxes
    ADD CONSTRAINT cash_boxes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: cash_boxes cash_boxes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_boxes
    ADD CONSTRAINT cash_boxes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: cash_flow_summaries cash_flow_summaries_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_flow_summaries
    ADD CONSTRAINT cash_flow_summaries_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: cash_flow_summaries cash_flow_summaries_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_flow_summaries
    ADD CONSTRAINT cash_flow_summaries_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: cash_transactions cash_transactions_cash_box_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transactions
    ADD CONSTRAINT cash_transactions_cash_box_id_fkey FOREIGN KEY (cash_box_id) REFERENCES public.cash_boxes(id);


--
-- Name: cash_transactions cash_transactions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transactions
    ADD CONSTRAINT cash_transactions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: cash_transactions cash_transactions_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transactions
    ADD CONSTRAINT cash_transactions_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.users(id);


--
-- Name: cash_transfers cash_transfers_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transfers
    ADD CONSTRAINT cash_transfers_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: cash_transfers cash_transfers_from_cash_box_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transfers
    ADD CONSTRAINT cash_transfers_from_cash_box_id_fkey FOREIGN KEY (from_cash_box_id) REFERENCES public.cash_boxes(id);


--
-- Name: cash_transfers cash_transfers_received_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transfers
    ADD CONSTRAINT cash_transfers_received_by_fkey FOREIGN KEY (received_by) REFERENCES public.users(id);


--
-- Name: cash_transfers cash_transfers_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transfers
    ADD CONSTRAINT cash_transfers_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.users(id);


--
-- Name: cash_transfers cash_transfers_to_cash_box_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_transfers
    ADD CONSTRAINT cash_transfers_to_cash_box_id_fkey FOREIGN KEY (to_cash_box_id) REFERENCES public.cash_boxes(id);


--
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.categories(id);


--
-- Name: chart_of_accounts chart_of_accounts_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT chart_of_accounts_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.chart_of_accounts(id);


--
-- Name: customer_price_categories customer_price_categories_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.customer_price_categories
    ADD CONSTRAINT customer_price_categories_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: customer_price_categories customer_price_categories_pricing_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.customer_price_categories
    ADD CONSTRAINT customer_price_categories_pricing_list_id_fkey FOREIGN KEY (pricing_list_id) REFERENCES public.pricing_lists(id);


--
-- Name: customer_price_categories customer_price_categories_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.customer_price_categories
    ADD CONSTRAINT customer_price_categories_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: customers customers_salesperson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_salesperson_id_fkey FOREIGN KEY (salesperson_id) REFERENCES public.users(id);


--
-- Name: employees employees_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: employees employees_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: employees employees_position_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_position_id_fkey FOREIGN KEY (position_id) REFERENCES public.positions(id);


--
-- Name: employees employees_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: exchange_rates exchange_rates_from_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_from_currency_id_fkey FOREIGN KEY (from_currency_id) REFERENCES public.currencies(id);


--
-- Name: exchange_rates exchange_rates_to_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_to_currency_id_fkey FOREIGN KEY (to_currency_id) REFERENCES public.currencies(id);


--
-- Name: expense_attachments expense_attachments_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expense_attachments
    ADD CONSTRAINT expense_attachments_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.expenses(id);


--
-- Name: expense_attachments expense_attachments_uploaded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expense_attachments
    ADD CONSTRAINT expense_attachments_uploaded_by_id_fkey FOREIGN KEY (uploaded_by_id) REFERENCES public.users(id);


--
-- Name: expense_items expense_items_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expense_items
    ADD CONSTRAINT expense_items_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.expenses(id);


--
-- Name: expense_items expense_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expense_items
    ADD CONSTRAINT expense_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: expenses expenses_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id);


--
-- Name: expenses expenses_approved_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_approved_by_id_fkey FOREIGN KEY (approved_by_id) REFERENCES public.users(id);


--
-- Name: expenses expenses_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: expenses expenses_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id);


--
-- Name: expenses expenses_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currencies(id);


--
-- Name: expenses expenses_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: expenses expenses_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES public.users(id);


--
-- Name: expenses expenses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: departments fk_departments_head_employee; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT fk_departments_head_employee FOREIGN KEY (head_employee_id) REFERENCES public.employees(id);


--
-- Name: employees fk_employees_direct_manager; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT fk_employees_direct_manager FOREIGN KEY (direct_manager_id) REFERENCES public.employees(id);


--
-- Name: inventory_items inventory_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: inventory_items inventory_items_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: invoice_payments invoice_payments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_payments
    ADD CONSTRAINT invoice_payments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: invoice_payments invoice_payments_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_payments
    ADD CONSTRAINT invoice_payments_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currencies(id);


--
-- Name: invoice_payments invoice_payments_purchase_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_payments
    ADD CONSTRAINT invoice_payments_purchase_invoice_id_fkey FOREIGN KEY (purchase_invoice_id) REFERENCES public.purchase_invoices(id);


--
-- Name: invoice_payments invoice_payments_sales_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_payments
    ADD CONSTRAINT invoice_payments_sales_invoice_id_fkey FOREIGN KEY (sales_invoice_id) REFERENCES public.sales_invoices(id);


--
-- Name: item_categories item_categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.item_categories
    ADD CONSTRAINT item_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.item_categories(id);


--
-- Name: journal_entries journal_entries_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: journal_entries journal_entries_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: journal_entries journal_entries_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currencies(id);


--
-- Name: journal_entries journal_entries_journal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_journal_id_fkey FOREIGN KEY (journal_id) REFERENCES public.journals(id);


--
-- Name: journal_entries journal_entries_posted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_posted_by_fkey FOREIGN KEY (posted_by) REFERENCES public.users(id);


--
-- Name: journal_lines journal_lines_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_lines
    ADD CONSTRAINT journal_lines_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id);


--
-- Name: journal_lines journal_lines_journal_entry_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_lines
    ADD CONSTRAINT journal_lines_journal_entry_id_fkey FOREIGN KEY (journal_entry_id) REFERENCES public.journal_entries(id);


--
-- Name: leave_requests leave_requests_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.employees(id);


--
-- Name: leave_requests leave_requests_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: leave_requests leave_requests_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.employees(id);


--
-- Name: leave_requests leave_requests_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.employees(id);


--
-- Name: migration_batches migration_batches_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_batches
    ADD CONSTRAINT migration_batches_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: migration_customers migration_customers_price_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_customers
    ADD CONSTRAINT migration_customers_price_list_id_fkey FOREIGN KEY (price_list_id) REFERENCES public.price_lists(id);


--
-- Name: migration_customers migration_customers_salesperson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_customers
    ADD CONSTRAINT migration_customers_salesperson_id_fkey FOREIGN KEY (salesperson_id) REFERENCES public.users(id);


--
-- Name: migration_items migration_items_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_items
    ADD CONSTRAINT migration_items_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.item_categories(id);


--
-- Name: migration_items migration_items_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_items
    ADD CONSTRAINT migration_items_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: migration_records migration_records_batch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_records
    ADD CONSTRAINT migration_records_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES public.migration_batches(id);


--
-- Name: migration_stock migration_stock_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_stock
    ADD CONSTRAINT migration_stock_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.migration_items(id);


--
-- Name: migration_stock migration_stock_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.migration_stock
    ADD CONSTRAINT migration_stock_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: money_transfers money_transfers_salesperson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.money_transfers
    ADD CONSTRAINT money_transfers_salesperson_id_fkey FOREIGN KEY (salesperson_id) REFERENCES public.users(id);


--
-- Name: payroll_records payroll_records_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.payroll_records
    ADD CONSTRAINT payroll_records_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: payroll_records payroll_records_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.payroll_records
    ADD CONSTRAINT payroll_records_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: payroll_records payroll_records_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.payroll_records
    ADD CONSTRAINT payroll_records_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: performance_reviews performance_reviews_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.performance_reviews
    ADD CONSTRAINT performance_reviews_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: performance_reviews performance_reviews_hr_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.performance_reviews
    ADD CONSTRAINT performance_reviews_hr_reviewed_by_fkey FOREIGN KEY (hr_reviewed_by) REFERENCES public.employees(id);


--
-- Name: performance_reviews performance_reviews_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.performance_reviews
    ADD CONSTRAINT performance_reviews_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.employees(id);


--
-- Name: pos_payments pos_payments_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_payments
    ADD CONSTRAINT pos_payments_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.pos_transactions(id);


--
-- Name: pos_sessions pos_sessions_closed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_sessions
    ADD CONSTRAINT pos_sessions_closed_by_fkey FOREIGN KEY (closed_by) REFERENCES public.users(id);


--
-- Name: pos_sessions pos_sessions_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_sessions
    ADD CONSTRAINT pos_sessions_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currencies(id);


--
-- Name: pos_sessions pos_sessions_terminal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_sessions
    ADD CONSTRAINT pos_sessions_terminal_id_fkey FOREIGN KEY (terminal_id) REFERENCES public.pos_terminals(id);


--
-- Name: pos_sessions pos_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_sessions
    ADD CONSTRAINT pos_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: pos_terminals pos_terminals_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_terminals
    ADD CONSTRAINT pos_terminals_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: pos_terminals pos_terminals_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_terminals
    ADD CONSTRAINT pos_terminals_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: pos_transaction_items pos_transaction_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transaction_items
    ADD CONSTRAINT pos_transaction_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: pos_transaction_items pos_transaction_items_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transaction_items
    ADD CONSTRAINT pos_transaction_items_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.pos_transactions(id);


--
-- Name: pos_transactions pos_transactions_cashier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transactions
    ADD CONSTRAINT pos_transactions_cashier_id_fkey FOREIGN KEY (cashier_id) REFERENCES public.users(id);


--
-- Name: pos_transactions pos_transactions_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transactions
    ADD CONSTRAINT pos_transactions_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: pos_transactions pos_transactions_sales_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transactions
    ADD CONSTRAINT pos_transactions_sales_order_id_fkey FOREIGN KEY (sales_order_id) REFERENCES public.sales_orders(id);


--
-- Name: pos_transactions pos_transactions_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transactions
    ADD CONSTRAINT pos_transactions_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.pos_sessions(id);


--
-- Name: pos_transactions pos_transactions_terminal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transactions
    ADD CONSTRAINT pos_transactions_terminal_id_fkey FOREIGN KEY (terminal_id) REFERENCES public.pos_terminals(id);


--
-- Name: pos_transactions pos_transactions_voided_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.pos_transactions
    ADD CONSTRAINT pos_transactions_voided_by_fkey FOREIGN KEY (voided_by) REFERENCES public.users(id);


--
-- Name: price_history price_history_pricing_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_pricing_list_id_fkey FOREIGN KEY (pricing_list_id) REFERENCES public.pricing_lists(id);


--
-- Name: price_history price_history_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: price_history price_history_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_history
    ADD CONSTRAINT price_history_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: price_list_categories price_list_categories_pricing_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_list_categories
    ADD CONSTRAINT price_list_categories_pricing_list_id_fkey FOREIGN KEY (pricing_list_id) REFERENCES public.pricing_lists(id);


--
-- Name: price_list_items price_list_items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_list_items
    ADD CONSTRAINT price_list_items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.migration_items(id);


--
-- Name: price_list_items price_list_items_price_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_list_items
    ADD CONSTRAINT price_list_items_price_list_id_fkey FOREIGN KEY (price_list_id) REFERENCES public.price_lists(id);


--
-- Name: price_lists price_lists_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_lists
    ADD CONSTRAINT price_lists_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: price_negotiation_requests price_negotiation_requests_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_negotiation_requests
    ADD CONSTRAINT price_negotiation_requests_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: price_negotiation_requests price_negotiation_requests_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_negotiation_requests
    ADD CONSTRAINT price_negotiation_requests_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: price_negotiation_requests price_negotiation_requests_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.price_negotiation_requests
    ADD CONSTRAINT price_negotiation_requests_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: product_prices product_prices_pricing_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.product_prices
    ADD CONSTRAINT product_prices_pricing_list_id_fkey FOREIGN KEY (pricing_list_id) REFERENCES public.pricing_lists(id);


--
-- Name: product_prices product_prices_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.product_prices
    ADD CONSTRAINT product_prices_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: purchase_invoice_items purchase_invoice_items_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoice_items
    ADD CONSTRAINT purchase_invoice_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.purchase_invoices(id);


--
-- Name: purchase_invoice_items purchase_invoice_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoice_items
    ADD CONSTRAINT purchase_invoice_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: purchase_invoice_items purchase_invoice_items_purchase_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoice_items
    ADD CONSTRAINT purchase_invoice_items_purchase_item_id_fkey FOREIGN KEY (purchase_item_id) REFERENCES public.purchase_items(id);


--
-- Name: purchase_invoices purchase_invoices_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoices
    ADD CONSTRAINT purchase_invoices_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: purchase_invoices purchase_invoices_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoices
    ADD CONSTRAINT purchase_invoices_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: purchase_invoices purchase_invoices_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoices
    ADD CONSTRAINT purchase_invoices_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currencies(id);


--
-- Name: purchase_invoices purchase_invoices_purchase_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoices
    ADD CONSTRAINT purchase_invoices_purchase_order_id_fkey FOREIGN KEY (purchase_order_id) REFERENCES public.purchase_orders(id);


--
-- Name: purchase_invoices purchase_invoices_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoices
    ADD CONSTRAINT purchase_invoices_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: purchase_invoices purchase_invoices_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_invoices
    ADD CONSTRAINT purchase_invoices_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: purchase_items purchase_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: purchase_items purchase_items_purchase_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_purchase_order_id_fkey FOREIGN KEY (purchase_order_id) REFERENCES public.purchase_orders(id);


--
-- Name: purchase_orders purchase_orders_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_orders
    ADD CONSTRAINT purchase_orders_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: purchase_orders purchase_orders_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_orders
    ADD CONSTRAINT purchase_orders_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: purchase_orders purchase_orders_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_orders
    ADD CONSTRAINT purchase_orders_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- Name: purchase_orders purchase_orders_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_orders
    ADD CONSTRAINT purchase_orders_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: sales_invoice_items sales_invoice_items_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoice_items
    ADD CONSTRAINT sales_invoice_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.sales_invoices(id);


--
-- Name: sales_invoice_items sales_invoice_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoice_items
    ADD CONSTRAINT sales_invoice_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: sales_invoice_items sales_invoice_items_sales_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoice_items
    ADD CONSTRAINT sales_invoice_items_sales_item_id_fkey FOREIGN KEY (sales_item_id) REFERENCES public.sales_items(id);


--
-- Name: sales_invoices sales_invoices_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices
    ADD CONSTRAINT sales_invoices_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: sales_invoices sales_invoices_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices
    ADD CONSTRAINT sales_invoices_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: sales_invoices sales_invoices_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices
    ADD CONSTRAINT sales_invoices_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES public.currencies(id);


--
-- Name: sales_invoices sales_invoices_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices
    ADD CONSTRAINT sales_invoices_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: sales_invoices sales_invoices_parent_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices
    ADD CONSTRAINT sales_invoices_parent_invoice_id_fkey FOREIGN KEY (parent_invoice_id) REFERENCES public.sales_invoices(id);


--
-- Name: sales_invoices sales_invoices_sales_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices
    ADD CONSTRAINT sales_invoices_sales_order_id_fkey FOREIGN KEY (sales_order_id) REFERENCES public.sales_orders(id);


--
-- Name: sales_invoices sales_invoices_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_invoices
    ADD CONSTRAINT sales_invoices_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: sales_items sales_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_items
    ADD CONSTRAINT sales_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: sales_items sales_items_sales_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_items
    ADD CONSTRAINT sales_items_sales_order_id_fkey FOREIGN KEY (sales_order_id) REFERENCES public.sales_orders(id);


--
-- Name: sales_orders sales_orders_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: sales_orders sales_orders_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: sales_orders sales_orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: sales_orders sales_orders_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: salesperson_regions salesperson_regions_assigned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.salesperson_regions
    ADD CONSTRAINT salesperson_regions_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES public.users(id);


--
-- Name: salesperson_regions salesperson_regions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.salesperson_regions
    ADD CONSTRAINT salesperson_regions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: stock_movements stock_movements_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: stock_movements stock_movements_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES public.inventory_items(id);


--
-- Name: users users_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: warehouses warehouses_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_branch_id_fkey FOREIGN KEY (branch_id) REFERENCES public.branches(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO "user";


--
-- PostgreSQL database dump complete
--

