-- Reference tables (no foreign keys)

CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE product_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE marketing_campaigns (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    channel TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE
);

-- Core entities

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES product_categories(id),
    price NUMERIC(10, 2) NOT NULL,
    cost NUMERIC(10, 2) NOT NULL
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    signup_date DATE NOT NULL,
    is_returning BOOLEAN NOT NULL DEFAULT FALSE
);

-- Transactional tables

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    campaign_id INTEGER REFERENCES marketing_campaigns(id),
    region_id INTEGER NOT NULL REFERENCES regions(id),
    order_date DATE NOT NULL
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    tier TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled'))
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(id),
    amount NUMERIC(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('succeeded', 'failed'))
);