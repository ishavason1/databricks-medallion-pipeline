# Debugging Notes - Troubleshooting Guide

**Common Issues, Solutions, and Best Practices**

---

## 📋 OVERVIEW

Comprehensive debugging guide for troubleshooting pipeline issues at each phase.

**Quick Reference:** Jump to issue category using links below.

---

## 🔍 DEBUG CATEGORIES

1. [Data Generation Issues](#data-generation-issues)
2. [Bronze Layer Issues](#bronze-layer-issues)
3. [Silver Layer Issues](#silver-layer-issues)
4. [Gold Layer Issues](#gold-layer-issues)
5. [Dashboard Issues](#dashboard-issues)
6. [Databricks-Specific Issues](#databricks-specific-issues)
7. [Performance Issues](#performance-issues)

---

## DATA GENERATION ISSUES

### Issue: "Python: command not found"

**Symptom:** Running `python3 generate_sample_data_no_dependencies.py` fails

**Root Cause:** Python not installed or not in PATH

**Solutions:**
```bash
# Check Python version
python --version
python3 --version

# If not found, install Python 3.7+
# macOS:
brew install python3

# Windows:
winget install Python.Python.3.11

# Linux (Ubuntu/Debian):
sudo apt-get install python3 python3-pip
```

---

### Issue: "Permission denied" on CSV generation

**Symptom:** `Permission denied: 'data/customers.csv'`

**Root Cause:** No write permissions in data directory

**Solutions:**
```bash
# Check permissions
ls -ld data/

# Fix permissions
chmod 755 data/
chmod 644 data/*

# Or create new data folder
mkdir -p data
python3 src/data_generation/generate_sample_data_no_dependencies.py
```

---

### Issue: "ModuleNotFoundError"

**Symptom:** `ModuleNotFoundError: No module named 'pandas'`

**Root Cause:** Script using dependencies not in standard library

**Solution:** Use the correct script:
```bash
# CORRECT (no dependencies):
python3 src/data_generation/generate_sample_data_no_dependencies.py

# WRONG (requires Faker):
python3 src/data_generation/generate_sample_data.py
```

---

### Issue: "CSV file not created"

**Symptom:** Running script but no CSV files appear

**Root Cause:** Script error or different working directory

**Solutions:**
```bash
# Check current directory
pwd

# Navigate to project root
cd databricks-medallion-pipeline

# Run script with verbose output
python3 -u src/data_generation/generate_sample_data_no_dependencies.py

# Check what was created
ls -lh data/

# If nothing, check script for errors
python3 -m py_compile src/data_generation/generate_sample_data_no_dependencies.py
```

---

## BRONZE LAYER ISSUES

### Issue: "Table already exists"

**Symptom:** `AnalysisException: Table bronze_customers already exists`

**Root Cause:** Table exists from previous run

**Solutions:**
```sql
-- Drop existing table
DROP TABLE IF EXISTS bronze_customers;

-- Or use REPLACE mode in Python
df.write.format("delta").mode("overwrite").saveAsTable("bronze_customers")

-- Verify table is gone
SHOW TABLES;
```

---

### Issue: "CSV not found in Databricks"

**Symptom:** `FileNotFoundError: s3://... customers.csv`

**Root Cause:** File not uploaded or wrong path

**Solutions:**
```python
# List files to see what's available
dbutils.fs.ls("dbfs:/Users/[your-email]/medallion_pipeline/data/")

# Check path syntax
# WRONG: /Users/email/medallion_pipeline/data/customers.csv
# RIGHT: /Users/email@company.com/medallion_pipeline/data/customers.csv

# Upload file if missing
# Via UI: Workspace → Upload files
# Via CLI: databricks fs cp data/customers.csv dbfs:/path/
```

---

### Issue: "Schema inference failed"

**Symptom:** `Exception: Failed to infer schema from CSV`

**Root Cause:** CSV malformed or has encoding issues

**Solutions:**
```python
# Try explicit schema
from pyspark.sql.types import StructType, StructField, StringType, LongType

schema = StructType([
    StructField("customer_id", LongType()),
    StructField("customer_name", StringType()),
    # ... add all fields
])

df = spark.read.schema(schema).csv(csv_path, header=True)

# Or try different encoding
df = spark.read.option("encoding", "UTF-8").csv(csv_path, header=True)

# Check CSV file integrity locally
head -5 data/customers.csv
wc -l data/customers.csv
```

---

### Issue: "0 rows ingested"

**Symptom:** Table created but `COUNT(*) = 0`

**Root Cause:** CSV not read correctly or all rows filtered

**Solutions:**
```sql
-- Check data exists
SELECT * FROM bronze_customers LIMIT 10;

-- Count distinct values
SELECT COUNT(DISTINCT customer_id) FROM bronze_customers;

-- Check for NULL customer_ids
SELECT COUNT(*) FROM bronze_customers WHERE customer_id IS NULL;

-- In Python, debug read step
df = spark.read.csv(csv_path, header=True)
print(df.count())  # Should be > 0
df.show(5)  # Show sample data
```

---

### Issue: "Memory error during ingestion"

**Symptom:** `OutOfMemoryError` or task timeout

**Root Cause:** Cluster too small for data volume

**Solutions:**
```python
# Option 1: Increase cluster size
# In Databricks: Clusters → Select cluster → Edit → Increase worker count

# Option 2: Read in batches (if needed)
# But our 100K rows should fit in 2GB+ cluster

# Option 3: Check for memory-heavy operations
# Avoid: df.collect() (brings all data to driver)
# Use: df.count(), df.show(), df.write()
```

---

## SILVER LAYER ISSUES

### Issue: "quality_check_result column not found"

**Symptom:** `AnalysisException: Column quality_check_result does not exist`

**Root Cause:** Silver table not created or using Bronze table

**Solutions:**
```sql
-- Verify table is silver (not bronze)
DESCRIBE silver_customers;  -- Should have quality_check_result column
DESCRIBE bronze_customers;  -- Should NOT have it

-- Run create_silver_tables.py if missing
-- Check that quality check scripts ran successfully

-- If column missing, add it:
ALTER TABLE silver_customers 
ADD COLUMN quality_check_result STRING DEFAULT 'PASS';
```

---

### Issue: "No data in quality_check_result"

**Symptom:** All rows show NULL or empty string for quality_check_result

**Root Cause:** Quality check script didn't run properly

**Solutions:**
```python
# In quality check script, verify initialization
df = df.withColumn("quality_check_result", F.lit("PASS"))

# Check intermediate steps
df.select("customer_id", "quality_check_result").show(20)

# Run quality checks manually
silver_customers = spark.read.table("silver_customers")
print(silver_customers.select("quality_check_result").distinct().collect())

# Expected: ['PASS', 'FAIL_NULL_email', 'FAIL_DUPLICATE', ...]
```

---

### Issue: "All rows marked as FAIL"

**Symptom:** `quality_check_result = 'FAIL_*'` for all or most rows

**Root Cause:** Quality check too strict or data schema mismatch

**Solutions:**
```python
# Check sample data
df = spark.read.table("silver_customers")
df.filter(F.col("quality_check_result") == "PASS").show(10)

# Verify null check logic
df.select("customer_id", "email", "quality_check_result")\
  .where(F.col("email").isNull())\
  .show(5)

# Count by result type
df.groupBy("quality_check_result").count().show()

# If all FAIL, check:
# 1. Data exists in bronze table
# 2. Column names match schema
# 3. Data types are correct
```

---

### Issue: "Quality check script timeout"

**Symptom:** Script runs for > 2 minutes or doesn't complete

**Root Cause:** Inefficient queries on large dataset

**Solutions:**
```python
# Add partition pruning
df = spark.read.table("silver_customers")\
    .repartition(8)  # Better parallelization

# Cache intermediate results
df_with_rownums = df.withColumn("rn", F.row_number()...)
df_with_rownums.cache()
df_with_rownums.count()  # Force evaluation

# Check execution plan
df.explain()  # Show PLAN output

# Optimize joins
# Use broadcast for small tables
df_small = F.broadcast(small_df)
```

---

## GOLD LAYER ISSUES

### Issue: "No rows in gold tables"

**Symptom:** `gold_sales_by_product` returns 0 rows

**Root Cause:** Silver layer has no PASS rows or aggregation logic error

**Solutions:**
```sql
-- Check if PASS rows exist
SELECT COUNT(*) 
FROM silver_products 
WHERE quality_check_result = 'PASS';

-- If > 0, check aggregation logic
SELECT 
    product_id,
    COUNT(*) as order_count,
    SUM(total_amount) as revenue
FROM silver_orders
WHERE quality_check_result = 'PASS'
GROUP BY product_id
LIMIT 10;

-- If no rows, check JOIN logic
SELECT COUNT(*) FROM silver_products p
LEFT JOIN silver_orders o 
  ON p.product_id = o.product_id
  AND p.quality_check_result = 'PASS'
  AND o.quality_check_result = 'PASS';
```

---

### Issue: "Incorrect aggregation values"

**Symptom:** `total_revenue` doesn't match expected values

**Root Cause:** Aggregation logic error or filter not applied

**Solutions:**
```python
# Verify filter applied
df_filtered = spark.read.table("silver_orders")\
    .filter(F.col("quality_check_result") == "PASS")
print(f"Filtered rows: {df_filtered.count()}")

# Check calculation
df_agg = df_filtered.groupBy("product_id")\
    .agg(
        F.sum("total_amount").alias("total_revenue"),
        F.count("order_id").alias("order_count")
    )
df_agg.show()

# Verify manually
product_id_sample = 501
manual_check = spark.sql(f"""
    SELECT 
        SUM(total_amount) as revenue,
        COUNT(*) as order_count
    FROM silver_orders
    WHERE product_id = {product_id_sample}
    AND quality_check_result = 'PASS'
""")
manual_check.show()
```

---

### Issue: "Segmentation incorrect"

**Symptom:** Customer counts in segmentation don't add up

**Root Cause:** Segmentation logic error or overlap

**Solutions:**
```python
# Verify no customer overlap
df_seg = spark.read.table("gold_customer_segmentation")
total = df_seg.groupBy().sum("customer_count").collect()[0][0]
print(f"Total customers in segments: {total}")
# Should be close to 9,950 (clean customers)

# Check segmentation logic
high_value_threshold = spark.sql("""
    SELECT 
        PERCENTILE_APPROX(total_revenue, 0.75) as p75
    FROM gold_revenue_by_customer
""").collect()[0][0]
print(f"High-value threshold: {high_value_threshold}")

# Verify each segment
spark.sql("""
SELECT 
    segment_type,
    customer_count,
    ROUND(AVG(total_revenue), 2) as avg_revenue
FROM gold_customer_segmentation
GROUP BY segment_type
ORDER BY customer_count DESC
""").show()
```

---

## DASHBOARD ISSUES

### Issue: "Dashboard shows no data"

**Symptom:** Dashboard created but tiles are empty

**Root Cause:** Gold tables not populated or query incorrect

**Solutions:**
1. Verify gold tables exist:
   ```sql
   SELECT COUNT(*) FROM gold_sales_by_product;
   SELECT COUNT(*) FROM gold_revenue_by_customer;
   SELECT COUNT(*) FROM gold_customer_segmentation;
   ```

2. Test dashboard queries manually:
   ```sql
   -- Test Tile 1
   SELECT 
       product_name,
       ROUND(total_revenue, 2) as revenue
   FROM gold_sales_by_product
   ORDER BY total_revenue DESC
   LIMIT 10;
   ```

3. If queries work but dashboard empty:
   - Re-save dashboard
   - Refresh dashboard (F5)
   - Check visualization settings (X/Y axes)

---

### Issue: "Visualization shows wrong chart type"

**Symptom:** Pie chart displays as bar chart

**Root Cause:** Chart type not set correctly

**Solutions:**
1. Click visualization settings
2. Select chart type: Pie
3. Configure:
   - Key: segment_type
   - Value: customer_count
4. Save visualization

---

### Issue: "Dashboard filter not working"

**Symptom:** Filter dropdown exists but doesn't filter

**Root Cause:** Filter not linked to visualization

**Solutions:**
1. Click: Edit dashboard
2. Select filter
3. Click: Link visualization
4. Select visualizations to link
5. Save dashboard

---

## DATABRICKS-SPECIFIC ISSUES

### Issue: "Cluster not starting"

**Symptom:** Cluster status stays yellow or turns red

**Root Cause:** Capacity issues or configuration error

**Solutions:**
```
1. Check cluster status
   Clusters → Select cluster → View logs

2. Try different node type
   Clusters → Edit → Change to Standard_DS3_v2

3. Reduce worker count
   Clusters → Edit → Set workers to 1

4. Restart cluster
   Clusters → Actions → Restart
   (Wait 5-10 minutes)

5. Delete and recreate
   Clusters → Delete → Create new cluster
```

---

### Issue: "Notebook execution timeout"

**Symptom:** Notebook takes > 30 minutes to run

**Root Cause:** Inefficient query or cluster too small

**Solutions:**
```python
# Add timeout handling
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Notebook execution timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(1800)  # 30 minute timeout

# Or optimize notebook
# Split into smaller cells
# Add checkpoints:
spark.sql("CHECKPOINT TABLE table_name")

# Run cells individually instead of all at once
```

---

### Issue: "Spark job fails with OOM"

**Symptom:** `OutOfMemoryError: Java heap space`

**Root Cause:** Insufficient memory for operation

**Solutions:**
```python
# Option 1: Increase driver/executor memory
# Clusters → Edit → Advanced Options → Spark Config
# spark.driver.memory 4g
# spark.executor.memory 4g

# Option 2: Optimize code
# Don't do: df.collect() - brings all data to driver
# Do: df.write() - distributed write

# Option 3: Repartition large dataframes
df_large = df.repartition(16)  # More partitions = less per executor

# Option 4: Use Databricks Delta caching
df.cache()
df.count()  # Force cache
```

---

## PERFORMANCE ISSUES

### Issue: "Pipeline runs slower than expected"

**Symptom:** Phase 4 (quality checks) takes > 2 minutes

**Root Cause:** Inefficient queries or small cluster

**Solutions:**
```python
# Add explain plan
df.explain()  # Shows EXPLAIN output

# Example optimization:
# BEFORE: Multiple passes over data
result1 = df.filter(col1.isNull()).count()
result2 = df.filter(col2.isNotNull()).count()

# AFTER: Single pass
result = df.select([
    F.when(F.col("col1").isNull(), 1).otherwise(0).alias("null_count"),
    F.when(F.col("col2").isNotNull(), 1).otherwise(0).alias("notnull_count")
])

# Enable query optimization
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
```

---

### Issue: "Joins are slow"

**Symptom:** JOIN operation takes > 1 minute

**Root Cause:** Unbalanced partitioning or large intermediate result

**Solutions:**
```python
# Strategy 1: Broadcast small table
df_small = F.broadcast(small_df)
result = df_large.join(df_small, condition)

# Strategy 2: Repartition before join
df_large_repartitioned = df_large.repartition(16, "key_column")
df_small_repartitioned = df_small.repartition(16, "key_column")
result = df_large_repartitioned.join(df_small_repartitioned, "key_column")

# Strategy 3: Use bucketing (for persistent tables)
df.write.bucketBy(16, "key_column")\
    .mode("overwrite")\
    .option("path", "/path/to/table")\
    .saveAsTable("bucketed_table")
```

---

## 📊 DEBUGGING WORKFLOW

When encountering an issue:

1. **Identify Phase:**
   - Data Generation?
   - Bronze?
   - Silver?
   - Gold?
   - Dashboard?

2. **Gather Information:**
   ```python
   # Always check these first
   spark.sql("SHOW TABLES").show()  # What tables exist?
   spark.sql("SELECT COUNT(*) FROM table_name").show()  # Row counts?
   spark.sql("DESCRIBE table_name").show()  # Schema correct?
   ```

3. **Check Logs:**
   - Databricks: Clusters → Select cluster → Logs
   - Notebook: Cell output and error messages
   - SQL: Query results and execution plan

4. **Test Incrementally:**
   - Run one notebook at a time
   - Add print/display statements
   - Check intermediate results

5. **Search Known Issues:**
   - Check this guide first
   - Search Databricks docs
   - Check GitHub issues

---

## 📝 LOGGING BEST PRACTICES

Add logging to scripts:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Starting ingestion, expected rows: 10000")
df = spark.read.csv(path)
logger.info(f"Ingested {df.count()} rows")
logger.info(f"Columns: {df.columns}")
```

---

**Last Updated:** August 30, 2026  
**Status:** ✅ Comprehensive Debugging Guide

