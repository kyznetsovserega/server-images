--
-- PostgreSQL database dump
--

-- Dumped from database version 13.21 (Debian 13.21-1.pgdg120+1)
-- Dumped by pg_dump version 13.21 (Debian 13.21-1.pgdg120+1)

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

--
-- Name: images; Type: TABLE; Schema: public; Owner: server_images_user
--

CREATE TABLE public.images (
    id integer NOT NULL,
    filename text NOT NULL,
    original_name text NOT NULL,
    size integer NOT NULL,
    upload_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    file_type text NOT NULL
);


ALTER TABLE public.images OWNER TO server_images_user;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: server_images_user
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.images_id_seq OWNER TO server_images_user;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: server_images_user
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: server_images_user
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: server_images_user
--

COPY public.images (id, filename, original_name, size, upload_time, file_type) FROM stdin;
1	1_back_8683ca.png	1_back.png	224071	2025-06-25 08:55:22.104778	png
2	2_back_489f3f.png	2_back.png	210635	2025-06-25 08:55:27.411898	png
3	3_back_e5a183.png	3_back.png	344737	2025-06-25 08:55:33.504076	png
4	4_back_823be0.png	4_back.png	126100	2025-06-25 08:55:39.56011	png
5	5_back_cdf1d8.png	5_back.png	286301	2025-06-25 08:55:46.526194	png
6	ChatGPT_Image_17_87c226.jpg	ChatGPT_Image_17_.jpg	1348032	2025-06-25 09:31:25.085987	jpg
7	1_back_7f9a58.png	1_back.png	224071	2025-06-25 10:09:06.045277	png
8	2_back_067396.png	2_back.png	210635	2025-06-25 10:09:11.539487	png
9	3_back_35b020.png	3_back.png	344737	2025-06-25 10:09:17.606708	png
10	4_back_110e8e.png	4_back.png	126100	2025-06-25 10:09:23.815601	png
11	5_back_c52f06.png	5_back.png	286301	2025-06-25 10:09:29.237578	png
12	4_back_9f84bc.png	4_back.png	126100	2025-06-25 12:32:19.750873	png
13	5_back_120600.png	5_back.png	286301	2025-06-25 12:32:36.649371	png
14	3_abaca8.jpg	3.jpg	504725	2025-06-25 12:33:04.182926	jpg
15	1_back_e1a7fe.png	1_back.png	224071	2025-06-25 12:34:01.373821	png
16	2_back_a34b23.png	2_back.png	210635	2025-06-25 12:34:17.129061	png
17	5_back_2b7f64.png	5_back.png	286301	2025-06-25 12:34:28.782675	png
18	4_back_41d9eb.png	4_back.png	126100	2025-06-25 12:34:31.037774	png
19	3_back_b18c3c.png	3_back.png	344737	2025-06-25 12:34:32.831431	png
20	2_back_310608.png	2_back.png	210635	2025-06-25 12:34:34.200902	png
21	1_back_e60b7b.png	1_back.png	224071	2025-06-25 12:34:36.462523	png
22	2_back_ad017e.png	2_back.png	210635	2025-06-25 12:34:38.018542	png
23	3_back_e26073.png	3_back.png	344737	2025-06-25 12:34:42.034732	png
\.


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: server_images_user
--

SELECT pg_catalog.setval('public.images_id_seq', 23, true);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: server_images_user
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

