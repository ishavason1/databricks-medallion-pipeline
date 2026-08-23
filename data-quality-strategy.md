# Data Quality Strategy

---

## 1. Quality Overview

**Goal:** Detect and flag ALL ~700 intentional data quality issues without deleting any rows

**Philosophy:** Quality checks are about transparency, not correction. Flag problematic rows for investigation; preserve data for audit trail.

**Detection Rate Target:** 100% (catch all 700 issues)

---

## 2. Four Quality Checks

### 2.1 Check 1: Completeness

**What:** Critical fields must not be NULL

**Fields to Check:**
- customers.email: 50 NULLs expected
- orders.customer_id: 100 NULLs expected
- orders.product_id: 200 NULLs expected

**Threshold:** >99% complete

**Expected Failures:** 50 + 100 + 200 = 350 rows

---

### 2.2 Check 2: Uniqueness

**What:** Primary keys must be unique

**Keys to Check:**
- customers.customer_id: 10 duplicates expected
- orders.order_id: 20 duplicates expected

**Threshold:** 100% unique (zero tolerance)

**Expected Failures:** 10 + 20 = 30 rows

---

### 2.3 Check 3: Referential Integrity

**What:** Foreign keys must exist in parent tables

**Keys to Check:**
- orders.customer_id → customers.customer_id: 50 orphans expected
- orders.product_id → products.product_id: 30 orphans expected

**Threshold:** >99.9% valid

**Expected Failures:** 50 + 30 = 80 rows

---

### 2.4 Check 4: Type Validation

**What:** Data types must match schema

**Threshold:** 100% type-valid

**Expected Failures:** 0 rows (Delta enforces schema)

---

## 3. Quality Check Implementation

**SQL Pattern for Completeness:**
```sql
SELECT *,
  CASE 
    WHEN email IS NULL THEN 'FAIL_NULL_EMAIL'
    WHEN customer_id IS NULL THEN 'FAIL_NULL_CUSTOMER_ID'
    WHEN product_id IS NULL THEN 'FAIL_NULL_PRODUCT_ID'
    ELSE 'PASS'
  END AS quality_check_result
FROM bronze_table
```

**SQL Pattern for Uniqueness:**
```sql
SELECT *,
  CASE 
    WHEN ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY customer_id) > 1 
      THEN 'FAIL_DUPLICATE'
    ELSE 'PASS'
  END AS quality_check_result
FROM bronze_table
```

**SQL Pattern for Referential Integrity:**
```sql
SELECT o.*,
  CASE 
    WHEN c.customer_id IS NULL AND o.customer_id IS NOT NULL 
      THEN 'FAIL_INVALID_FK'
    ELSE 'PASS'
  END AS quality_check_result
FROM bronze_orders o
LEFT JOIN bronze_customers c ON o.customer_id = c.customer_id
```

---

## 4. Quality Report Output

**Expected Summary:**

```
TABLE: customers (10,000 rows)
  Completeness:  9,950 / 10,000 (99.5%)
  Uniqueness:    9,990 / 10,000 (99.9%)
  Referential:   10,000 / 10,000 (100%)
  Type Valid:    10,000 / 10,000 (100%)

TABLE: orders (100,000 rows)
  Completeness:  99,500 / 100,000 (99.5%)
  Uniqueness:    99,980 / 100,000 (99.98%)
  Referential:   99,920 / 100,000 (99.92%)
  Type Valid:    100,000 / 100,000 (100%)

TOTAL ISSUES DETECTED: ~700 rows (0.63%)
STATUS: ✓ All intentional issues detected
```

---

## 5. Sample Data Quality Issues Breakdown

| Issue Type | Table | Count | Detection Method |
|-----------|-------|-------|-----------------|
| NULL email | customers | 50 | Completeness |
| NULL customer_id | orders | 100 | Completeness |
| NULL product_id | orders | 200 | Completeness |
| Duplicate customer_id | customers | 10 | Uniqueness |
| Duplicate order_id | orders | 20 | Uniqueness |
| Invalid customer FK | orders | 50 | Referential Integrity |
| Invalid product FK | orders | 30 | Referential Integrity |
| **TOTAL** | | **~700** | |

---

## 6. Gold Layer Quality Filtering

**Always filter to PASS rows when creating aggregations:**

```sql
-- Correct: Filter to PASS only
SELECT ... FROM silver_orders 
WHERE quality_check_result = 'PASS'

-- Incorrect: Include FAIL rows
SELECT ... FROM silver_orders  -- Includes FAIL rows - bad!
```

