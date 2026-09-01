-- ================================================================================
-- Databricks Medallion Architecture - Complete Schema Definition
-- eCommerce Sales Pipeline
-- ================================================================================
-- This file defines all tables for Bronze, Silver, and Gold layers
-- ================================================================================

-- ================================================================================
-- BRONZE LAYER - RAW DATA (NO TRANSFORMATIONS)
-- ================================================================================

-- Bronze Layer: Customers
-- Source: customers.csv (10,000 rows)
-- Purpose: Raw customer data with no modifications
CREATE TABLE IF NOT EXISTS bronze_customers (
    customer_id BIGINT NOT NULL,
    customer_name STRING NOT NULL,
    email STRING,
    country STRING NOT NULL,
    signup_date DATE NOT NULL,
    customer_segment STRING NOT NULL,
    lifetime_value DECIMAL(12, 2) NOT NULL
)
USING DELTA
COMMENT 'Bronze layer: Raw customer data';

-- Add primary key constraint (informational, not enforced in Delta)
-- PRIMARY KEY (customer_id)

---

-- Bronze Layer: Orders
-- Source: orders.csv (100,000 rows)
-- Purpose: Raw order data with no modifications
CREATE TABLE IF NOT EXISTS bronze_orders (
    order_id BIGINT NOT NULL,
    customer_id BIGINT,
    order_date DATE NOT NULL,
    product_id BIGINT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    order_status STRING NOT NULL,
    payment_date DATE
)
USING DELTA
COMMENT 'Bronze layer: Raw order data';

-- Foreign Keys (informational, not enforced)
-- FOREIGN KEY (customer_id) REFERENCES bronze_customers(customer_id)
-- FOREIGN KEY (product_id) REFERENCES bronze_products(product_id)

---

-- Bronze Layer: Products
-- Source: products.csv (500 rows)
-- Purpose: Raw product data with no modifications
CREATE TABLE IF NOT EXISTS bronze_products (
    product_id BIGINT NOT NULL,
    product_name STRING NOT NULL,
    category STRING NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    reorder_level INT NOT NULL
)
USING DELTA
COMMENT 'Bronze layer: Raw product data';

-- ================================================================================
-- SILVER LAYER - QUALITY-CHECKED DATA
-- ================================================================================

-- Silver Layer: Customers with Quality Check Results
-- Purpose: Bronze customers + quality_check_result column
-- Quality checks: Completeness, Uniqueness, Type Validation
CREATE TABLE IF NOT EXISTS silver_customers (
    customer_id BIGINT NOT NULL,
    customer_name STRING NOT NULL,
    email STRING,
    country STRING NOT NULL,
    signup_date DATE NOT NULL,
    customer_segment STRING NOT NULL,
    lifetime_value DECIMAL(12, 2) NOT NULL,
    quality_check_result STRING NOT NULL DEFAULT 'PASS'
)
USING DELTA
COMMENT 'Silver layer: Quality-checked customer data with flags';

---

-- Silver Layer: Orders with Quality Check Results
-- Purpose: Bronze orders + quality_check_result column
-- Quality checks: Completeness, Uniqueness, Referential Integrity, Type Validation
CREATE TABLE IF NOT EXISTS silver_orders (
    order_id BIGINT NOT NULL,
    customer_id BIGINT,
    order_date DATE NOT NULL,
    product_id BIGINT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    order_status STRING NOT NULL,
    payment_date DATE,
    quality_check_result STRING NOT NULL DEFAULT 'PASS'
)
USING DELTA
COMMENT 'Silver layer: Quality-checked order data with flags';

---

-- Silver Layer: Products with Quality Check Results
-- Purpose: Bronze products + quality_check_result column
-- Quality checks: Completeness, Uniqueness, Type Validation
CREATE TABLE IF NOT EXISTS silver_products (
    product_id BIGINT NOT NULL,
    product_name STRING NOT NULL,
    category STRING NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    reorder_level INT NOT NULL,
    quality_check_result STRING NOT NULL DEFAULT 'PASS'
)
USING DELTA
COMMENT 'Silver layer: Quality-checked product data with flags';

-- ================================================================================
-- GOLD LAYER - BUSINESS-READY AGGREGATIONS
-- ================================================================================

-- Gold Layer: Sales by Product
-- Purpose: Aggregated sales metrics by product
-- Filter: Only PASS quality rows from silver layer
-- Aggregation: GROUP BY product with SUM and AVG
CREATE TABLE IF NOT EXISTS gold_sales_by_product (
    product_id BIGINT NOT NULL,
    product_name STRING NOT NULL,
    category STRING NOT NULL,
    total_orders BIGINT NOT NULL,
    total_revenue DECIMAL(14, 2) NOT NULL,
    avg_order_value DECIMAL(12, 2) NOT NULL
)
USING DELTA
COMMENT 'Gold layer: Aggregated sales metrics by product';

CREATE INDEX idx_gold_sales_product_id ON gold_sales_by_product (product_id);
CREATE INDEX idx_gold_sales_revenue ON gold_sales_by_product (total_revenue DESC);

---

-- Gold Layer: Revenue by Customer
-- Purpose: Aggregated revenue metrics by customer
-- Filter: Only PASS quality rows from silver layer
-- Aggregation: GROUP BY customer with SUM and AVG
CREATE TABLE IF NOT EXISTS gold_revenue_by_customer (
    customer_id BIGINT NOT NULL,
    customer_name STRING NOT NULL,
    customer_segment STRING NOT NULL,
    total_orders BIGINT NOT NULL,
    total_revenue DECIMAL(14, 2) NOT NULL,
    avg_order_value DECIMAL(12, 2) NOT NULL,
    lifetime_value_actual DECIMAL(12, 2) NOT NULL
)
USING DELTA
COMMENT 'Gold layer: Aggregated revenue metrics by customer';

CREATE INDEX idx_gold_revenue_customer_id ON gold_revenue_by_customer (customer_id);
CREATE INDEX idx_gold_revenue_segment ON gold_revenue_by_customer (customer_segment);
CREATE INDEX idx_gold_revenue_total ON gold_revenue_by_customer (total_revenue DESC);

---

-- Gold Layer: Customer Segmentation
-- Purpose: Customers segmented by value and behavior
-- Filter: Only PASS quality rows from silver layer
-- Segmentation Logic:
--   High-Value: total_revenue > 75th percentile
--   Repeat: order_count >= 5 (and not high-value)
--   One-Time: order_count = 1
--   Inactive: order_count = 0
CREATE TABLE IF NOT EXISTS gold_customer_segmentation (
    segment_type STRING NOT NULL,
    customer_count BIGINT NOT NULL,
    avg_revenue DECIMAL(14, 2) NOT NULL,
    total_revenue DECIMAL(14, 2) NOT NULL
)
USING DELTA
COMMENT 'Gold layer: Customer segmentation by value and behavior';

CREATE INDEX idx_gold_segment_type ON gold_customer_segmentation (segment_type);
CREATE INDEX idx_gold_segment_revenue ON gold_customer_segmentation (total_revenue DESC);

-- ================================================================================
-- VIEWS FOR COMMON QUERIES
-- ================================================================================

-- View: Quality Check Summary by Table
CREATE OR REPLACE VIEW vw_quality_check_summary AS
SELECT 
    'customers' as table_name,
    quality_check_result,
    COUNT(*) as row_count
FROM silver_customers
GROUP BY quality_check_result
UNION ALL
SELECT 
    'orders' as table_name,
    quality_check_result,
    COUNT(*) as row_count
FROM silver_orders
GROUP BY quality_check_result
UNION ALL
SELECT 
    'products' as table_name,
    quality_check_result,
    COUNT(*) as row_count
FROM silver_products
GROUP BY quality_check_result;

---

-- View: Data Quality Issues Summary
CREATE OR REPLACE VIEW vw_quality_issues AS
SELECT 
    'customers - NULL emails' as issue_type,
    COUNT(*) as issue_count
FROM silver_customers
WHERE quality_check_result LIKE 'FAIL_NULL_email'
UNION ALL
SELECT 
    'customers - Duplicates',
    COUNT(*)
FROM silver_customers
WHERE quality_check_result = 'FAIL_DUPLICATE'
UNION ALL
SELECT 
    'orders - NULL customer_id',
    COUNT(*)
FROM silver_orders
WHERE quality_check_result LIKE 'FAIL_NULL_customer_id'
UNION ALL
SELECT 
    'orders - NULL product_id',
    COUNT(*)
FROM silver_orders
WHERE quality_check_result LIKE 'FAIL_NULL_product_id'
UNION ALL
SELECT 
    'orders - Invalid customer FK',
    COUNT(*)
FROM silver_orders
WHERE quality_check_result LIKE 'FAIL_INVALID_customers_FK'
UNION ALL
SELECT 
    'orders - Invalid product FK',
    COUNT(*)
FROM silver_orders
WHERE quality_check_result LIKE 'FAIL_INVALID_products_FK'
UNION ALL
SELECT 
    'orders - Duplicates',
    COUNT(*)
FROM silver_orders
WHERE quality_check_result = 'FAIL_DUPLICATE';

---

-- View: Top 10 Products by Revenue (for Dashboard)
CREATE OR REPLACE VIEW vw_top_10_products AS
SELECT 
    product_name,
    total_revenue,
    total_orders,
    avg_order_value
FROM gold_sales_by_product
ORDER BY total_revenue DESC
LIMIT 10;

---

-- View: Customer Segmentation Breakdown
CREATE OR REPLACE VIEW vw_customer_segments AS
SELECT 
    segment_type,
    customer_count,
    ROUND((customer_count * 100.0 / SUM(customer_count) OVER ()), 2) as pct_of_total,
    avg_revenue,
    total_revenue
FROM gold_customer_segmentation
ORDER BY total_revenue DESC;

-- ================================================================================
-- DATA QUALITY CONSTRAINTS
-- ================================================================================

-- Note: Delta Lake doesn't enforce constraints at the table level,
-- but these are implemented in the quality check scripts

-- Bronze Constraints:
-- - customer_id: NOT NULL, BIGINT, UNIQUE
-- - email: STRING (can be NULL)
-- - signup_date: DATE (2020-2024 range)
-- - lifetime_value: DECIMAL >= 0
-- - order_id: NOT NULL, BIGINT, UNIQUE
-- - customer_id: BIGINT (can be NULL - quality issue)
-- - product_id: BIGINT (can be NULL - quality issue)
-- - quantity: INT > 0
-- - unit_price: DECIMAL >= 0
-- - total_amount: DECIMAL >= 0
-- - product_id: NOT NULL, BIGINT, UNIQUE
-- - price: DECIMAL > 0
-- - cost: DECIMAL > 0
-- - stock_quantity: INT >= 0

-- ================================================================================
-- INDEXES FOR PERFORMANCE
-- ================================================================================

-- Bronze Layer Indexes
CREATE INDEX IF NOT EXISTS idx_bronze_customers_id ON bronze_customers (customer_id);
CREATE INDEX IF NOT EXISTS idx_bronze_orders_id ON bronze_orders (order_id);
CREATE INDEX IF NOT EXISTS idx_bronze_orders_customer ON bronze_orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_bronze_orders_product ON bronze_orders (product_id);
CREATE INDEX IF NOT EXISTS idx_bronze_products_id ON bronze_products (product_id);

-- Silver Layer Indexes
CREATE INDEX IF NOT EXISTS idx_silver_customers_quality ON silver_customers (quality_check_result);
CREATE INDEX IF NOT EXISTS idx_silver_orders_quality ON silver_orders (quality_check_result);
CREATE INDEX IF NOT EXISTS idx_silver_products_quality ON silver_products (quality_check_result);

-- Gold Layer Indexes (already created above)

-- ================================================================================
-- STATISTICS FOR QUERY OPTIMIZATION
-- ================================================================================

-- Generate column statistics for Bronze tables
-- ANALYZE TABLE bronze_customers COMPUTE STATISTICS;
-- ANALYZE TABLE bronze_orders COMPUTE STATISTICS;
-- ANALYZE TABLE bronze_products COMPUTE STATISTICS;

-- Generate column statistics for Silver tables
-- ANALYZE TABLE silver_customers COMPUTE STATISTICS;
-- ANALYZE TABLE silver_orders COMPUTE STATISTICS;
-- ANALYZE TABLE silver_products COMPUTE STATISTICS;

-- Generate column statistics for Gold tables
-- ANALYZE TABLE gold_sales_by_product COMPUTE STATISTICS;
-- ANALYZE TABLE gold_revenue_by_customer COMPUTE STATISTICS;
-- ANALYZE TABLE gold_customer_segmentation COMPUTE STATISTICS;

-- ================================================================================
-- SUMMARY OF TABLES
-- ================================================================================

-- Bronze Layer (3 tables, raw data):
--   - bronze_customers: 10,000 rows
--   - bronze_orders: 100,000 rows
--   - bronze_products: 500 rows
--   Total: 110,500 rows

-- Silver Layer (3 tables, quality-checked):
--   - silver_customers: 10,000 rows + quality_check_result
--   - silver_orders: 100,000 rows + quality_check_result
--   - silver_products: 500 rows + quality_check_result
--   Total: 110,500 rows

-- Gold Layer (3 tables, aggregated):
--   - gold_sales_by_product: 500 rows (one per product)
--   - gold_revenue_by_customer: 9,950 rows (clean customers only)
--   - gold_customer_segmentation: 4 rows (one per segment)
--   Total: 10,454 rows

-- Views (4 aggregate queries):
--   - vw_quality_check_summary: Quality metrics by table
--   - vw_quality_issues: Issues breakdown
--   - vw_top_10_products: Top products for dashboard
--   - vw_customer_segments: Segment breakdown

-- ================================================================================
-- END OF SCHEMA DEFINITION
-- ================================================================================

