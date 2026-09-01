# AI Prompts — Phase 3: Bronze Layer Ingestion

---

## Prompt 1: Bronze Layer Architecture

**PROMPT SENT (USER):**
```
"Now help me in phase 3 of our project, we already completed phase 1(initialization, 
requirement gathering etc) and phase2 for generating the same data. 

Now I need to create the Bronze layer - just raw data ingestion with no transformations.
Can you create 4 Python scripts for me:

1. 01_ingest_customers.py - reads customers.csv and loads it to a Delta table called bronze_customers
2. 02_ingest_orders.py - reads orders.csv and loads it to bronze_orders
3. 03_ingest_products.py - reads products.csv and loads it to bronze_products
4. ingest_all.py - a master script that calls all 3 in sequence

Requirements:
* Use PySpark and Delta Lake
* Keep data exactly as-is (no transformations, no cleaning)
* Overwrite tables each time (idempotent)
* Log when data was ingested (timestamp) and how many rows
* Include basic error handling
* Add print statements so I can see what's happening
* Validate row counts match expected (10000, 100000, 500)

The CSV files are in data/ folder. The schemas match the column names in the CSVs exactly.
Make the code clear with comments. Each script should work independently, and ingest_all.py 
should call them in sequence."
```

**AI RESPONSE SUMMARY:**
- Generated 3 individual ingestion notebooks (PySpark)
- Created ingest_all.py using dbutils.notebook.run()
- Each notebook:
  - Reads CSV with inferSchema
  - Writes to Delta table with mode="overwrite"
  - Logs timestamp and row counts
  - Includes error handling with try-except
  - Validates expected row counts
  - Has print statements for visibility

**YOUR EVALUATION:**
✓ **What was good:**
- Clean, readable code
- Proper error handling
- Row count validation
- Logging implementation
- Clear comments

✗ **What needed fixing:**
- ingest_all.py used dbutils.notebook.run()
- Path resolution issues in Databricks
- notebook.run() not reliable for orchestration

**What you changed:**
- Kept 3 individual ingestion scripts
- Replaced ingest_all.py with Databricks Workflow approach
- Use native Databricks job scheduling instead of custom orchestration
- Why: Databricks Workflows more reliable, better monitoring, native feature

---

## Prompt 2: Alternative to notebook.run()

**PROMPT SENT (USER):**
```
"The ingest_all.py approach with dbutils.notebook.run() is giving me path resolution errors.
What's the best way to orchestrate these 3 ingestion notebooks in Databricks?
Should I create them as separate notebooks and call them from a Workflow instead?"
```

**AI RESPONSE SUMMARY:**
- Recommended Databricks Workflows (native feature)
- Benefits:
  - No path resolution issues
  - Built-in retry logic
  - Native job scheduling
  - Better monitoring/logging
  - Easier to debug
- Workflow structure:
  - Task 1: 01_ingest_customers (no dependencies)
  - Task 2: 02_ingest_orders (no dependencies)
  - Task 3: 03_ingest_products (no dependencies)
  - Can run in parallel or sequence
- Why NOT custom scripts:
  - Error-prone path resolution
  - No built-in scheduling
  - Hard to monitor
  - Not idiomatic Databricks

**YOUR EVALUATION:**
✓ **ACCEPTED** - Much better approach

**Decision:**
- Kept 3 individual notebooks for Databricks
- Skip ingest_all.py entirely
- Use native Databricks Workflows for orchestration
- Why: Matches Databricks best practices, more reliable

---

## Prompt 3: Schema Definition

**PROMPT SENT (USER):**
```
"Create a schema.sql file that defines all 9 tables:
- 3 Bronze tables (no transformations, raw schema)
- 3 Silver tables (bronze schema + quality_check_result column)
- 3 Gold tables (aggregated/final schema)

Include:
- Column definitions with types
- Primary keys
- Foreign keys (informational, not enforced in Delta)
- Indexes for Gold layer tables
- Views for common queries"
```

**AI RESPONSE SUMMARY:**
- Generated comprehensive schema.sql
- Bronze layer: 3 tables with raw column definitions
- Silver layer: Same as bronze + quality_check_result STRING
- Gold layer: Aggregated schemas (different columns)
- Added primary key constraints (informational)
- Added foreign key constraints (informational)
- Created indexes for performance (Gold layer)
- Created 4 useful views:
  - Quality check summary
  - Quality issues breakdown
  - Top 10 products
  - Customer segments

**YOUR EVALUATION:**
✓ **ACCEPTED** - Comprehensive and complete

**File:** `database/schema.sql`

---

## Summary: Bronze Layer Phase

**Total Prompts:** 3  
**Iterations:** 1 (ingest_all.py → Databricks Workflows)  
**Rejections:** 0  

**Final Deliverables:**
- ✅ 01_ingest_customers.py
- ✅ 02_ingest_orders.py
- ✅ 03_ingest_products.py
- ✅ schema.sql
- ✅ Documentation

**Key Decisions:**
- ✓ Accepted: PySpark + Delta Lake
- ✓ Accepted: Idempotent loading (mode="overwrite")
- ✓ Accepted: Databricks Workflows for orchestration
- ✗ Rejected: Custom ingest_all.py with notebook.run()

**Data Ingested:**
- ✅ bronze_customers: 10,000 rows
- ✅ bronze_orders: 100,000 rows
- ✅ bronze_products: 500 rows
- ✅ Total: 110,500 rows

**Status:** ✅ Phase 3 Complete

