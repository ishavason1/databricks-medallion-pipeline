#!/usr/bin/env python3
"""
Silver Layer - Quality Check: Type Validation
Flags rows with data type mismatches
"""

from pyspark.sql import functions as F
from datetime import datetime
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_type_validation(table_name, silver_table, schema_map):
    """
    Check data types match expected schema
    schema_map: dict of column_name -> expected_type
    """
    try:
        print(f"\n{'='*80}")
        print(f"QUALITY CHECK: Type Validation - {table_name}")
        print(f"{'='*80}")
        
        logger.info(f"Starting type validation for {table_name}")
        
        # Read silver table
        print(f"\n[1/3] Reading from {silver_table}...")
        df = spark.read.table(silver_table)
        total_rows = df.count()
        print(f"      Total rows: {total_rows:,}")
        
        # Get actual schema
        print(f"\n[2/3] Validating data types...")
        actual_schema = {field.name: str(field.dataType) for field in df.schema.fields}
        
        df_result = df
        type_mismatches = 0
        
        for col, expected_type in schema_map.items():
            if col in actual_schema:
                actual_type = actual_schema[col]
                if expected_type not in actual_type:
                    print(f"      ⚠️  {col}: expected {expected_type}, got {actual_type}")
                    type_mismatches += 1
                    
                    # Flag rows with type mismatch
                    df_result = df_result.withColumn(
                        "quality_check_result",
                        F.when(
                            F.col("quality_check_result") == "PASS",
                            F.lit(f"FAIL_TYPE_{col}")
                        ).otherwise(F.col("quality_check_result"))
                    )
                else:
                    print(f"      ✓ {col}: {expected_type}")
        
        # Count results
        passed = df_result.filter(F.col("quality_check_result") == "PASS").count()
        failed = total_rows - passed
        
        print(f"\n[3/3] Writing results...")
        print(f"      Rows PASSED: {passed:,}")
        print(f"      Rows FAILED: {failed:,}")
        print(f"      Type mismatches found: {type_mismatches}")
        
        # Write back to silver table
        df_result.write.format("delta").mode("overwrite").saveAsTable(silver_table)
        
        print(f"\n✓ Type validation completed for {table_name}")
        logger.info(f"Type validation completed: {passed:,} passed, {failed:,} failed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during type validation: {str(e)}")
        logger.error(f"Error in type validation: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Define expected schema for orders
    schema_map = {
        "order_id": "long",
        "customer_id": "long",
        "order_date": "date",
        "product_id": "long",
        "quantity": "long",
        "unit_price": "decimal",
        "total_amount": "decimal"
    }
    
    success = check_type_validation("Orders", "silver_orders", schema_map)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
