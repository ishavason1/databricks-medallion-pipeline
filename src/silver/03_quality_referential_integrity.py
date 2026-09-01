#!/usr/bin/env python3
"""
Silver Layer - Quality Check: Referential Integrity
Flags rows with orphan foreign keys (FK doesn't exist in referenced table)
Uses LEFT JOIN to find orphans
"""

from pyspark.sql import functions as F
from datetime import datetime
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_referential_integrity(table_name, silver_table, ref_table, fk_column, pk_column, fk_name):
    """
    Check foreign key integrity using LEFT JOIN
    Flags rows where FK doesn't exist in reference table
    """
    try:
        print(f"\n{'='*80}")
        print(f"QUALITY CHECK: Referential Integrity - {table_name}")
        print(f"{'='*80}")
        
        logger.info(f"Starting referential integrity check for {table_name}")
        
        # Read silver table
        print(f"\n[1/3] Reading from {silver_table}...")
        df = spark.read.table(silver_table)
        total_rows = df.count()
        print(f"      Total rows: {total_rows:,}")
        
        # Read reference table
        print(f"      Reading from {ref_table}...")
        df_ref = spark.read.table(ref_table)
        ref_count = df_ref.select(pk_column).distinct().count()
        print(f"      Reference table rows: {ref_count:,}")
        
        # LEFT JOIN to find orphans
        print(f"\n[2/3] Checking FK {fk_column} against {ref_table}.{pk_column}...")
        
        df_join = df.join(
            df_ref.select(pk_column),
            df[fk_column] == df_ref[pk_column],
            "left"
        )
        
        # Flag rows where FK doesn't exist (NULL in reference table)
        df_result = df_join.withColumn(
            "quality_check_result",
            F.when(
                (F.col("quality_check_result") == "PASS") & (F.col(pk_column).isNull()),
                F.lit(f"FAIL_INVALID_{fk_name}_FK")
            ).otherwise(F.col("quality_check_result"))
        ).drop(pk_column)
        
        # Count results
        passed = df_result.filter(F.col("quality_check_result") == "PASS").count()
        failed = total_rows - passed
        
        print(f"\n[3/3] Writing results...")
        print(f"      Rows PASSED: {passed:,}")
        print(f"      Rows FAILED: {failed:,}")
        
        # Write back to silver table
        df_result.write.format("delta").mode("overwrite").saveAsTable(silver_table)
        
        print(f"\n✓ Referential integrity check completed for {table_name}")
        logger.info(f"Referential integrity check completed: {passed:,} passed, {failed:,} failed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during referential integrity check: {str(e)}")
        logger.error(f"Error in referential integrity check: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = check_referential_integrity(
        "Orders",
        "silver_orders",
        "bronze_customers",
        "customer_id",
        "customer_id",
        "customers"
    )
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
