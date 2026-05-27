-- Q1 Monthly revenue trend

SELECT 
    date_trunc('month', order_date) AS month,
    COUNT(*) AS orders,
    SUM(total) AS revenue
FROM shop.orders
GROUP BY month
ORDER BY month;

-- Q2 Top 10 products by revenue

SELECT 
    p.name AS product_name,
    SUM(oi.quantity) AS total_qty,
    SUM(oi.quantity * oi.unit_price_at_sale) AS revenue
FROM shop.order_item oi
JOIN shop.product p 
    ON oi.product_id = p.product_id
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 10;

-- Q3 Average order value by status

SELECT 
    o.status,
    COUNT(o.order_id) AS number_of_orders,
    ROUND(AVG(o.total), 2) AS average_total,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY o.total) AS median_total
FROM shop.orders o
GROUP BY o.status;

-- Q4 Dormant customers

SELECT 
    c.customer_id,
    c.email,
    cast(MAX(o.order_date) as DATE) AS last_order_date,
    CURRENT_DATE - MAX(o.order_date)::DATE AS days_dormant
FROM shop.customer c
LEFT JOIN shop.orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.email
HAVING MAX(o.order_date) < CURRENT_DATE - INTERVAL '90 days'
ORDER BY days_dormant DESC;

-- Q5 Top customers by lifetime spend

SELECT
    RANK() OVER (ORDER BY SUM(o.total) desc) AS rank,
    c.email,
    SUM(o.total) AS lifetime_spend,
    LAG(SUM(o.total)) OVER (
            ORDER BY SUM(o.total) desc ) - SUM(o.total) 
            AS gap_to_previous
FROM shop.customer c
JOIN shop.orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.email
ORDER BY lifetime_spend DESC