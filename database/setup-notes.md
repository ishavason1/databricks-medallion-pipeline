# Setup Notes - Complete Installation & Configuration Guide

**Databricks Medallion Architecture Pipeline - Setup Instructions**

---

## 📋 OVERVIEW

Complete step-by-step guide to set up the pipeline from scratch.

**Estimated Time:** 30-45 minutes  
**Prerequisites:** Databricks account, Git, Python 3.7+  
**Difficulty:** Intermediate

---

## ✅ PRE-REQUISITES

### 1. Databricks Workspace
- [ ] Active Databricks account (Community Edition or paid)
- [ ] Access to workspace
- [ ] Permissions to create clusters, notebooks, tables

### 2. Local Environment
- [ ] Python 3.7+ installed
- [ ] Git installed
- [ ] Text editor or IDE
- [ ] Terminal/command line access

### 3. Network Access
- [ ] Internet access to GitHub (for code repo)
- [ ] Access to Databricks cloud
- [ ] No proxy/firewall blocking

---

## 🚀 SETUP STEPS

### Step 1: Clone Repository (5 min)

```bash
# Clone the repository
git clone https://github.com/isha-vason/databricks-medallion-pipeline.git
cd databricks-medallion-pipeline

# Verify structure
ls -la
# Expected output:
# ├── README.md
# ├── src/
# ├── data/
# ├── dashboard/
# └── ...
```

**Troubleshooting:**
- If git not installed: `brew install git` (Mac) or `winget install git` (Windows)
- If permission denied: Check SSH keys or use HTTPS clone URL

---

### Step 2: Generate Test Data (5 min)

```bash
# Navigate to data generation script
cd src/data_generation

# Run data generator (creates 3 CSV files)
python3 generate_sample_data_no_dependencies.py

# Verify files were created
ls -lh ../../data/
# Expected output:
# customers.csv  (1.0 MB, 10,001 lines)
# orders.csv     (10.0 MB, 100,001 lines)
# products.csv   (50 KB, 501 lines)

# Verify row counts
wc -l ../../data/*.csv
# Expected: 10001, 100001, 501 (including headers)
```

**Troubleshooting:**
- If "no module named random": Python not found, install Python 3.7+
- If file creation fails: Check disk space (need ~15 MB)
- If permission denied: `chmod +x generate_sample_data_no_dependencies.py`

---

### Step 3: Set Up Databricks Workspace (10 min)

#### 3.1: Create Workspace Folder
```
Workspace → Users → [Your Email] → Create Folder
Name: medallion_pipeline
```

#### 3.2: Create Data Folder
```
medallion_pipeline → Create Folder → Name: data
```

#### 3.3: Upload CSV Files to Databricks

**Option A: Web Upload (Easiest)**
1. Go to Databricks workspace
2. Navigate to: Users → [Your Email] → medallion_pipeline → data
3. Click: Upload files
4. Select: customers.csv, orders.csv, products.csv
5. Wait for upload (may take 1-2 minutes for large files)

**Option B: Databricks CLI**
```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token
# Enter: Databricks instance URL
# Enter: API token (from Databricks account settings)

# Upload files
databricks fs cp data/customers.csv dbfs:/Users/[email]/medallion_pipeline/data/
databricks fs cp data/orders.csv dbfs:/Users/[email]/medallion_pipeline/data/
databricks fs cp data/products.csv dbfs:/Users/[email]/medallion_pipeline/data/

# Verify upload
databricks fs ls dbfs:/Users/[email]/medallion_pipeline/data/
```

**Verification:**
```sql
-- In Databricks SQL, verify files
SHOW DATABASES;  -- Find default database
LIST 's3://...medallion_pipeline/data/'  -- List uploaded files
```

---

### Step 4: Create Databricks Cluster (5 min)

1. Go to Databricks workspace
2. Click: Compute (left sidebar)
3. Click: Create Cluster
4. Configuration:
   - **Cluster Name:** medallion-pipeline
   - **Policy:** Unrestricted
   - **Databricks Runtime:** 13.3 LTS (Spark 3.4, Scala 2.12)
   - **Node Type:** Single Node (for testing) or Multi-node for production
   - **Min Workers:** 1
   - **Max Workers:** 2
5. Click: Create Cluster
6. Wait for cluster to start (~3-5 minutes)

**Status Indicator:**
- Green: Running ✅
- Yellow: Starting ⏳
- Red: Error ❌

---

### Step 5: Create Notebooks & Upload Code (10 min)

#### 5.1: Create Bronze Layer Notebooks

**Notebook 1: 01_ingest_customers.py**
1. Go to medallion_pipeline folder
2. Create → Notebook
3. Name: 01_ingest_customers
4. Language: Python
5. Copy content from: `src/bronze/01_ingest_customers.py`
6. Paste into notebook
7. Attach cluster: Select medallion-pipeline
8. Click: Run

**Notebook 2: 02_ingest_orders.py**
- Repeat for `src/bronze/02_ingest_orders.py`

**Notebook 3: 03_ingest_products.py**
- Repeat for `src/bronze/03_ingest_products.py`

#### 5.2: Create Silver Layer Notebook

**Notebook: create_silver_tables.py**
1. Create → Notebook
2. Name: create_silver_tables
3. Copy from: `src/silver/create_silver_tables.py`
4. Paste and run

#### 5.3: Create Gold Layer Notebook

**Notebook: create_gold_tables.py**
1. Create → Notebook
2. Name: create_gold_tables
3. Copy from: `src/gold/create_gold_tables.py`
4. Paste and run

---

### Step 6: Run Bronze Layer (5 min)

```python
# In Databricks Notebook (01_ingest_customers)

csv_path = "/Users/[your-email]/medallion_pipeline/data/customers.csv"
df = spark.read.option("header","true").option("inferSchema","true").csv(csv_path)
df.write.format("delta").mode("overwrite").saveAsTable("bronze_customers")

# Run this notebook
# Expected output: 10,000 rows ingested
```

**Repeat for:**
- 02_ingest_orders → bronze_orders (100,000 rows)
- 03_ingest_products → bronze_products (500 rows)

**Verification:**
```sql
-- In SQL cell
SELECT COUNT(*) FROM bronze_customers;  -- 10,000
SELECT COUNT(*) FROM bronze_orders;     -- 100,000
SELECT COUNT(*) FROM bronze_products;   -- 500
```

---

### Step 7: Run Silver Layer (5 min)

```python
# In create_silver_tables notebook

# This runs all 4 quality checks and creates silver tables
# Execution time: ~80 seconds
# Output: silver_customers, silver_orders, silver_products (with quality_check_result)
```

**Verification:**
```sql
-- Check PASS vs FAIL rows
SELECT quality_check_result, COUNT(*) 
FROM silver_customers 
GROUP BY quality_check_result;
```

---

### Step 8: Run Gold Layer (5 min)

```python
# In create_gold_tables notebook

# This creates all 3 aggregation tables
# Execution time: ~45 seconds
# Output: gold_sales_by_product, gold_revenue_by_customer, gold_customer_segmentation
```

**Verification:**
```sql
-- Check gold tables
SELECT * FROM gold_sales_by_product LIMIT 10;
SELECT * FROM gold_revenue_by_customer LIMIT 10;
SELECT * FROM gold_customer_segmentation;
```

---

### Step 9: Create Databricks Workflow (Optional but Recommended) (10 min)

**Purpose:** Automate pipeline execution

1. Go to Workflows (left sidebar)
2. Click: Create Job
3. Configuration:
   - **Job name:** medallion_pipeline
   - **Cluster:** Select medallion-pipeline
   - **Tasks:**
     - Task 1: 01_ingest_customers (notebook path)
     - Task 2: 02_ingest_orders (depends on Task 1)
     - Task 3: 03_ingest_products (depends on Task 1)
     - Task 4: create_silver_tables (depends on Tasks 1-3)
     - Task 5: create_gold_tables (depends on Task 4)
4. Schedule:
   - (Optional) Click: Add schedule
   - Frequency: Daily at 2:00 AM
5. Click: Create

---

### Step 10: Create Dashboard (10 min)

**See:** `dashboard/DASHBOARD_SETUP_GUIDE.md` for complete instructions

Quick Summary:
1. Go to SQL (left sidebar)
2. Create 3 queries (from `dashboard/dashboard_queries.sql`)
3. Create visualizations (Bar, Histogram, Pie)
4. Save to dashboard: `eCommerce Sales Dashboard`

---

## 🔑 CONFIGURATION

### Important Paths (Update with Your Email)

**Local File Path:**
```bash
/Users/isha.vason@tothenew.com/medallion_pipeline/data/customers.csv
```

**Databricks DBFS Path:**
```
dbfs:/Users/isha.vason@tothenew.com/medallion_pipeline/data/customers.csv
```

**In Notebooks, Use:**
```python
csv_path = "/Users/isha.vason@tothenew.com/medallion_pipeline/data/customers.csv"
df = spark.read.csv(csv_path, header=True, inferSchema=True)
```

### Databricks Configuration

**Spark Settings (Optional):**
```python
# In first cell of notebook
spark.conf.set("spark.sql.shuffle.partitions", "100")
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
```

---

## 🧪 VERIFICATION CHECKLIST

After completing all steps:

- [ ] All 3 CSV files uploaded to Databricks
- [ ] bronze_customers table exists (10,000 rows)
- [ ] bronze_orders table exists (100,000 rows)
- [ ] bronze_products table exists (500 rows)
- [ ] silver_customers table exists with quality_check_result
- [ ] silver_orders table exists with quality_check_result
- [ ] silver_products table exists with quality_check_result
- [ ] gold_sales_by_product table exists (500 rows)
- [ ] gold_revenue_by_customer table exists (~9,950 rows)
- [ ] gold_customer_segmentation table exists (4 rows)
- [ ] Dashboard displays 3 visualizations
- [ ] All queries return data

**Quick Verification Query:**
```sql
-- Run in Databricks SQL to verify everything
SELECT 'bronze_customers' as table_name, COUNT(*) as row_count FROM bronze_customers
UNION ALL
SELECT 'bronze_orders', COUNT(*) FROM bronze_orders
UNION ALL
SELECT 'bronze_products', COUNT(*) FROM bronze_products
UNION ALL
SELECT 'silver_customers', COUNT(*) FROM silver_customers
UNION ALL
SELECT 'gold_sales_by_product', COUNT(*) FROM gold_sales_by_product
UNION ALL
SELECT 'gold_revenue_by_customer', COUNT(*) FROM gold_revenue_by_customer
UNION ALL
SELECT 'gold_customer_segmentation', COUNT(*) FROM gold_customer_segmentation;
```

---

## 🆘 TROUBLESHOOTING

### Issue: "CSV file not found"

**Cause:** File path incorrect or file not uploaded

**Solution:**
```python
# Check available files
dbutils.fs.ls("dbfs:/Users/[email]/medallion_pipeline/data/")

# If not listed, upload files using:
# - Web UI upload, or
# - Databricks CLI (see Step 3 above)
```

---

### Issue: "Table already exists"

**Cause:** Table was created in previous run

**Solution:**
```python
# Drop existing table
spark.sql("DROP TABLE IF EXISTS bronze_customers")

# Then re-run the notebook
```

---

### Issue: "InferSchema failed"

**Cause:** CSV has encoding issues or malformed data

**Solution:**
```python
# Try with explicit schema
df = spark.read.option("header","true")\
    .option("encoding","UTF-8")\
    .csv(csv_path)
```

---

### Issue: "Cluster timeout"

**Cause:** Cluster took too long to start

**Solution:**
1. Check cluster status
2. If red: Click cluster name → Restart
3. Wait 5-10 minutes for restart
4. Re-run notebook

---

### Issue: "Permission denied"

**Cause:** Insufficient permissions in Databricks workspace

**Solution:**
1. Contact workspace admin
2. Request: "Can create notebooks, tables, clusters"
3. Request: "Can access data in workspace folder"

---

## 📊 EXPECTED EXECUTION TIMES

| Step | Operation | Time |
|------|-----------|------|
| 1 | Clone repo | 1 min |
| 2 | Generate data | 1 min |
| 3 | Set up workspace | 10 min |
| 4 | Create cluster | 5 min |
| 5 | Upload code | 10 min |
| 6 | Bronze layer | 2 min (3 notebooks) |
| 7 | Silver layer | 2 min |
| 8 | Gold layer | 1 min |
| 9 | Create workflow | 5 min |
| 10 | Create dashboard | 5 min |
| **Total** | **Full setup** | **~45 min** |

---

## ✅ NEXT STEPS

After setup:
1. Review `README_FINAL.md` for project overview
2. Check `TESTING_AND_VERIFICATION.md` for test procedures
3. Read `REFLECTION.md` for learnings
4. Explore dashboard visualizations
5. Run end-to-end pipeline test

---

**Last Updated:** August 30, 2026  
**Status:** ✅ Ready for Production Setup

