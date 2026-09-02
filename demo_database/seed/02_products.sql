-- Electronics
INSERT INTO products (name, category_id, price, cost) VALUES
    ('Product A - Wireless Earbuds', (SELECT id FROM product_categories WHERE name = 'Electronics'), 79.99, 35.00),
    ('Bluetooth Speaker', (SELECT id FROM product_categories WHERE name = 'Electronics'), 49.99, 22.00),
    ('USB-C Charging Hub', (SELECT id FROM product_categories WHERE name = 'Electronics'), 29.99, 12.00),

-- Home & Kitchen
    ('Ceramic Cookware Set', (SELECT id FROM product_categories WHERE name = 'Home & Kitchen'), 89.99, 40.00),
    ('Electric Kettle', (SELECT id FROM product_categories WHERE name = 'Home & Kitchen'), 34.99, 15.00),
    ('Knife Block Set', (SELECT id FROM product_categories WHERE name = 'Home & Kitchen'), 59.99, 25.00),

-- Apparel
    ('Cotton Hoodie', (SELECT id FROM product_categories WHERE name = 'Apparel'), 44.99, 18.00),
    ('Running Shoes', (SELECT id FROM product_categories WHERE name = 'Apparel'), 69.99, 30.00),
    ('Denim Jacket', (SELECT id FROM product_categories WHERE name = 'Apparel'), 79.99, 34.00),

-- Beauty
    ('Skincare Set', (SELECT id FROM product_categories WHERE name = 'Beauty'), 39.99, 16.00),
    ('Hair Dryer', (SELECT id FROM product_categories WHERE name = 'Beauty'), 54.99, 24.00),
    ('Perfume', (SELECT id FROM product_categories WHERE name = 'Beauty'), 64.99, 28.00);