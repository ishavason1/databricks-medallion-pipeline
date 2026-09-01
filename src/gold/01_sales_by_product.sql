-- Gold Layer - Sales by Product
-- Aggregates sales data by product (only PASS quality rows)

CREATE OR REPLACE TABLE gold_sales_by_product AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(o.total_amount), 2) as total_revenue,
    ROUND(AVG(o.total_amount), 2) as avg_order_value
FROM silver_products p
LEFT JOIN silver_orders o 
    ON p.product_id = o.product_id
    AND o.quality_check_result = 'PASS'
WHERE p.quality_check_result = 'PASS'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC;
