#!/usr/bin/env python3
"""
Bronze Layer - Ingest Customers
Reads customers.csv and loads raw data to bronze_customers Delta table
No transformations - data kept exactly as-is
"""

from pyspark.sql import SparkSession
from datetime import datetime
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_ingestion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def ingest_customers():
    """
    Ingest customers.csv to bronze_customers Delta table
    """
    try:
        print("\n" + "="*80)
        print("BRONZE LAYER: Ingesting Customers")
        print("="*80)
        
        # Initialize Spark Session
        spark = SparkSession.builder \
            .appName("ingest_customers") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
            .getOrCreate()
        
        logger.info("Spark Session initialized")
        
        # Read CSV file
        csv_path = "data/customers.csv"
        print(f"\n[1/3] Reading CSV file: {csv_path}")
        
        df_customers = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(csv_path)
        
        logger.info(f"Successfully read customers.csv")
        
        # Validate row count
        row_count = df_customers.count()
        expected_count = 10000
        
        print(f"[2/3] Validating row count...")
        print(f"      Read rows: {row_count}")
        print(f"      Expected: {expected_count}")
        
        if row_count != expected_count:
            logger.warning(f"Row count mismatch! Expected {expected_count}, got {row_count}")
            print(f"      ⚠️  WARNING: Row count mismatch!")
        else:
            print(f"      ✓ Row count validated")
        
        # Display schema
        print(f"\n[Schema]")
        df_customers.printSchema()
        
        # Write to Delta Lake (overwrite mode for idempotency)
        print(f"\n[3/3] Writing to Delta table: bronze_customers")
        
        df_customers.write \
            .format("delta") \
            .mode("overwrite") \
            .option("mergeSchema", "false") \
            .saveAsTable("bronze_customers")
        
        logger.info(f"Successfully wrote {row_count} rows to bronze_customers")
        
        # Log ingestion metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[Ingestion Metadata]")
        print(f"  Timestamp: {timestamp}")
        print(f"  Table: bronze_customers")
        print(f"  Source: data/customers.csv")
        print(f"  Rows Ingested: {row_count}")
        print(f"  Status: SUCCESS ✓")
        
        logger.info(f"Customers ingestion completed successfully at {timestamp}")
        
        print("\n" + "="*80)
        print("Customers ingestion completed successfully!")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during customers ingestion:")
        print(f"   {str(e)}")
        logger.error(f"Error ingesting customers: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = ingest_customers()
    sys.exit(0 if success else 1)
