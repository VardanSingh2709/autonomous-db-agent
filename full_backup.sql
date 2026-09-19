--
-- PostgreSQL database dump
--

\restrict dk89fMJqZK3lMJYmwXZ7fHRbg8SkMlYU8rBHg9KFLDBwee9qDOh8zkHbKHQRfgi

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

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
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    id integer NOT NULL,
    name text NOT NULL,
    email text NOT NULL,
    region_id integer NOT NULL,
    signup_date date NOT NULL,
    is_returning boolean DEFAULT false NOT NULL
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_id_seq OWNER TO postgres;

--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_id_seq OWNED BY public.customers.id;


--
-- Name: marketing_campaigns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marketing_campaigns (
    id integer NOT NULL,
    name text NOT NULL,
    channel text NOT NULL,
    start_date date NOT NULL,
    end_date date
);


ALTER TABLE public.marketing_campaigns OWNER TO postgres;

--
-- Name: marketing_campaigns_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.marketing_campaigns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.marketing_campaigns_id_seq OWNER TO postgres;

--
-- Name: marketing_campaigns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.marketing_campaigns_id_seq OWNED BY public.marketing_campaigns.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    CONSTRAINT order_items_quantity_check CHECK ((quantity > 0))
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_id_seq OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    campaign_id integer,
    region_id integer NOT NULL,
    order_date date NOT NULL
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    subscription_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_date date NOT NULL,
    status text NOT NULL,
    CONSTRAINT payments_status_check CHECK ((status = ANY (ARRAY['succeeded'::text, 'failed'::text])))
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_id_seq OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- Name: product_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_categories (
    id integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.product_categories OWNER TO postgres;

--
-- Name: product_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_categories_id_seq OWNER TO postgres;

--
-- Name: product_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_categories_id_seq OWNED BY public.product_categories.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name text NOT NULL,
    category_id integer NOT NULL,
    price numeric(10,2) NOT NULL,
    cost numeric(10,2) NOT NULL
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: regions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regions (
    id integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.regions OWNER TO postgres;

--
-- Name: regions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.regions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.regions_id_seq OWNER TO postgres;

--
-- Name: regions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.regions_id_seq OWNED BY public.regions.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    tier text NOT NULL,
    start_date date NOT NULL,
    end_date date,
    status text NOT NULL,
    CONSTRAINT subscriptions_status_check CHECK ((status = ANY (ARRAY['active'::text, 'cancelled'::text])))
);


ALTER TABLE public.subscriptions OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: customers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN id SET DEFAULT nextval('public.customers_id_seq'::regclass);


--
-- Name: marketing_campaigns id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketing_campaigns ALTER COLUMN id SET DEFAULT nextval('public.marketing_campaigns_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- Name: product_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories ALTER COLUMN id SET DEFAULT nextval('public.product_categories_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: regions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions ALTER COLUMN id SET DEFAULT nextval('public.regions_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (id, name, email, region_id, signup_date, is_returning) FROM stdin;
1	Aarav Sharma	aarav.sharma1@example.com	1	2023-11-02	t
2	Priya Nair	priya.nair1@example.com	1	2023-12-10	t
3	Karan Mehta	karan.mehta1@example.com	1	2024-01-05	t
4	Sara Iqbal	sara.iqbal1@example.com	1	2024-01-20	f
5	Rohan Gupta	rohan.gupta1@example.com	1	2024-02-01	t
6	Ananya Rao	ananya.rao1@example.com	1	2024-02-14	f
7	Vikram Joshi	vikram.joshi1@example.com	1	2024-02-28	t
8	Neha Kapoor	neha.kapoor1@example.com	1	2024-03-15	t
9	Arjun Verma	arjun.verma1@example.com	1	2024-03-22	f
10	Ishita Sen	ishita.sen1@example.com	1	2024-04-02	t
11	Devansh Rathi	devansh.rathi1@example.com	1	2024-04-10	t
12	Meera Pillai	meera.pillai1@example.com	1	2024-04-18	f
13	Yash Malhotra	yash.malhotra1@example.com	1	2024-05-01	t
14	Divya Chawla	divya.chawla1@example.com	1	2024-05-15	t
15	Nikhil Bose	nikhil.bose1@example.com	1	2024-05-30	f
16	Lakshmi Iyer	lakshmi.iyer1@example.com	2	2023-11-05	t
17	Suresh Reddy	suresh.reddy1@example.com	2	2023-12-01	t
18	Kavya Menon	kavya.menon1@example.com	2	2024-01-08	f
19	Arun Kumar	arun.kumar1@example.com	2	2024-01-25	t
20	Deepika Rao	deepika.rao1@example.com	2	2024-02-05	t
21	Manoj Pillai	manoj.pillai1@example.com	2	2024-02-18	f
22	Swathi Nair	swathi.nair1@example.com	2	2024-03-01	t
23	Ravi Shankar	ravi.shankar1@example.com	2	2024-03-12	t
24	Anitha Krishnan	anitha.krishnan1@example.com	2	2024-03-28	f
25	Vijay Subramaniam	vijay.subramaniam1@example.com	2	2024-04-05	t
26	Divya Raman	divya.raman1@example.com	2	2024-04-15	t
27	Harish Babu	harish.babu1@example.com	2	2024-04-25	f
28	Nandini Rajan	nandini.rajan1@example.com	2	2024-05-05	t
29	Prakash Iyer	prakash.iyer1@example.com	2	2024-05-20	t
30	Meenakshi Devi	meenakshi.devi1@example.com	2	2024-05-28	f
31	Sourav Das	sourav.das1@example.com	3	2023-11-10	t
32	Riya Chatterjee	riya.chatterjee1@example.com	3	2023-12-15	t
33	Abhishek Ghosh	abhishek.ghosh1@example.com	3	2024-01-10	f
34	Payal Bhattacharya	payal.bhattacharya1@example.com	3	2024-01-28	t
35	Debashish Roy	debashish.roy1@example.com	3	2024-02-08	t
36	Ipsita Mishra	ipsita.mishra1@example.com	3	2024-02-20	f
37	Bikash Sarkar	bikash.sarkar1@example.com	3	2024-03-05	t
38	Sneha Das	sneha.das1@example.com	3	2024-03-18	t
39	Tapan Nayak	tapan.nayak1@example.com	3	2024-04-01	f
40	Ruma Sengupta	ruma.sengupta1@example.com	3	2024-04-12	t
41	Anupam Dutta	anupam.dutta1@example.com	3	2024-04-22	t
42	Moumita Halder	moumita.halder1@example.com	3	2024-05-02	f
43	Subrata Paul	subrata.paul1@example.com	3	2024-05-12	t
44	Ananya Basu	ananya.basu1@example.com	3	2024-05-25	t
45	Rajib Saha	rajib.saha1@example.com	3	2024-05-30	f
46	Aditi Deshmukh	aditi.deshmukh1@example.com	4	2023-11-15	t
47	Rahul Patil	rahul.patil1@example.com	4	2023-12-20	t
48	Snehal Joshi	snehal.joshi1@example.com	4	2024-01-12	f
49	Nikhil Shah	nikhil.shah1@example.com	4	2024-01-30	t
50	Pooja Kulkarni	pooja.kulkarni1@example.com	4	2024-02-10	t
51	Sameer Bhosale	sameer.bhosale1@example.com	4	2024-02-22	f
52	Trupti More	trupti.more1@example.com	4	2024-03-08	t
53	Ganesh Pawar	ganesh.pawar1@example.com	4	2024-03-20	t
54	Vaishnavi Naik	vaishnavi.naik1@example.com	4	2024-04-03	f
55	Om Kadam	om.kadam1@example.com	4	2024-04-14	t
56	Ketaki Sawant	ketaki.sawant1@example.com	4	2024-04-24	t
57	Rajesh Chavan	rajesh.chavan1@example.com	4	2024-05-04	f
58	Shalini Gaikwad	shalini.gaikwad1@example.com	4	2024-05-14	t
59	Amol Jadhav	amol.jadhav1@example.com	4	2024-05-24	t
60	Pallavi Kale	pallavi.kale1@example.com	4	2024-05-29	f
\.


--
-- Data for Name: marketing_campaigns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.marketing_campaigns (id, name, channel, start_date, end_date) FROM stdin;
1	Spring Sale	email	2024-03-01	2024-03-31
2	Summer Push	social_media	2024-06-01	2024-06-30
3	Search Ads Q2	paid_search	2024-04-01	2024-06-30
4	Search Ads Q3	paid_search	2024-07-01	2024-09-30
5	Influencer Collab	social_media	2024-08-01	2024-08-31
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_items (id, order_id, product_id, quantity, unit_price) FROM stdin;
1	1	1	15	79.99
2	2	1	15	79.99
3	3	1	15	79.99
4	4	1	15	79.99
5	5	1	15	79.99
6	6	1	15	79.99
7	7	1	15	79.99
8	8	1	15	79.99
9	9	1	15	79.99
10	10	1	15	79.99
11	11	1	15	79.99
12	12	1	15	79.99
13	13	1	15	79.99
14	14	1	15	79.99
15	15	1	15	79.99
16	16	2	5	49.99
17	17	2	5	49.99
18	18	2	5	49.99
19	19	2	5	49.99
20	20	2	5	49.99
21	21	2	5	49.99
22	22	2	5	49.99
23	23	2	5	49.99
24	24	2	5	49.99
25	25	2	5	49.99
26	26	2	5	49.99
27	27	2	5	49.99
28	28	2	5	49.99
29	29	2	5	49.99
30	30	2	5	49.99
31	16	4	4	89.99
32	17	4	4	89.99
33	18	4	4	89.99
34	19	4	4	89.99
35	20	4	4	89.99
36	21	4	4	89.99
37	22	4	4	89.99
38	23	4	4	89.99
39	24	4	4	89.99
40	25	4	4	89.99
41	26	4	4	89.99
42	27	4	4	89.99
43	28	4	4	89.99
44	29	4	4	89.99
45	30	4	4	89.99
46	16	7	4	44.99
47	17	7	4	44.99
48	18	7	4	44.99
49	19	7	4	44.99
50	20	7	4	44.99
51	21	7	4	44.99
52	22	7	4	44.99
53	23	7	4	44.99
54	24	7	4	44.99
55	25	7	4	44.99
56	26	7	4	44.99
57	27	7	4	44.99
58	28	7	4	44.99
59	29	7	4	44.99
60	30	7	4	44.99
61	31	1	10	79.99
62	32	1	10	79.99
63	33	1	10	79.99
64	34	1	10	79.99
65	35	1	10	79.99
66	36	1	10	79.99
67	37	1	10	79.99
68	38	1	10	79.99
69	39	1	10	79.99
70	40	1	10	79.99
71	41	2	6	49.99
72	42	2	6	49.99
73	43	2	6	49.99
74	44	2	6	49.99
75	45	2	6	49.99
76	46	2	6	49.99
77	47	2	6	49.99
78	48	2	6	49.99
79	49	2	6	49.99
80	50	2	6	49.99
81	51	2	6	49.99
82	52	2	6	49.99
83	53	2	6	49.99
84	54	2	6	49.99
85	55	2	6	49.99
86	41	4	4	89.99
87	42	4	4	89.99
88	43	4	4	89.99
89	44	4	4	89.99
90	45	4	4	89.99
91	46	4	4	89.99
92	47	4	4	89.99
93	48	4	4	89.99
94	49	4	4	89.99
95	50	4	4	89.99
96	51	4	4	89.99
97	52	4	4	89.99
98	53	4	4	89.99
99	54	4	4	89.99
100	55	4	4	89.99
101	41	7	5	44.99
102	42	7	5	44.99
103	43	7	5	44.99
104	44	7	5	44.99
105	45	7	5	44.99
106	46	7	5	44.99
107	47	7	5	44.99
108	48	7	5	44.99
109	49	7	5	44.99
110	50	7	5	44.99
111	51	7	5	44.99
112	52	7	5	44.99
113	53	7	5	44.99
114	54	7	5	44.99
115	55	7	5	44.99
116	56	3	8	29.99
117	57	3	8	29.99
118	58	3	8	29.99
119	59	3	8	29.99
120	60	3	8	29.99
121	61	3	8	29.99
122	62	3	8	29.99
123	63	3	8	29.99
124	64	3	8	29.99
125	65	3	8	29.99
126	66	3	8	29.99
127	67	3	8	29.99
128	68	3	8	29.99
129	69	3	8	29.99
130	70	3	8	29.99
131	71	3	8	29.99
132	72	3	8	29.99
133	73	3	8	29.99
134	74	3	8	29.99
135	75	3	8	29.99
136	76	3	8	29.99
137	77	3	8	29.99
138	78	3	8	29.99
139	79	3	8	29.99
140	80	3	8	29.99
141	81	3	8	29.99
142	82	3	8	29.99
143	83	3	8	29.99
144	84	3	8	29.99
145	85	3	8	29.99
146	86	3	8	29.99
147	87	3	8	29.99
148	88	3	8	29.99
149	89	3	8	29.99
150	90	3	8	29.99
151	91	3	8	29.99
152	92	3	8	29.99
153	93	3	8	29.99
154	94	3	8	29.99
155	95	3	8	29.99
156	96	3	8	29.99
157	97	3	8	29.99
158	98	3	8	29.99
159	99	3	8	29.99
160	100	3	8	29.99
161	56	5	7	34.99
162	57	5	7	34.99
163	58	5	7	34.99
164	59	5	7	34.99
165	60	5	7	34.99
166	61	5	7	34.99
167	62	5	7	34.99
168	63	5	7	34.99
169	64	5	7	34.99
170	65	5	7	34.99
171	66	5	7	34.99
172	67	5	7	34.99
173	68	5	7	34.99
174	69	5	7	34.99
175	70	5	7	34.99
176	71	5	7	34.99
177	72	5	7	34.99
178	73	5	7	34.99
179	74	5	7	34.99
180	75	5	7	34.99
181	76	5	7	34.99
182	77	5	7	34.99
183	78	5	7	34.99
184	79	5	7	34.99
185	80	5	7	34.99
186	81	5	7	34.99
187	82	5	7	34.99
188	83	5	7	34.99
189	84	5	7	34.99
190	85	5	7	34.99
191	86	5	7	34.99
192	87	5	7	34.99
193	88	5	7	34.99
194	89	5	7	34.99
195	90	5	7	34.99
196	91	5	7	34.99
197	92	5	7	34.99
198	93	5	7	34.99
199	94	5	7	34.99
200	95	5	7	34.99
201	96	5	7	34.99
202	97	5	7	34.99
203	98	5	7	34.99
204	99	5	7	34.99
205	100	5	7	34.99
206	56	8	10	69.99
207	57	8	10	69.99
208	58	8	10	69.99
209	59	8	10	69.99
210	60	8	10	69.99
211	61	8	10	69.99
212	62	8	10	69.99
213	63	8	10	69.99
214	64	8	10	69.99
215	65	8	10	69.99
216	66	8	10	69.99
217	67	8	10	69.99
218	68	8	10	69.99
219	69	8	10	69.99
220	70	8	10	69.99
221	71	8	10	69.99
222	72	8	10	69.99
223	73	8	10	69.99
224	74	8	10	69.99
225	75	8	10	69.99
226	76	8	10	69.99
227	77	8	10	69.99
228	78	8	10	69.99
229	79	8	10	69.99
230	80	8	10	69.99
231	81	8	10	69.99
232	82	8	10	69.99
233	83	8	10	69.99
234	84	8	10	69.99
235	85	8	10	69.99
236	86	8	10	69.99
237	87	8	10	69.99
238	88	8	10	69.99
239	89	8	10	69.99
240	90	8	10	69.99
241	91	8	10	69.99
242	92	8	10	69.99
243	93	8	10	69.99
244	94	8	10	69.99
245	95	8	10	69.99
246	96	8	10	69.99
247	97	8	10	69.99
248	98	8	10	69.99
249	99	8	10	69.99
250	100	8	10	69.99
251	56	12	6	64.99
252	57	12	6	64.99
253	58	12	6	64.99
254	59	12	6	64.99
255	60	12	6	64.99
256	61	12	6	64.99
257	62	12	6	64.99
258	63	12	6	64.99
259	64	12	6	64.99
260	65	12	6	64.99
261	66	12	6	64.99
262	67	12	6	64.99
263	68	12	6	64.99
264	69	12	6	64.99
265	70	12	6	64.99
266	71	12	6	64.99
267	72	12	6	64.99
268	73	12	6	64.99
269	74	12	6	64.99
270	75	12	6	64.99
271	76	12	6	64.99
272	77	12	6	64.99
273	78	12	6	64.99
274	79	12	6	64.99
275	80	12	6	64.99
276	81	12	6	64.99
277	82	12	6	64.99
278	83	12	6	64.99
279	84	12	6	64.99
280	85	12	6	64.99
281	86	12	6	64.99
282	87	12	6	64.99
283	88	12	6	64.99
284	89	12	6	64.99
285	90	12	6	64.99
286	91	12	6	64.99
287	92	12	6	64.99
288	93	12	6	64.99
289	94	12	6	64.99
290	95	12	6	64.99
291	96	12	6	64.99
292	97	12	6	64.99
293	98	12	6	64.99
294	99	12	6	64.99
295	100	12	6	64.99
296	101	3	7	29.99
297	102	3	7	29.99
298	103	3	7	29.99
299	104	3	7	29.99
300	105	3	7	29.99
301	106	3	7	29.99
302	107	3	7	29.99
303	108	3	7	29.99
304	109	3	7	29.99
305	110	3	7	29.99
306	111	3	7	29.99
307	112	3	7	29.99
308	113	3	7	29.99
309	114	3	7	29.99
310	115	3	7	29.99
311	116	3	7	29.99
312	117	3	7	29.99
313	118	3	7	29.99
314	119	3	7	29.99
315	120	3	7	29.99
316	121	3	7	29.99
317	122	3	7	29.99
318	123	3	7	29.99
319	124	3	7	29.99
320	125	3	7	29.99
321	126	3	7	29.99
322	127	3	7	29.99
323	128	3	7	29.99
324	129	3	7	29.99
325	130	3	7	29.99
326	131	3	7	29.99
327	132	3	7	29.99
328	133	3	7	29.99
329	134	3	7	29.99
330	135	3	7	29.99
331	136	3	7	29.99
332	137	3	7	29.99
333	138	3	7	29.99
334	139	3	7	29.99
335	140	3	7	29.99
336	141	3	7	29.99
337	142	3	7	29.99
338	143	3	7	29.99
339	144	3	7	29.99
340	145	3	7	29.99
341	101	5	7	34.99
342	102	5	7	34.99
343	103	5	7	34.99
344	104	5	7	34.99
345	105	5	7	34.99
346	106	5	7	34.99
347	107	5	7	34.99
348	108	5	7	34.99
349	109	5	7	34.99
350	110	5	7	34.99
351	111	5	7	34.99
352	112	5	7	34.99
353	113	5	7	34.99
354	114	5	7	34.99
355	115	5	7	34.99
356	116	5	7	34.99
357	117	5	7	34.99
358	118	5	7	34.99
359	119	5	7	34.99
360	120	5	7	34.99
361	121	5	7	34.99
362	122	5	7	34.99
363	123	5	7	34.99
364	124	5	7	34.99
365	125	5	7	34.99
366	126	5	7	34.99
367	127	5	7	34.99
368	128	5	7	34.99
369	129	5	7	34.99
370	130	5	7	34.99
371	131	5	7	34.99
372	132	5	7	34.99
373	133	5	7	34.99
374	134	5	7	34.99
375	135	5	7	34.99
376	136	5	7	34.99
377	137	5	7	34.99
378	138	5	7	34.99
379	139	5	7	34.99
380	140	5	7	34.99
381	141	5	7	34.99
382	142	5	7	34.99
383	143	5	7	34.99
384	144	5	7	34.99
385	145	5	7	34.99
386	101	8	9	69.99
387	102	8	9	69.99
388	103	8	9	69.99
389	104	8	9	69.99
390	105	8	9	69.99
391	106	8	9	69.99
392	107	8	9	69.99
393	108	8	9	69.99
394	109	8	9	69.99
395	110	8	9	69.99
396	111	8	9	69.99
397	112	8	9	69.99
398	113	8	9	69.99
399	114	8	9	69.99
400	115	8	9	69.99
401	116	8	9	69.99
402	117	8	9	69.99
403	118	8	9	69.99
404	119	8	9	69.99
405	120	8	9	69.99
406	121	8	9	69.99
407	122	8	9	69.99
408	123	8	9	69.99
409	124	8	9	69.99
410	125	8	9	69.99
411	126	8	9	69.99
412	127	8	9	69.99
413	128	8	9	69.99
414	129	8	9	69.99
415	130	8	9	69.99
416	131	8	9	69.99
417	132	8	9	69.99
418	133	8	9	69.99
419	134	8	9	69.99
420	135	8	9	69.99
421	136	8	9	69.99
422	137	8	9	69.99
423	138	8	9	69.99
424	139	8	9	69.99
425	140	8	9	69.99
426	141	8	9	69.99
427	142	8	9	69.99
428	143	8	9	69.99
429	144	8	9	69.99
430	145	8	9	69.99
431	101	12	6	64.99
432	102	12	6	64.99
433	103	12	6	64.99
434	104	12	6	64.99
435	105	12	6	64.99
436	106	12	6	64.99
437	107	12	6	64.99
438	108	12	6	64.99
439	109	12	6	64.99
440	110	12	6	64.99
441	111	12	6	64.99
442	112	12	6	64.99
443	113	12	6	64.99
444	114	12	6	64.99
445	115	12	6	64.99
446	116	12	6	64.99
447	117	12	6	64.99
448	118	12	6	64.99
449	119	12	6	64.99
450	120	12	6	64.99
451	121	12	6	64.99
452	122	12	6	64.99
453	123	12	6	64.99
454	124	12	6	64.99
455	125	12	6	64.99
456	126	12	6	64.99
457	127	12	6	64.99
458	128	12	6	64.99
459	129	12	6	64.99
460	130	12	6	64.99
461	131	12	6	64.99
462	132	12	6	64.99
463	133	12	6	64.99
464	134	12	6	64.99
465	135	12	6	64.99
466	136	12	6	64.99
467	137	12	6	64.99
468	138	12	6	64.99
469	139	12	6	64.99
470	140	12	6	64.99
471	141	12	6	64.99
472	142	12	6	64.99
473	143	12	6	64.99
474	144	12	6	64.99
475	145	12	6	64.99
476	146	10	1	39.99
477	147	10	1	39.99
478	148	10	1	39.99
479	149	10	1	39.99
480	150	10	1	39.99
481	151	10	1	39.99
482	152	10	1	39.99
483	153	10	1	39.99
484	154	10	1	39.99
485	155	10	1	39.99
486	156	10	1	39.99
487	157	10	1	39.99
488	158	10	1	39.99
489	159	10	1	39.99
490	160	10	1	39.99
491	161	10	1	39.99
492	162	10	1	39.99
493	163	10	1	39.99
494	164	10	1	39.99
495	165	10	1	39.99
496	166	10	1	39.99
497	167	10	1	39.99
498	168	10	1	39.99
499	169	10	1	39.99
500	170	10	1	39.99
501	171	10	1	39.99
502	172	10	1	39.99
503	173	10	1	39.99
504	174	10	1	39.99
505	175	10	1	39.99
506	176	10	1	39.99
507	177	10	1	39.99
508	178	10	1	39.99
509	179	10	1	39.99
510	180	10	1	39.99
511	181	10	1	39.99
512	182	10	1	39.99
513	183	10	1	39.99
514	184	10	1	39.99
515	185	10	1	39.99
516	186	10	1	39.99
517	187	10	1	39.99
518	188	10	1	39.99
519	189	10	1	39.99
520	190	10	1	39.99
521	191	10	1	39.99
522	192	10	1	39.99
523	193	10	1	39.99
524	194	10	1	39.99
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, customer_id, campaign_id, region_id, order_date) FROM stdin;
91	51	\N	4	2024-05-10
92	52	\N	4	2024-05-10
93	53	\N	4	2024-05-10
94	54	\N	4	2024-05-10
95	55	\N	4	2024-05-10
96	56	\N	4	2024-05-10
97	57	\N	4	2024-05-10
98	58	\N	4	2024-05-10
99	59	\N	4	2024-05-10
100	60	\N	4	2024-05-10
116	31	\N	3	2024-08-05
117	32	\N	3	2024-08-05
118	33	\N	3	2024-08-05
119	34	\N	3	2024-08-05
120	35	\N	3	2024-08-05
121	36	\N	3	2024-08-05
122	37	\N	3	2024-08-05
123	38	\N	3	2024-08-05
124	39	\N	3	2024-08-05
125	40	\N	3	2024-08-05
126	41	\N	3	2024-08-05
127	42	\N	3	2024-08-05
128	43	\N	3	2024-08-05
129	44	\N	3	2024-08-05
130	45	\N	3	2024-08-05
131	46	\N	4	2024-08-10
132	47	\N	4	2024-08-10
133	48	\N	4	2024-08-10
134	49	\N	4	2024-08-10
135	50	\N	4	2024-08-10
136	51	\N	4	2024-08-10
137	52	\N	4	2024-08-10
138	53	\N	4	2024-08-10
139	54	\N	4	2024-08-10
140	55	\N	4	2024-08-10
141	56	\N	4	2024-08-10
142	57	\N	4	2024-08-10
143	58	\N	4	2024-08-10
144	59	\N	4	2024-08-10
145	60	\N	4	2024-08-10
1	1	3	1	2024-05-01
2	2	3	1	2024-05-01
3	3	3	1	2024-05-01
4	4	3	1	2024-05-01
5	5	3	1	2024-05-01
6	6	3	1	2024-05-01
7	7	3	1	2024-05-01
8	8	3	1	2024-05-01
9	9	3	1	2024-05-01
10	10	3	1	2024-05-01
11	11	3	1	2024-05-01
12	12	3	1	2024-05-01
13	13	3	1	2024-05-01
14	14	3	1	2024-05-01
15	15	3	1	2024-05-01
16	1	3	1	2024-05-15
17	2	3	1	2024-05-15
18	3	3	1	2024-05-15
19	4	3	1	2024-05-15
20	5	3	1	2024-05-15
21	6	3	1	2024-05-15
22	7	3	1	2024-05-15
23	8	3	1	2024-05-15
24	9	3	1	2024-05-15
25	10	3	1	2024-05-15
26	11	3	1	2024-05-15
27	12	3	1	2024-05-15
28	13	3	1	2024-05-15
29	14	3	1	2024-05-15
30	15	3	1	2024-05-15
56	16	1	2	2024-05-01
57	17	1	2	2024-05-01
58	18	1	2	2024-05-01
59	19	1	2	2024-05-01
60	20	1	2	2024-05-01
61	21	1	2	2024-05-01
62	22	1	2	2024-05-01
63	23	1	2	2024-05-01
64	24	1	2	2024-05-01
65	25	1	2	2024-05-01
66	26	1	2	2024-05-01
67	27	1	2	2024-05-01
68	28	1	2	2024-05-01
69	29	1	2	2024-05-01
70	30	1	2	2024-05-01
71	31	1	3	2024-05-05
72	32	1	3	2024-05-05
73	33	1	3	2024-05-05
74	34	1	3	2024-05-05
75	35	1	3	2024-05-05
76	36	2	3	2024-05-05
77	37	2	3	2024-05-05
78	38	2	3	2024-05-05
79	39	2	3	2024-05-05
80	40	2	3	2024-05-05
81	41	2	3	2024-05-05
82	42	2	3	2024-05-05
83	43	2	3	2024-05-05
84	44	2	3	2024-05-05
85	45	2	3	2024-05-05
86	46	2	4	2024-05-10
87	47	2	4	2024-05-10
88	48	2	4	2024-05-10
89	49	2	4	2024-05-10
90	50	2	4	2024-05-10
31	1	4	1	2024-08-01
32	2	4	1	2024-08-01
33	3	4	1	2024-08-01
34	4	4	1	2024-08-01
35	5	4	1	2024-08-01
36	6	4	1	2024-08-01
37	7	4	1	2024-08-01
38	8	4	1	2024-08-01
39	9	1	1	2024-08-01
40	10	1	1	2024-08-01
41	1	1	1	2024-08-15
42	2	1	1	2024-08-15
43	3	1	1	2024-08-15
44	4	1	1	2024-08-15
45	5	1	1	2024-08-15
46	6	1	1	2024-08-15
47	7	1	1	2024-08-15
48	8	1	1	2024-08-15
49	9	1	1	2024-08-15
50	10	1	1	2024-08-15
51	11	1	1	2024-08-15
52	12	1	1	2024-08-15
53	13	1	1	2024-08-15
54	14	1	1	2024-08-15
55	15	1	1	2024-08-15
102	17	5	2	2024-08-01
103	18	5	2	2024-08-01
104	19	5	2	2024-08-01
105	20	5	2	2024-08-01
106	21	5	2	2024-08-01
107	22	5	2	2024-08-01
108	23	5	2	2024-08-01
109	24	5	2	2024-08-01
110	25	5	2	2024-08-01
111	26	5	2	2024-08-01
112	27	5	2	2024-08-01
113	28	5	2	2024-08-01
114	29	5	2	2024-08-01
115	30	5	2	2024-08-01
101	16	1	2	2024-08-01
146	1	\N	1	2024-06-25
147	2	\N	1	2024-06-25
148	3	\N	1	2024-06-25
149	5	\N	1	2024-06-25
150	7	\N	1	2024-06-25
151	8	\N	1	2024-06-25
152	10	\N	1	2024-06-25
153	11	\N	1	2024-06-25
154	13	\N	1	2024-06-25
155	14	\N	1	2024-06-25
156	16	\N	2	2024-06-25
157	17	\N	2	2024-06-25
158	19	\N	2	2024-06-25
159	20	\N	2	2024-06-25
160	22	\N	2	2024-06-25
161	23	\N	2	2024-06-25
162	25	\N	2	2024-06-25
163	26	\N	2	2024-06-25
164	28	\N	2	2024-06-25
165	29	\N	2	2024-06-25
166	31	\N	3	2024-06-25
167	32	\N	3	2024-06-25
168	34	\N	3	2024-06-25
169	35	\N	3	2024-06-25
170	37	\N	3	2024-06-25
171	38	\N	3	2024-06-25
172	40	\N	3	2024-06-25
173	41	\N	3	2024-06-25
174	43	\N	3	2024-06-25
175	44	\N	3	2024-06-25
176	46	\N	4	2024-06-25
177	47	\N	4	2024-06-25
178	49	\N	4	2024-06-25
179	50	\N	4	2024-06-25
180	52	\N	4	2024-06-25
181	53	\N	4	2024-06-25
182	55	\N	4	2024-06-25
183	56	\N	4	2024-06-25
184	58	\N	4	2024-06-25
185	59	\N	4	2024-06-25
186	8	\N	1	2024-09-25
187	16	\N	2	2024-09-25
188	20	\N	2	2024-09-25
189	28	\N	2	2024-09-25
190	32	\N	3	2024-09-25
191	40	\N	3	2024-09-25
192	44	\N	3	2024-09-25
193	52	\N	4	2024-09-25
194	56	\N	4	2024-09-25
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, subscription_id, amount, payment_date, status) FROM stdin;
\.


--
-- Data for Name: product_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_categories (id, name) FROM stdin;
1	Electronics
2	Home & Kitchen
3	Apparel
4	Beauty
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, name, category_id, price, cost) FROM stdin;
1	Product A - Wireless Earbuds	1	79.99	35.00
2	Bluetooth Speaker	1	49.99	22.00
3	USB-C Charging Hub	1	29.99	12.00
4	Ceramic Cookware Set	2	89.99	40.00
5	Electric Kettle	2	34.99	15.00
6	Knife Block Set	2	59.99	25.00
7	Cotton Hoodie	3	44.99	18.00
8	Running Shoes	3	69.99	30.00
9	Denim Jacket	3	79.99	34.00
10	Skincare Set	4	39.99	16.00
11	Hair Dryer	4	54.99	24.00
12	Perfume	4	64.99	28.00
\.


--
-- Data for Name: regions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regions (id, name) FROM stdin;
1	North
2	South
3	East
4	West
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscriptions (id, customer_id, tier, start_date, end_date, status) FROM stdin;
5	5	Basic	2023-06-01	\N	active
6	6	Basic	2023-06-01	\N	active
7	7	Basic	2023-06-01	\N	active
8	8	Basic	2023-06-01	\N	active
9	9	Basic	2023-06-01	\N	active
10	10	Basic	2023-06-01	\N	active
11	11	Basic	2023-06-01	\N	active
12	12	Basic	2023-06-01	\N	active
13	13	Basic	2023-06-01	\N	active
14	14	Basic	2023-06-01	\N	active
15	15	Basic	2023-06-01	\N	active
16	16	Basic	2023-06-01	\N	active
17	17	Basic	2023-06-01	\N	active
18	18	Basic	2023-06-01	\N	active
19	19	Basic	2023-06-01	\N	active
20	20	Basic	2023-06-01	\N	active
21	21	Basic	2023-06-01	\N	active
22	22	Basic	2023-06-01	\N	active
23	23	Basic	2023-06-01	\N	active
24	24	Basic	2023-06-01	\N	active
25	25	Basic	2023-06-01	\N	active
26	26	Basic	2023-06-01	\N	active
27	27	Basic	2023-06-01	\N	active
28	28	Basic	2023-06-01	\N	active
29	29	Basic	2023-06-01	\N	active
30	30	Basic	2023-06-01	\N	active
40	10	Premium	2023-06-01	\N	active
41	11	Premium	2023-06-01	\N	active
42	12	Premium	2023-06-01	\N	active
43	13	Premium	2023-06-01	\N	active
44	14	Premium	2023-06-01	\N	active
45	15	Premium	2023-06-01	\N	active
46	16	Premium	2023-06-01	\N	active
47	17	Premium	2023-06-01	\N	active
48	18	Premium	2023-06-01	\N	active
49	19	Premium	2023-06-01	\N	active
50	20	Premium	2023-06-01	\N	active
51	21	Premium	2023-06-01	\N	active
52	22	Premium	2023-06-01	\N	active
53	23	Premium	2023-06-01	\N	active
54	24	Premium	2023-06-01	\N	active
55	25	Premium	2023-06-01	\N	active
56	26	Premium	2023-06-01	\N	active
57	27	Premium	2023-06-01	\N	active
58	28	Premium	2023-06-01	\N	active
59	29	Premium	2023-06-01	\N	active
60	30	Premium	2023-06-01	\N	active
63	3	Enterprise	2023-06-01	\N	active
64	4	Enterprise	2023-06-01	\N	active
65	5	Enterprise	2023-06-01	\N	active
66	6	Enterprise	2023-06-01	\N	active
67	7	Enterprise	2023-06-01	\N	active
68	8	Enterprise	2023-06-01	\N	active
69	9	Enterprise	2023-06-01	\N	active
70	10	Enterprise	2023-06-01	\N	active
71	11	Enterprise	2023-06-01	\N	active
72	12	Enterprise	2023-06-01	\N	active
73	13	Enterprise	2023-06-01	\N	active
74	14	Enterprise	2023-06-01	\N	active
75	15	Enterprise	2023-06-01	\N	active
76	16	Enterprise	2023-06-01	\N	active
77	17	Enterprise	2023-06-01	\N	active
78	18	Enterprise	2023-06-01	\N	active
79	19	Enterprise	2023-06-01	\N	active
80	20	Enterprise	2023-06-01	\N	active
81	21	Enterprise	2023-06-01	\N	active
82	22	Enterprise	2023-06-01	\N	active
83	23	Enterprise	2023-06-01	\N	active
84	24	Enterprise	2023-06-01	\N	active
85	25	Enterprise	2023-06-01	\N	active
86	26	Enterprise	2023-06-01	\N	active
87	27	Enterprise	2023-06-01	\N	active
88	28	Enterprise	2023-06-01	\N	active
89	29	Enterprise	2023-06-01	\N	active
90	30	Enterprise	2023-06-01	\N	active
1	1	Basic	2023-06-01	2024-05-15	cancelled
2	2	Basic	2023-06-01	2024-05-15	cancelled
3	3	Basic	2023-06-01	2024-08-15	cancelled
4	4	Basic	2023-06-01	2024-08-15	cancelled
31	1	Premium	2023-06-01	2024-05-20	cancelled
32	2	Premium	2023-06-01	2024-05-20	cancelled
33	3	Premium	2023-06-01	2024-08-20	cancelled
34	4	Premium	2023-06-01	2024-08-20	cancelled
35	5	Premium	2023-06-01	2024-08-20	cancelled
36	6	Premium	2023-06-01	2024-08-20	cancelled
37	7	Premium	2023-06-01	2024-08-20	cancelled
38	8	Premium	2023-06-01	2024-08-20	cancelled
39	9	Premium	2023-06-01	2024-08-20	cancelled
61	1	Enterprise	2023-06-01	2024-05-25	cancelled
62	2	Enterprise	2023-06-01	2024-08-25	cancelled
\.


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customers_id_seq', 61, true);


--
-- Name: marketing_campaigns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.marketing_campaigns_id_seq', 5, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_items_id_seq', 524, true);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 194, true);


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 1, false);


--
-- Name: product_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_categories_id_seq', 6, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 12, true);


--
-- Name: regions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.regions_id_seq', 6, true);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 90, true);


--
-- Name: customers customers_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_email_key UNIQUE (email);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: marketing_campaigns marketing_campaigns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketing_campaigns
    ADD CONSTRAINT marketing_campaigns_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: product_categories product_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT product_categories_name_key UNIQUE (name);


--
-- Name: product_categories product_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT product_categories_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: regions regions_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_name_key UNIQUE (name);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: customers customers_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: orders orders_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.marketing_campaigns(id);


--
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: orders orders_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: payments payments_subscription_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_subscription_id_fkey FOREIGN KEY (subscription_id) REFERENCES public.subscriptions(id);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.product_categories(id);


--
-- Name: subscriptions subscriptions_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO readonly_agent;


--
-- Name: TABLE customers; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.customers TO readonly_agent;


--
-- Name: TABLE marketing_campaigns; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.marketing_campaigns TO readonly_agent;


--
-- Name: TABLE order_items; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.order_items TO readonly_agent;


--
-- Name: TABLE orders; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.orders TO readonly_agent;


--
-- Name: TABLE payments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.payments TO readonly_agent;


--
-- Name: TABLE product_categories; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.product_categories TO readonly_agent;


--
-- Name: TABLE products; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.products TO readonly_agent;


--
-- Name: TABLE regions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.regions TO readonly_agent;


--
-- Name: TABLE subscriptions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.subscriptions TO readonly_agent;


--
-- PostgreSQL database dump complete
--

\unrestrict dk89fMJqZK3lMJYmwXZ7fHRbg8SkMlYU8rBHg9KFLDBwee9qDOh8zkHbKHQRfgi

