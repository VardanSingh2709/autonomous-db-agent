-- South (region_id = 2), East (region_id = 3), West (region_id = 4)
-- Same quantities for all three regions — Q2 vs Q3 mild, realistic decline

-- Q2 orders
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, region_id, '2024-05-01' FROM customers WHERE region_id = 2;
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, region_id, '2024-05-05' FROM customers WHERE region_id = 3;
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, region_id, '2024-05-10' FROM customers WHERE region_id = 4;

-- Q2 order_items — same quantities across South/East/West
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 3, 8, 29.99 FROM orders WHERE region_id IN (2,3,4) AND order_date IN ('2024-05-01','2024-05-05','2024-05-10');
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 5, 7, 34.99 FROM orders WHERE region_id IN (2,3,4) AND order_date IN ('2024-05-01','2024-05-05','2024-05-10');
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 8, 10, 69.99 FROM orders WHERE region_id IN (2,3,4) AND order_date IN ('2024-05-01','2024-05-05','2024-05-10');
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 12, 6, 64.99 FROM orders WHERE region_id IN (2,3,4) AND order_date IN ('2024-05-01','2024-05-05','2024-05-10');

-- Q3 orders
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, region_id, '2024-08-01' FROM customers WHERE region_id = 2;
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, region_id, '2024-08-05' FROM customers WHERE region_id = 3;
INSERT INTO orders (customer_id, region_id, order_date)
SELECT id, region_id, '2024-08-10' FROM customers WHERE region_id = 4;

-- Q3 order_items — mild decline
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 3, 7, 29.99 FROM orders WHERE region_id IN (2,3,4) AND order_date IN ('2024-08-01','2024-08-05','2024-08-10');
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 5, 7, 34.99 FROM orders WHERE region_id IN (2,3,4) AND order_date IN ('2024-08-01','2024-08-05','2024-08-10');
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 8, 9, 69.99 FROM orders WHERE region_id IN (2,3,4) AND order_date IN ('2024-08-01','2024-08-05','2024-08-10');
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT id, 12, 6, 64.99 FROM orders WHERE region_id IN (2,3,4) AND order_date IN ('2024-08-01','2024-08-05','2024-08-10');
