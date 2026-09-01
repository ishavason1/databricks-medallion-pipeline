#!/usr/bin/env python3
"""
Silver Layer - Quality Check: Uniqueness
Flags rows with duplicate primary keys
"""

from pyspark.sql import functions as F, Window
from datetime import datetime
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_uniqueness(table_name, bronze_table, silver_table, pk_column):
    """
    Check for duplicate primary keys
    """
    try:
        print(f"\n{'='*80}")
        print(f"QUALITY CHECK: Uniqueness - {table_name}")
        print(f"{'='*80}")
        
        logger.info(f"Starting uniqueness check for {table_name}")
        
        # Read silver table (has quality_check_result from previous check)
        print(f"\n[1/3] Reading from silver_{table_name.lower()}...")
        df = spark.read.table(f"silver_{table_name.lower()}")
        total_rows = df.count()
        print(f"      Total rows: {total_rows:,}")
        
        # Count occurrences of each primary key
        print(f"\n[2/3] Checking for duplicates in {pk_column}...")
        
        window_spec = Window.partitionBy(pk_column)
        df_with_count = df.withColumn("pk_count", F.count(pk_column).over(window_spec))
        
        # Flag duplicates if not already flagged
        df_result = df_with_count.withColumn(
            "quality_check_result",
            F.when(
                (F.col("quality_check_result") == "PASS") & (F.col("pk_count") > 1),
                F.lit("FAIL_DUPLICATE")
            ).otherwise(F.col("quality_check_result"))
        ).drop("pk_count")
        
        # Count results
        passed = df_result.filter(F.col("quality_check_result") == "PASS").count()
        failed = total_rows - passed
        
        print(f"\n[3/3] Writing results...")
        print(f"      Rows PASSED: {passed:,}")
        print(f"      Rows FAILED: {failed:,}")
        
        # Write back to silver table
        df_result.write.format("delta").mode("overwrite").saveAsTable(f"silver_{table_name.lower()}")
        
        print(f"\n✓ Uniqueness check completed for {table_name}")
        logger.info(f"Uniqueness check completed: {passed:,} passed, {failed:,} failed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during uniqueness check: {str(e)}")
        logger.error(f"Error in uniqueness check: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = check_uniqueness("Customers", "silver_customers", "silver_customers", "customer_id")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
