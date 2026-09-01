-- ================================================================================
-- Databricks SQL Dashboard Queries
-- eCommerce Sales Dashboard
-- ================================================================================
-- 3 tiles: Top 10 Products, Customer Revenue Distribution, Customer Segmentation
-- ================================================================================

-- ================================================================================
-- TILE 1: Top 10 Products by Revenue (Bar Chart)
-- ================================================================================
-- X Axis: product_name
-- Y Axis: revenue
-- Sort: revenue DESC

SELECT 
    product_name,
    ROUND(total_revenue, 2) as revenue
FROM gold_sales_by_product
ORDER BY total_revenue DESC
LIMIT 10;

-- ================================================================================
-- TILE 2: Customer Revenue Distribution (Histogram)
-- ================================================================================
-- X Axis: total_revenue
-- Buckets: Auto

SELECT 
    total_revenue
FROM gold_revenue_by_customer
WHERE total_revenue > 0
ORDER BY total_revenue;

-- ================================================================================
-- TILE 3: Customer Segmentation (Pie Chart)
-- ================================================================================
-- Key: segment_type
-- Value: count

SELECT 
    segment_type,
    customer_count as count
FROM gold_customer_segmentation
ORDER BY total_revenue DESC;

-- ================================================================================
-- Optional Filter Queries
-- ================================================================================

-- Filter by Product Category (for Tile 1)
SELECT DISTINCT category
FROM gold_sales_by_product
ORDER BY category;

-- Filter by Customer Segment (for Tile 3)
SELECT DISTINCT segment_type
FROM gold_customer_segmentation
ORDER BY segment_type;
