# Requirements Analysis: Databricks Medallion Architecture Data Pipeline

 
**Project Type:** AI-Assisted Data Engineering Exercise

---

## 1. Problem Statement

An e-commerce company ingests daily sales data from multiple sources into Databricks. The company needs a scalable, reliable data pipeline that:

- Ingests raw transactional data (customers, orders, products)
- Validates data quality at source (before analysis)
- Creates business-ready aggregations for analytics and reporting
- Surfaces insights through dashboards for stakeholders

**Current State:**
- Data exists in CSV format in S3/DBFS
- No quality validation currently exists
- No standardized transformation or aggregation process
- Business users have no self-service analytics capability

**Desired State:**
- Raw data ingested and landed in Bronze layer (append-only)
- Data quality validated in Silver layer (flagged, not deleted)
- Business aggregations available in Gold layer (ready for BI)
- Dashboard visualizations for decision-making

---

## 2. Functional Requirements

### 2.1 Data Ingestion (Bronze Layer)

| Requirement | Details |
|------------|---------|
| **Source Data** | 3 CSV files: customers.csv, orders.csv, products.csv |
| **Ingest Method** | Batch load from S3/DBFS into Databricks |
| **Schema Handling** | Auto-infer schema from CSV headers; apply explicit types where needed |
| **Data Volume** | customers: 10K rows, orders: 100K rows, products: 500 rows |
| **Raw vs Clean** | Store raw data unchanged (no transformations) |
| **Metadata** | Log ingestion timestamp, row counts, source file info |
| **Idempotency** | Each run should be repeatable (upsert, not append duplicates) |

### 2.2 Data Quality Validation (Silver Layer)

| Check | What | Acceptable Threshold | Action |
|-------|------|---------------------|--------|
| **Completeness** | No NULLs in critical fields: email, customer_id, product_id | >99% complete | Flag rows with NULLs; calculate % complete |
| **Uniqueness** | No duplicate rows (same order_id, customer_id) | 100% unique | Flag duplicates; count duplicates |
| **Referential Integrity** | Foreign keys exist in parent tables (customer_id in customers, product_id in products) | >99.9% valid | Flag orphan records; count invalid refs |
| **Type Validation** | Data types match schema (INT, STRING, DATE, DECIMAL) | 100% correct | Flag type mismatches; identify bad values |

**Quality Check Output:**
- Add `quality_check_result` column to each table (PASS/FAIL/ERROR)
- Do NOT delete bad rows — flag them for investigation
- Generate quality report: % passed per check

### 2.3 Data Aggregation (Gold Layer)

Create three business-ready aggregation tables:

#### **Aggregation A: Sales by Product**
| Field | Logic |
|-------|-------|
| product_id | From orders |
| product_name | From products |
| category | From products |
| total_orders | COUNT(order_id) |
| total_revenue | SUM(total_amount) |
| avg_order_value | AVG(total_amount) |

**Filter:** Only PASSED quality checks

#### **Aggregation B: Revenue by Customer**
| Field | Logic |
|-------|-------|
| customer_id | From orders |
| customer_name | From customers |
| customer_segment | From customers (Premium/Standard/Basic) |
| total_orders | COUNT(order_id) |
| total_revenue | SUM(total_amount) |
| avg_order_value | AVG(total_amount) |
| lifetime_value_actual | CALCULATED SUM(total_amount) |

**Filter:** Only PASSED quality checks  
**Validation:** Compare lifetime_value_actual vs stored lifetime_value

#### **Aggregation C: Customer Segmentation**
| Segment Type | Definition | Logic |
|--------------|-----------|-------|
| High-Value | Revenue in top 25% | revenue >= 75th percentile |
| Repeat | 5+ orders | COUNT(order_id) >= 5 |
| One-Time | Exactly 1 order | COUNT(order_id) = 1 |
| Inactive | No orders in last 90 days | MAX(order_date) < NOW() - 90 days |

**Output:**
- segment_type
- customer_count
- avg_revenue
- total_revenue

### 2.4 Business Intelligence Dashboard

| Visualization | Purpose | Data Source |
|--------------|---------|-------------|
| **Top 10 Products by Revenue** | Identify best-selling products | gold_sales_by_product (sorted by total_revenue DESC, limit 10) |
| **Customer Revenue Distribution** | Understand revenue concentration (histogram) | gold_revenue_by_customer (histogram of total_revenue) |
| **Customer Segmentation Breakdown** | See segment distribution (pie chart) | gold_customer_segmentation (pie of customer_count by segment_type) |

**Minimum 3+ queries** (can add more)  
**Interactivity:** Enable filters (date range, segment, category) if applicable

---

## 3. Non-Functional Requirements

| Requirement | Target |
|------------|--------|
| **Scalability** | Support up to 100x growth in data volume (1B orders) without redesign |
| **Reliability** | Pipeline must handle and report on data quality issues; no silent failures |
| **Maintainability** | Code must be readable, commented, and reusable |
| **Traceability** | Every row flagged in Silver layer must be traceable to source |
| **Performance** | End-to-end pipeline (Bronze → Silver → Gold) completes in <5 minutes |
| **Documentation** | Every script must have clear purpose, inputs, outputs |
| **Testing** | Data quality checks must be validated to catch intentional issues |
| **Reusability** | Code should be modular; easy to add new sources or quality checks |

---

## 4. Data Schema & Structure

### 4.1 Source Data (Bronze Input)

**customers.csv (10,000 rows)**
```
customer_id (INT, PK)
customer_name (STRING)
email (STRING)
country (STRING)
signup_date (DATE, range: 2020-2024)
customer_segment (STRING: Premium/Standard/Basic)
lifetime_value (DECIMAL)
```

**orders.csv (100,000 rows)**
```
order_id (INT, PK)
customer_id (INT, FK → customers.customer_id)
order_date (DATE)
product_id (INT, FK → products.product_id)
quantity (INT)
unit_price (DECIMAL)
total_amount (DECIMAL)
order_status (STRING: Pending/Completed/Cancelled)
payment_date (DATE, nullable)
```

**products.csv (500 rows)**
```
product_id (INT, PK)
product_name (STRING)
category (STRING)
price (DECIMAL)
cost (DECIMAL)
stock_quantity (INT)
reorder_level (INT)
```

### 4.2 Data Quality Issues (Intentional)

| Issue | Table | Count | Type | How to Detect |
|-------|-------|-------|------|--------------|
| NULL email | customers | 50 rows | Completeness | email IS NULL |
| Duplicate customer_id | customers | 10 rows | Uniqueness | Count(*) Group By customer_id HAVING Count > 1 |
| NULL customer_id | orders | 100 rows | Completeness | customer_id IS NULL |
| NULL product_id | orders | 200 rows | Completeness | product_id IS NULL |
| customer_id not in customers | orders | 50 rows | Referential Integrity | LEFT JOIN to customers, found NULLs |
| product_id not in products | orders | 30 rows | Referential Integrity | LEFT JOIN to products, found NULLs |
| Duplicate order_id | orders | 20 rows | Uniqueness | Count(*) Group By order_id HAVING Count > 1 |
| **TOTAL** | **~** | **~700 rows** | **0.7% error rate** | **All detectable** |

---

## 5. Assumptions

### 5.1 Technical Assumptions

- **Databricks Environment:** Community Edition or cloud workspace available
- **Data Location:** CSVs can be loaded into S3/DBFS for testing
- **Languages:** Python, PySpark, and SQL available
- **Libraries:** PySpark, Delta Lake, pandas available
- **Version Control:** Git available for repository management
- **AI Tool:** Cursor, Claude, or approved AI assistant available for coding help

### 5.2 Business Assumptions

- **Data Ownership:** Quality issues are expected; goal is to detect and flag them
- **No Deletion:** Bad rows are flagged, not deleted (regulatory/audit trail)
- **Single Snapshot:** Pipeline creates a daily snapshot (not streaming; batch is sufficient)
- **Historical Data:** No need for slowly-changing dimensions; assume current state only
- **Availability:** 24-hour window for data to be available in Gold/Dashboard

### 5.3 Data Assumptions

- **No PII Restrictions:** Can generate sample data with realistic names/emails (fake data)
- **Foreign Keys:** Orders may have orphan records (intentional); must be detected
- **Duplicates:** Some rows may be duplicates; should be flagged, not deduplicated silently
- **Date Consistency:** Assume order_date <= payment_date; if violated, can flag
- **Amounts:** Assume total_amount = quantity × unit_price; validation possible
- **Updates:** Assume append-only; no updates to past data

---

## 6. Edge Cases & Exception Handling

| Edge Case | Scenario | Handling |
|-----------|----------|----------|
| **Empty File** | Customer CSV has 0 rows | Log warning; create empty table; continue |
| **Schema Mismatch** | CSV column missing from header | Fail fast with error; report column name |
| **Type Coercion Failure** | String "abc" in INT field | Flag row in type validation; log value |
| **Very Large Orders** | total_amount > 999,999 (outlier) | Accept as valid; flag in aggregation if needed |
| **Duplicate Entire Row** | Identical values across all columns | Detect via uniqueness check; flag |
| **No Valid Rows** | All orders fail quality checks | Log error; create empty Gold tables (0 rows) |
| **Missing Aggregation Dimension** | A product has no orders (orphan) | Include in aggregations with COUNT=0 |
| **Future Dates** | signup_date or order_date in future | Flag in validation; accept as data error |
| **Null vs Empty String** | email is NULL vs "" (empty) | Treat both as incomplete; flag |

---

## 7. Acceptance Criteria

For this project to be considered **COMPLETE**, ALL of the following must be met:

### 7.1 Code & Functionality
- ✅ Sample data generator script creates 3 CSVs with exact quality issues
- ✅ Bronze layer ingests all 3 sources successfully into Delta tables
- ✅ Silver layer implements all 4 quality checks (completeness, uniqueness, referential integrity, type validation)
- ✅ Quality report displays % passed for each check
- ✅ Gold layer creates all 3 aggregation tables with correct calculations
- ✅ Spot-check: 2-3 aggregation calculations verified manually
- ✅ Dashboard displays all 3+ visualizations correctly
- ✅ All code is readable, commented, and documented

### 7.2 Documentation & Artifacts
- ✅ README.md with step-by-step setup instructions (verified working)
- ✅ All design documents complete (requirements, design, data model, quality strategy)
- ✅ Full AI prompt history documented by phase (data-generation, bronze, silver, gold, dashboard)
- ✅ Each prompt includes: what you sent, AI's response, what you accepted/changed/rejected
- ✅ Debugging notes documented (issues encountered, how resolved)
- ✅ Reflection document (what worked, what didn't, lessons learned)

### 7.3 Testing & Validation
- ✅ Data quality tests pass (verify checks catch the ~700 intentional issues)
- ✅ Aggregation calculations verified (spot-check sums/counts/averages)
- ✅ End-to-end pipeline test passes (delete all → regenerate → verify all outputs)
- ✅ README setup instructions tested and working

### 7.4 Repository Structure
- ✅ Git repository with all files in correct folders (matching template)
- ✅ All CSVs present in data/ folder
- ✅ All scripts in src/ subfolders (data_generation, bronze, silver, gold, dashboard)
- ✅ All markdown documents in root and subdirectories
- ✅ All AI prompts documented in ai-prompts/ folder

---

## 8. Success Metrics

| Metric | Target | How to Verify |
|--------|--------|---------------|
| **Data Quality Detection Rate** | Catch ~700 intentional issues (70% at minimum) | Run quality checks; count flagged rows |
| **Gold Aggregation Accuracy** | All calculations correct | Spot-check 3+ records manually vs source |
| **Dashboard Functionality** | All 3+ visualizations display | Screenshot/test each tile |
| **Documentation Completeness** | All required documents present | Checklist against template |
| **AI Usage Evidence** | Full prompt history for all phases | ai-prompts/ folder with all interactions |
| **Code Quality** | All code readable and commented | Peer review or self-review |
| **Reusability** | Code can be extended (e.g., add 4th quality check) | Assess modularity and naming |

---

## 9. Out of Scope

The following are **NOT required** for this exercise:

- ❌ Streaming data pipeline (batch is sufficient)
- ❌ Real-time dashboard updates (hourly refresh is fine)
- ❌ Handling of sensitive PII (using fake data is acceptable)
- ❌ Performance optimization (5-minute runtime is acceptable)
- ❌ Multi-table transactions or ACID compliance (Delta handles this)
- ❌ Complex slowly-changing dimensions or temporal data
- ❌ Machine learning models or advanced analytics
- ❌ Cloud infrastructure setup (use Databricks Community Edition)

---

## 10. Next Steps

1. **Design Phase** → Create design-notes.md (architecture, layer design, testing approach)
2. **Strategy Phase** → Create data-quality-strategy.md (detailed quality check logic)
3. **Tool Workflow** → Create tool-workflow.md (how you'll use AI across the lifecycle)
4. **Development** → Start Phase 2 with sample data generation

---

## 11. Questions & Clarifications Needed

**None at this stage** — requirements are clear and comprehensive.

**If clarifications arise during development:**
- Document assumptions made
- Record questions asked to AI tool (Cursor/Claude)
- Update this document as needed

