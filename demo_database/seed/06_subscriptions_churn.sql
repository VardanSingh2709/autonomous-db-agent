-- Basic tier: 30 subscriptions -> ids 1-30
INSERT INTO subscriptions (customer_id, tier, start_date, end_date, status)
SELECT ((n - 1) % 60) + 1, 'Basic', '2023-06-01', NULL, 'active'
FROM generate_series(1, 30) AS n;

-- Premium tier: 30 subscriptions -> ids 31-60
INSERT INTO subscriptions (customer_id, tier, start_date, end_date, status)
SELECT ((n - 1) % 60) + 1, 'Premium', '2023-06-01', NULL, 'active'
FROM generate_series(1, 30) AS n;

-- Enterprise tier: 30 subscriptions -> ids 61-90
INSERT INTO subscriptions (customer_id, tier, start_date, end_date, status)
SELECT ((n - 1) % 60) + 1, 'Enterprise', '2023-06-01', NULL, 'active'
FROM generate_series(1, 30) AS n;

-- Basic: 2 cancel in Q2, 2 cancel in Q3 (stable ~7%)
UPDATE subscriptions SET status = 'cancelled', end_date = '2024-05-15' WHERE id IN (1, 2);
UPDATE subscriptions SET status = 'cancelled', end_date = '2024-08-15' WHERE id IN (3, 4);

-- Premium: 2 cancel in Q2 (normal), 7 cancel in Q3 (SPIKE to 25%)
UPDATE subscriptions SET status = 'cancelled', end_date = '2024-05-20' WHERE id IN (31, 32);
UPDATE subscriptions SET status = 'cancelled', end_date = '2024-08-20' WHERE id IN (33, 34, 35, 36, 37, 38, 39);

-- Enterprise: 1 cancels in Q2, 1 cancels in Q3 (stable ~3.4%)
UPDATE subscriptions SET status = 'cancelled', end_date = '2024-05-25' WHERE id IN (61);
UPDATE subscriptions SET status = 'cancelled', end_date = '2024-08-25' WHERE id IN (62);