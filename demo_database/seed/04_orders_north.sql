-- North Q2 — Product A orders (all 15 North customers)
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, 1, '2024-05-01' FROM customers WHERE region_id = 1;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 1, 15, 79.99 FROM orders WHERE region_id = 1 AND order_date = '2024-05-01';

-- North Q2 — other products orders (all 15 North customers)
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, 1, '2024-05-15' FROM customers WHERE region_id = 1;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 2, 5, 49.99 FROM orders WHERE region_id = 1 AND order_date = '2024-05-15';
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 4, 4, 89.99 FROM orders WHERE region_id = 1 AND order_date = '2024-05-15';
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 7, 4, 44.99 FROM orders WHERE region_id = 1 AND order_date = '2024-05-15';

-- North Q3 — Product A orders (only 10 of the 15 customers: crash)
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, 1, '2024-08-01' FROM customers WHERE region_id = 1 AND id BETWEEN 1 AND 10;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 1, 10, 79.99 FROM orders WHERE region_id = 1 AND order_date = '2024-08-01';

-- North Q3 — other products orders (all 15 North customers, slight growth)
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, 1, '2024-08-15' FROM customers WHERE region_id = 1;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 2, 6, 49.99 FROM orders WHERE region_id = 1 AND order_date = '2024-08-15';
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 4, 4, 89.99 FROM orders WHERE region_id = 1 AND order_date = '2024-08-15';
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 7, 5, 44.99 FROM orders WHERE region_id = 1 AND order_date = '2024-08-15';