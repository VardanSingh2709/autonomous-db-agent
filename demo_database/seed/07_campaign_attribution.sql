-- Q2: label first 30 orders as paid_search, next 20 as email, next 15 as social_media, remaining 10 stay organic (NULL)
WITH q2_orders_ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM orders
    WHERE order_date >= '2024-04-01' AND order_date < '2024-07-01'
)
UPDATE orders SET campaign_id = 3  -- Search Ads Q2 (paid_search)
FROM q2_orders_ranked
WHERE orders.id = q2_orders_ranked.id AND q2_orders_ranked.rn <= 30;

WITH q2_orders_ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM orders
    WHERE order_date >= '2024-04-01' AND order_date < '2024-07-01'
)
UPDATE orders SET campaign_id = 1  -- Spring Sale (email)
FROM q2_orders_ranked
WHERE orders.id = q2_orders_ranked.id AND q2_orders_ranked.rn BETWEEN 31 AND 50;

WITH q2_orders_ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM orders
    WHERE order_date >= '2024-04-01' AND order_date < '2024-07-01'
)
UPDATE orders SET campaign_id = 2  -- Summer Push (social_media)
FROM q2_orders_ranked
WHERE orders.id = q2_orders_ranked.id AND q2_orders_ranked.rn BETWEEN 51 AND 65;
-- remaining orders (rn 66-75) stay campaign_id = NULL (organic/direct)

-- Q3: paid_search collapses to just 8 orders; email=18, social=14, rest organic
WITH q3_orders_ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM orders
    WHERE order_date >= '2024-07-01' AND order_date < '2024-10-01'
)
UPDATE orders SET campaign_id = 4  -- Search Ads Q3 (paid_search)
FROM q3_orders_ranked
WHERE orders.id = q3_orders_ranked.id AND q3_orders_ranked.rn <= 8;

WITH q3_orders_ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM orders
    WHERE order_date >= '2024-07-01' AND order_date < '2024-10-01'
)
UPDATE orders SET campaign_id = 1  -- Spring Sale reused as the "email" label
FROM q3_orders_ranked
WHERE orders.id = q3_orders_ranked.id AND q3_orders_ranked.rn BETWEEN 9 AND 26;

WITH q3_orders_ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM orders
    WHERE order_date >= '2024-07-01' AND order_date < '2024-10-01'
)
UPDATE orders SET campaign_id = 5  -- Influencer Collab (social_media)
FROM q3_orders_ranked
WHERE orders.id = q3_orders_ranked.id AND q3_orders_ranked.rn BETWEEN 27 AND 40;
-- remaining orders (rn 41-70) stay campaign_id = NULL (organic/direct)