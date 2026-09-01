-- Gold Layer - Revenue by Customer
-- Aggregates revenue data by customer (only PASS quality rows)

CREATE OR REPLACE TABLE gold_revenue_by_customer AS
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(o.total_amount), 2) as total_revenue,
    ROUND(AVG(o.total_amount), 2) as avg_order_value,
    ROUND(c.lifetime_value, 2) as lifetime_value_actual
FROM silver_customers c
LEFT JOIN silver_orders o 
    ON c.customer_id = o.customer_id
    AND o.quality_check_result = 'PASS'
WHERE c.quality_check_result = 'PASS'
GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.lifetime_value
ORDER BY total_revenue DESC;
