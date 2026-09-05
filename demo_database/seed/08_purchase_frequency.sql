-- Q2: one extra order for every returning customer
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, region_id, '2024-06-25'
FROM customers
WHERE is_returning = TRUE;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 10, 1, 39.99
FROM orders
WHERE order_date = '2024-06-25';

-- Q3: extra order for only ~25% of returning customers (id divisible by 4)
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, region_id, '2024-09-25'
FROM customers
WHERE is_returning = TRUE AND id % 4 = 0;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 10, 1, 39.99
FROM orders
WHERE order_date = '2024-09-25';