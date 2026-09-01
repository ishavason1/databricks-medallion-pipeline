# Databricks notebook source

from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("GOLD LAYER - AGGREGATIONS ORCHESTRATION")
print("="*80)

start_time = datetime.now()
print(f"\nAggregations started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

results = {}

# ========================================
# [1/3] SALES BY PRODUCT
# ========================================

print("\n[1/3] Creating gold_sales_by_product...")

try:
    spark.sql("""
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
        ORDER BY total_revenue DESC
    """)
    
    row_count = spark.sql("SELECT COUNT(*) as count FROM gold_sales_by_product").collect()[0][0]
    print(f"   ✓ gold_sales_by_product created: {row_count:,} rows")
    logger.info(f"gold_sales_by_product created with {row_count:,} rows")
    results["Sales by Product"] = True
    
except Exception as e:
    print(f"   ❌ Failed: {str(e)}")
    logger.error(f"Error creating gold_sales_by_product: {str(e)}", exc_info=True)
    results["Sales by Product"] = False

# ========================================
# [2/3] REVENUE BY CUSTOMER
# ========================================

print("\n[2/3] Creating gold_revenue_by_customer...")

try:
    spark.sql("""
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
        ORDER BY total_revenue DESC
    """)
    
    row_count = spark.sql("SELECT COUNT(*) as count FROM gold_revenue_by_customer").collect()[0][0]
    print(f"   ✓ gold_revenue_by_customer created: {row_count:,} rows")
    logger.info(f"gold_revenue_by_customer created with {row_count:,} rows")
    results["Revenue by Customer"] = True
    
except Exception as e:
    print(f"   ❌ Failed: {str(e)}")
    logger.error(f"Error creating gold_revenue_by_customer: {str(e)}", exc_info=True)
    results["Revenue by Customer"] = False

# ========================================
# [3/3] CUSTOMER SEGMENTATION
# ========================================

print("\n[3/3] Creating gold_customer_segmentation...")

try:
    spark.sql("""
        CREATE OR REPLACE TABLE gold_customer_segmentation AS
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
        ORDER BY total_revenue DESC
    """)
    
    row_count = spark.sql("SELECT COUNT(*) as count FROM gold_customer_segmentation").collect()[0][0]
    print(f"   ✓ gold_customer_segmentation created: {row_count:,} rows")
    logger.info(f"gold_customer_segmentation created with {row_count:,} rows")
    results["Customer Segmentation"] = True
    
except Exception as e:
    print(f"   ❌ Failed: {str(e)}")
    logger.error(f"Error creating gold_customer_segmentation: {str(e)}", exc_info=True)
    results["Customer Segmentation"] = False

# ========================================
# SUMMARY
# ========================================

print("\n" + "="*80)
print("GOLD LAYER SUMMARY")
print("="*80)

try:
    sales_count = spark.sql("SELECT COUNT(*) as count FROM gold_sales_by_product").collect()[0][0]
    print(f"\ngold_sales_by_product: {sales_count:,} products")
    
    customer_count = spark.sql("SELECT COUNT(*) as count FROM gold_revenue_by_customer").collect()[0][0]
    print(f"gold_revenue_by_customer: {customer_count:,} customers")
    
    segment_count = spark.sql("SELECT COUNT(*) as count FROM gold_customer_segmentation").collect()[0][0]
    print(f"gold_customer_segmentation: {segment_count:,} segments")
    
    # Show segmentation breakdown
    print("\n[Customer Segments]")
    segment_df = spark.sql("SELECT segment_type, customer_count, total_revenue FROM gold_customer_segmentation ORDER BY total_revenue DESC")
    for row in segment_df.collect():
        print(f"  {row['segment_type']}: {row['customer_count']:,} customers, ${row['total_revenue']:,.2f} revenue")
    
except Exception as e:
    print(f"Error retrieving summary: {str(e)}")
    logger.error(f"Error retrieving summary: {str(e)}", exc_info=True)

# Overall status
print("\n" + "="*80)
print("EXECUTION STATUS")
print("="*80)

for table, success in results.items():
    status = "✓ SUCCESS" if success else "❌ FAILED"
    print(f"{table}: {status}")

end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

print(f"\nAggregations ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total duration: {duration:.2f} seconds")

all_successful = all(results.values())

if all_successful:
    print("\n✓ All gold layer aggregations completed successfully!")
else:
    print("\n❌ Some aggregations failed!")

print("="*80 + "\n")
