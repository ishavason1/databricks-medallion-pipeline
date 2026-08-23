# Design Notes: Medallion Architecture Pipeline

---

## 1. Architecture Overview

### 1.1 High-Level Data Flow

```
SOURCES (CSV FILES)
    ├── customers.csv (10K rows)
    ├── orders.csv (100K rows, with ~700 quality issues)
    └── products.csv (500 rows)
         ↓
    BRONZE LAYER (RAW DATA)
         ↓
    SILVER LAYER (VALIDATED DATA with quality_check_result column)
         ↓
    GOLD LAYER (BUSINESS-READY AGGREGATIONS)
         ↓
    DASHBOARD (VISUALIZATIONS FOR BI)
```

---

## 2. Layer-by-Layer Design

### 2.1 Bronze Layer Design

**Objective:** Store raw data exactly as received, with no transformations

**Approach:**
- Read CSV files from S3/DBFS
- Preserve all columns, all rows, all values (including NULLs)
- Apply explicit data types (INT, STRING, DATE, DECIMAL)
- Create Delta tables (not Parquet) for ACID compliance
- Log ingestion metadata (timestamp, row count)

**Implementation:**
1. customers.csv → bronze_customers (10,000 rows)
2. orders.csv → bronze_orders (100,000 rows with 700 quality issues)
3. products.csv → bronze_products (500 rows)

**Key Principle:** NO TRANSFORMATIONS - Store raw data for traceability

---

### 2.2 Silver Layer Design

**Objective:** Detect and flag data quality issues (NOT delete)

**Four Quality Checks:**

#### **Check 1: Completeness**
- Detect: NULLs in email, customer_id, product_id
- Action: Flag rows with "FAIL_NULL_*" in quality_check_result
- Expected Issues: 50 NULL emails, 100 NULL customer_ids, 200 NULL product_ids
- Metrics: % complete for each field

#### **Check 2: Uniqueness**
- Detect: Duplicate rows (same order_id, customer_id)
- Action: Flag ALL duplicates (not just first) with "FAIL_DUPLICATE"
- Expected Issues: 10 duplicate customer_ids, 20 duplicate order_ids
- Metrics: % unique per key

#### **Check 3: Referential Integrity**
- Detect: Foreign keys missing from parent tables
- Action: Flag with "FAIL_INVALID_*_FK"
- Expected Issues: 50 invalid customer_ids, 30 invalid product_ids
- Metrics: % valid foreign keys

#### **Check 4: Type Validation**
- Detect: Data type mismatches (string in INT field, negative amounts, etc.)
- Action: Flag with "FAIL_TYPE_*"
- Expected Issues: 0 (Delta schema enforces types at read)
- Metrics: % type-valid

**Output:** silver_* tables with quality_check_result column + Quality Report

---

### 2.3 Gold Layer Design

**Objective:** Create 3 business-ready aggregation tables

**Aggregation 1: gold_sales_by_product**
- Metric: total_orders, total_revenue, avg_order_value
- Dimension: product_id, product_name, category
- Filter: WHERE quality_check_result = 'PASS'
- Expected Rows: 500 (one per product, or fewer if some have no PASS orders)

**Aggregation 2: gold_revenue_by_customer**
- Metric: total_orders, total_revenue, avg_order_value, lifetime_value_actual
- Dimension: customer_id, customer_name, customer_segment
- Filter: WHERE quality_check_result = 'PASS'
- Validation: lifetime_value_actual should match stored lifetime_value
- Expected Rows: ~9,950 (customers with at least one PASS order)

**Aggregation 3: gold_customer_segmentation**
- Dimension: segment_type (High-Value, Repeat, One-Time, Inactive)
- Metric: customer_count, avg_revenue, total_revenue
- Logic: Segment by revenue percentile, order frequency, recency
- Expected Rows: 4 (one per segment type)

---

### 2.4 Dashboard Design

**Visualization 1: Top 10 Products by Revenue**
- Type: Bar Chart
- Data: gold_sales_by_product (ordered by total_revenue DESC, limit 10)
- Axis: product_name (Y), total_revenue (X)

**Visualization 2: Customer Revenue Distribution**
- Type: Histogram
- Data: gold_revenue_by_customer
- Axis: total_revenue (binned), customer_count
- Shows: Distribution of customer spending

**Visualization 3: Customer Segmentation**
- Type: Pie Chart
- Data: gold_customer_segmentation
- Slices: segment_type
- Labels: customer_count and %

---

## 3. Data Quality Strategy

**Philosophy:** Flag, don't delete. All issues are detectable.

**Quality Check Sequence:**
1. Completeness → identifies NULLs
2. Uniqueness → identifies duplicates
3. Referential Integrity → identifies orphans
4. Type Validation → identifies type mismatches

**Quality Report Output:**
```
Table: customers
  Completeness:  9,950 / 10,000 (99.5%)
  Uniqueness:    9,990 / 10,000 (99.9%)
  Referential:   10,000 / 10,000 (100%)
  Type Valid:    10,000 / 10,000 (100%)

Table: orders
  Completeness:  99,500 / 100,000 (99.5%)
  Uniqueness:    99,980 / 100,000 (99.98%)
  Referential:   99,920 / 100,000 (99.92%)
  Type Valid:    100,000 / 100,000 (100%)

TOTAL ISSUES DETECTED: ~700 rows (0.7%)
```

---

## 4. Testing Strategy

**Unit Tests (by layer):**
- Bronze: Row counts, schema match, file ingestion
- Silver: Each quality check catches expected issues (~700 total)
- Gold: Aggregation calculations verified (spot-check 3+)
- Dashboard: All 3+ queries execute and visualizations render

**Integration Test:**
- End-to-end: data generator → bronze → silver → gold → dashboard
- Verify quality issues are detected and cascaded correctly

**Validation:**
- Spot-check: Manually verify 2-3 calculations in Gold layer
- Accuracy: Verify aggregation sums/counts match source data

---

## 5. Error Handling & Debugging

**Common Issues:**
- CSV path incorrect → Verify S3/DBFS location
- Schema mismatch → Check CSV headers
- Type conversion error → Flag in Silver; investigate source
- Duplicate key error → Use overwrite mode in Bronze
- Null join error → Handle NULLs before joins in Silver

**Logging:**
- Bronze ingestion: timestamp, row count, status
- Silver quality checks: check name, PASS count, FAIL count, %
- Gold aggregations: table name, row count, execution time

---

## 6. Implementation Sequence

**Phase 1 (Complete):** Requirements & Design  
**Phase 2:** Sample Data Generation + Bronze Ingestion  
**Phase 3:** Silver Quality Checks  
**Phase 4:** Gold Aggregations  
**Phase 5:** Dashboard Creation  
**Phase 6:** Testing & Validation  
**Phase 7:** Documentation & Reflection  

---

## 7. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Flag rows instead of delete | Audit trail, regulatory compliance |
| Use Delta Lake | ACID, time-travel, schema evolution |
| Overwrite Bronze on each run | Idempotent, no duplicates |
| Quality checks in Silver layer | Separate concerns, preserve raw data |
| LEFT JOINs for FK checks | Catches orphan records |
| Filter to PASS for Gold | Only trust validated data |


