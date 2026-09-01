#!/usr/bin/env python3
"""
Silver Layer - Quality Check: Completeness
Flags rows with NULL values in required columns
Adds quality_check_result column
"""

from pyspark.sql import functions as F
from datetime import datetime
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_completeness(table_name, bronze_table, silver_table, required_columns):
    """
    Check for NULL values in required columns
    """
    try:
        print(f"\n{'='*80}")
        print(f"QUALITY CHECK: Completeness - {table_name}")
        print(f"{'='*80}")
        
        logger.info(f"Starting completeness check for {table_name}")
        
        # Read bronze table
        print(f"\n[1/3] Reading from {bronze_table}...")
        df = spark.read.table(bronze_table)
        total_rows = df.count()
        print(f"      Total rows: {total_rows:,}")
        
        # Initialize quality_check_result column if not exists
        if "quality_check_result" not in df.columns:
            df = df.withColumn("quality_check_result", F.lit("PASS"))
        
        # Check each required column for NULLs
        print(f"\n[2/3] Checking for NULL values in: {', '.join(required_columns)}")
        
        for col in required_columns:
            df = df.withColumn(
                "quality_check_result",
                F.when(
                    (F.col("quality_check_result") == "PASS") & (F.col(col).isNull()),
                    F.lit(f"FAIL_NULL_{col}")
                ).otherwise(F.col("quality_check_result"))
            )
        
        # Count results
        passed = df.filter(F.col("quality_check_result") == "PASS").count()
        failed = total_rows - passed
        
        print(f"\n[3/3] Writing to {silver_table}...")
        print(f"      Rows PASSED: {passed:,}")
        print(f"      Rows FAILED: {failed:,}")
        
        # Write to silver table
        df.write.format("delta").mode("overwrite").saveAsTable(silver_table)
        
        print(f"\n✓ Completeness check completed for {table_name}")
        logger.info(f"Completeness check completed: {passed:,} passed, {failed:,} failed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during completeness check: {str(e)}")
        logger.error(f"Error in completeness check: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Customers
    success = check_completeness(
        "Customers",
        "bronze_customers",
        "silver_customers",
        ["customer_id", "customer_name", "email"]
    )
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
