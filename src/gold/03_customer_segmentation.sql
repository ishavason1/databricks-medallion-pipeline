-- Gold Layer - Customer Segmentation
-- Segments customers by value and behavior (only PASS quality rows)

WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.customer_name,
        COUNT(DISTINCT o.order_id) as order_count,
        ROUND(SUM(o.total_amount), 2) as total_revenue
    FROM silver_customers c
    LEFT JOIN silver_orders o 
        ON c.customer_id = o.customer_id
        AND o.quality_check_result = 'PASS'
    WHERE c.quality_check_result = 'PASS'
    GROUP BY c.customer_id, c.customer_name
),
percentiles AS (
    SELECT
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_revenue) as revenue_75th
    FROM customer_metrics
    WHERE total_revenue > 0
),
segmented_customers AS (
    SELECT
        cm.customer_id,
        cm.customer_name,
        cm.order_count,
        cm.total_revenue,
        CASE
            WHEN cm.total_revenue > p.revenue_75th THEN 'High-Value'
            WHEN cm.order_count >= 5 AND cm.total_revenue <= p.revenue_75th THEN 'Repeat'
            WHEN cm.order_count = 1 THEN 'One-Time'
            WHEN cm.order_count = 0 OR cm.total_revenue IS NULL THEN 'Inactive'
            ELSE 'One-Time'
        END as segment_type
    FROM customer_metrics cm
    CROSS JOIN percentiles p
)
SELECT
    segment_type,
    COUNT(DISTINCT customer_id) as customer_count,
    ROUND(AVG(total_revenue), 2) as avg_revenue,
    ROUND(SUM(total_revenue), 2) as total_revenue
FROM segmented_customers
GROUP BY segment_type
ORDER BY total_revenue DESC;
