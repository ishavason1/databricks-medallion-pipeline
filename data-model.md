# Data Model - Databricks Medallion Architecture

**eCommerce Sales Pipeline Data Model**

---

## 📋 OVERVIEW

Complete data model documentation for the three-layer Medallion Architecture:
- **Bronze Layer:** Raw data (no transformations)
- **Silver Layer:** Validated data (quality checks)
- **Gold Layer:** Aggregated data (business-ready)

---

## 🏗️ DATA MODEL ARCHITECTURE

```
CSV Files
  ├── customers.csv (10,000 rows)
  ├── orders.csv (100,000 rows)
  └── products.csv (500 rows)
        ↓
BRONZE LAYER (Raw)
  ├── bronze_customers
  ├── bronze_orders
  └── bronze_products
        ↓
SILVER LAYER (Quality-Checked)
  ├── silver_customers (quality_check_result added)
  ├── silver_orders (quality_check_result added)
  └── silver_products (quality_check_result added)
        ↓ (Filter: WHERE quality_check_result = 'PASS')
GOLD LAYER (Aggregations)
  ├── gold_sales_by_product
  ├── gold_revenue_by_customer
  └── gold_customer_segmentation
```

---

## 📊 BRONZE LAYER SCHEMA

### Table: bronze_customers

**Source:** customers.csv (10,000 rows)

| Column | Data Type | Length | Nullable | Description |
|--------|-----------|--------|----------|-------------|
| customer_id | BIGINT | - | NO | Unique customer identifier (Primary Key) |
| customer_name | STRING | 255 | NO | Customer full name |
| email | STRING | 255 | YES | Customer email address |
| country | STRING | 100 | NO | Customer country |
| signup_date | DATE | - | NO | Date customer signed up (2020-2024) |
| customer_segment | STRING | 50 | NO | Customer segment (Premium/Standard/Basic) |
| lifetime_value | DECIMAL(12,2) | - | NO | Total lifetime value in USD |

**Intentional Quality Issues (50 rows):**
- 50 rows have NULL email
- 10 rows have duplicate customer_id

**Sample Data:**
```
customer_id | customer_name | email | country | signup_date | customer_segment | lifetime_value
1 | John Smith | john@example.com | USA | 2020-01-15 | Premium | 5000.00
2 | Jane Doe | NULL | Canada | 2021-06-20 | Standard | 2500.00
...
```

---

### Table: bronze_orders

**Source:** orders.csv (100,000 rows)

| Column | Data Type | Length | Nullable | Description |
|--------|-----------|--------|----------|-------------|
| order_id | BIGINT | - | NO | Unique order identifier (Primary Key) |
| customer_id | BIGINT | - | YES | Foreign Key to bronze_customers (100 NULLs) |
| order_date | DATE | - | NO | Date order was placed |
| product_id | BIGINT | - | YES | Foreign Key to bronze_products (200 NULLs) |
| quantity | INT | - | NO | Quantity ordered |
| unit_price | DECIMAL(10,2) | - | NO | Price per unit |
| total_amount | DECIMAL(12,2) | - | NO | Total order amount |
| order_status | STRING | 50 | NO | Status (Pending/Completed/Cancelled) |
| payment_date | DATE | - | YES | Date payment received (nullable) |

**Intentional Quality Issues (640 rows):**
- 100 rows have NULL customer_id
- 200 rows have NULL product_id
- 50 rows have invalid customer_id (FK orphans)
- 30 rows have invalid product_id (FK orphans)
- 20 rows have duplicate order_id
- 40 rows have NULL total_amount

**Sample Data:**
```
order_id | customer_id | order_date | product_id | quantity | unit_price | total_amount | order_status | payment_date
1001 | 1 | 2023-01-10 | 501 | 2 | 49.99 | 99.98 | Completed | 2023-01-10
1002 | NULL | 2023-01-11 | 502 | 1 | 29.99 | 29.99 | Pending | NULL
1003 | 2 | 2023-01-12 | NULL | 3 | 99.99 | 299.97 | Completed | 2023-01-12
...
```

---

### Table: bronze_products

**Source:** products.csv (500 rows)

| Column | Data Type | Length | Nullable | Description |
|--------|-----------|--------|----------|-------------|
| product_id | BIGINT | - | NO | Unique product identifier (Primary Key) |
| product_name | STRING | 255 | NO | Product name |
| category | STRING | 100 | NO | Product category |
| price | DECIMAL(10,2) | - | NO | Current selling price |
| cost | DECIMAL(10,2) | - | NO | Product cost |
| stock_quantity | INT | - | NO | Current stock level |
| reorder_level | INT | - | NO | Minimum stock before reorder |

**Intentional Quality Issues:**
- 0 (No issues - clean data)

**Sample Data:**
```
product_id | product_name | category | price | cost | stock_quantity | reorder_level
501 | Laptop | Electronics | 999.99 | 600.00 | 45 | 10
502 | Mouse | Electronics | 29.99 | 8.00 | 250 | 50
503 | Desk | Furniture | 299.99 | 150.00 | 12 | 3
...
```

---

## 🔍 SILVER LAYER SCHEMA

### All Silver Tables = Bronze + quality_check_result

Each silver table has ALL columns from corresponding bronze table PLUS:

| Column | Data Type | Description |
|--------|-----------|-------------|
| quality_check_result | STRING | Quality check result flag |

**Possible Values:**
- `PASS` - Row passed all quality checks
- `FAIL_NULL_<column_name>` - Column contains NULL in required field
- `FAIL_DUPLICATE` - Row has duplicate primary key
- `FAIL_INVALID_<fk_table>_FK` - Foreign key doesn't exist in referenced table
- `FAIL_TYPE_<column_name>` - Data type mismatch

### Table: silver_customers

**Schema:** bronze_customers + quality_check_result

**Quality Check Results (10,000 rows):**
- 9,940 rows: `PASS`
- 50 rows: `FAIL_NULL_email` (NULLs in email)
- 10 rows: `FAIL_DUPLICATE` (duplicate customer_id)

**Example:**
```
customer_id | customer_name | email | ... | quality_check_result
1 | John Smith | john@example.com | ... | PASS
2 | Jane Doe | NULL | ... | FAIL_NULL_email
100 | Bob Smith | bob@example.com | ... | FAIL_DUPLICATE (duplicate ID)
```

---

### Table: silver_orders

**Schema:** bronze_orders + quality_check_result

**Quality Check Results (100,000 rows):**
- 99,600 rows: `PASS` (clean data)
- 100 rows: `FAIL_NULL_customer_id`
- 200 rows: `FAIL_NULL_product_id`
- 50 rows: `FAIL_INVALID_customers_FK` (customer_id doesn't exist)
- 30 rows: `FAIL_INVALID_products_FK` (product_id doesn't exist)
- 20 rows: `FAIL_DUPLICATE` (duplicate order_id)

**Note:** Rows can have multiple FAIL flags in cumulative checks.

---

### Table: silver_products

**Schema:** bronze_products + quality_check_result

**Quality Check Results (500 rows):**
- 500 rows: `PASS` (all clean)

---

## ✨ GOLD LAYER SCHEMA

### Table: gold_sales_by_product

**Purpose:** Aggregated sales metrics by product

**Row Count:** 500 (one per product)

**Columns:**

| Column | Data Type | Description |
|--------|-----------|-------------|
| product_id | BIGINT | Unique product identifier |
| product_name | STRING | Product name |
| category | STRING | Product category |
| total_orders | BIGINT | Count of distinct orders for product |
| total_revenue | DECIMAL(14,2) | Total revenue from product (SUM) |
| avg_order_value | DECIMAL(12,2) | Average order value for product (AVG) |

**Data Source:** gold_sales_by_product is created by:
1. Reading silver_products (filtered: quality_check_result = 'PASS')
2. LEFT JOIN with silver_orders (filtered: quality_check_result = 'PASS')
3. GROUP BY product_id, product_name, category
4. SORT BY total_revenue DESC

**Sample Data:**
```
product_id | product_name | category | total_orders | total_revenue | avg_order_value
501 | Laptop | Electronics | 450 | 425,000.00 | 944.44
502 | Monitor | Electronics | 380 | 95,000.00 | 250.00
503 | Keyboard | Electronics | 600 | 18,000.00 | 30.00
...
```

**Indices:** Sorted by total_revenue (descending)

---

### Table: gold_revenue_by_customer

**Purpose:** Aggregated revenue metrics by customer

**Row Count:** 9,950 (clean customers only)

**Columns:**

| Column | Data Type | Description |
|--------|-----------|-------------|
| customer_id | BIGINT | Unique customer identifier |
| customer_name | STRING | Customer name |
| customer_segment | STRING | Premium/Standard/Basic |
| total_orders | BIGINT | Count of distinct orders by customer |
| total_revenue | DECIMAL(14,2) | Total revenue from customer |
| avg_order_value | DECIMAL(12,2) | Average order value per customer |
| lifetime_value_actual | DECIMAL(12,2) | Actual lifetime value from data |

**Data Source:** gold_revenue_by_customer is created by:
1. Reading silver_customers (filtered: quality_check_result = 'PASS')
2. LEFT JOIN with silver_orders (filtered: quality_check_result = 'PASS')
3. GROUP BY customer_id, customer_name, customer_segment, lifetime_value
4. SORT BY total_revenue DESC

**Sample Data:**
```
customer_id | customer_name | customer_segment | total_orders | total_revenue | avg_order_value | lifetime_value_actual
1 | John Smith | Premium | 25 | 15,000.00 | 600.00 | 15,000.00
5 | Alice Johnson | Premium | 18 | 12,500.00 | 694.44 | 12,500.00
10 | Bob Wilson | Standard | 8 | 3,200.00 | 400.00 | 3,200.00
...
```

**Indices:** Sorted by total_revenue (descending)

---

### Table: gold_customer_segmentation

**Purpose:** Customer segmentation by value & behavior

**Row Count:** 4 segments

**Columns:**

| Column | Data Type | Description |
|--------|-----------|-------------|
| segment_type | STRING | High-Value / Repeat / One-Time / Inactive |
| customer_count | BIGINT | Number of customers in segment |
| avg_revenue | DECIMAL(14,2) | Average revenue per customer in segment |
| total_revenue | DECIMAL(14,2) | Total revenue from segment |

**Segmentation Logic:**

| Segment | Criteria | Description |
|---------|----------|-------------|
| **High-Value** | revenue > 75th percentile | Top spenders |
| **Repeat** | order_count >= 5 AND NOT high-value | Regular customers |
| **One-Time** | order_count = 1 | Single purchase |
| **Inactive** | order_count = 0 | No orders |

**Data Source:** gold_customer_segmentation is created by:
1. Reading silver_customers (filtered: quality_check_result = 'PASS')
2. LEFT JOIN with silver_orders (filtered: quality_check_result = 'PASS')
3. GROUP BY customer_id to get: order_count, total_revenue
4. Calculate 75th percentile of revenue
5. Apply CASE WHEN logic for segmentation
6. GROUP BY segment_type
7. SORT BY total_revenue DESC

**Sample Data:**
```
segment_type | customer_count | avg_revenue | total_revenue
High-Value | 2,487 | 7,411.11 | 18,432,000.00
Repeat | 3,245 | 2,750.00 | 8,920,750.00
One-Time | 4,218 | 508.33 | 2,145,000.00
Inactive | 0 | 0.00 | 0.00
```

**Indices:** Sorted by total_revenue (descending)

---

## 🔑 PRIMARY KEYS & FOREIGN KEYS

### Primary Keys

| Table | Primary Key | Type |
|-------|-------------|------|
| bronze_customers | customer_id | BIGINT |
| bronze_orders | order_id | BIGINT |
| bronze_products | product_id | BIGINT |
| silver_customers | customer_id | BIGINT |
| silver_orders | order_id | BIGINT |
| silver_products | product_id | BIGINT |
| gold_sales_by_product | product_id | BIGINT |
| gold_revenue_by_customer | customer_id | BIGINT |
| gold_customer_segmentation | segment_type | STRING |

### Foreign Keys

| Table | Foreign Key | References | Type |
|-------|------------|-----------|------|
| bronze_orders | customer_id | bronze_customers.customer_id | BIGINT |
| bronze_orders | product_id | bronze_products.product_id | BIGINT |
| silver_orders | customer_id | silver_customers.customer_id | BIGINT |
| silver_orders | product_id | silver_products.product_id | BIGINT |

**Note:** Foreign key violations are detected in Silver layer and flagged in quality_check_result.

---

## 📈 DATA FLOW & RELATIONSHIPS

### Bronze to Silver

```
bronze_customers → silver_customers
├── Completeness check (customer_id, customer_name, email required)
├── Uniqueness check (customer_id must be unique)
└── Type validation (all types correct)
    → Result: quality_check_result column added

bronze_orders → silver_orders
├── Completeness check (order_id, order_date required)
├── Uniqueness check (order_id must be unique)
├── Referential integrity (customer_id must exist in customers)
├── Referential integrity (product_id must exist in products)
└── Type validation
    → Result: quality_check_result column added

bronze_products → silver_products
├── Completeness check (all columns required)
├── Uniqueness check (product_id must be unique)
└── Type validation
    → Result: quality_check_result column added
```

### Silver to Gold (Filter: WHERE quality_check_result = 'PASS')

```
silver_products (PASS) → gold_sales_by_product
├── LEFT JOIN silver_orders (PASS)
├── GROUP BY product_id, product_name, category
└── Aggregate: COUNT, SUM, AVG

silver_customers (PASS) → gold_revenue_by_customer
├── LEFT JOIN silver_orders (PASS)
├── GROUP BY customer_id, customer_name, customer_segment, lifetime_value
└── Aggregate: COUNT, SUM, AVG

silver_customers (PASS) → gold_customer_segmentation
├── LEFT JOIN silver_orders (PASS)
├── GROUP BY customer_id (get order_count, total_revenue)
├── Calculate 75th percentile
├── Apply segmentation logic (CASE WHEN)
└── GROUP BY segment_type
```

---

## 🎯 QUALITY CHECKS APPLIED

### Completeness Check (NULL Detection)

**Customers Required Fields:** customer_id, customer_name, email  
**Orders Required Fields:** order_id, order_date  
**Products Required Fields:** product_id, product_name

**Flag:** `FAIL_NULL_<column_name>`

**Examples:**
- Row has NULL email → `FAIL_NULL_email`
- Row has NULL product_id → `FAIL_NULL_product_id`

---

### Uniqueness Check (Duplicate Detection)

**Customers:** customer_id must be unique  
**Orders:** order_id must be unique  
**Products:** product_id must be unique

**Flag:** `FAIL_DUPLICATE`

**Examples:**
- customer_id appears twice → Both rows: `FAIL_DUPLICATE`
- order_id appears twice → Both rows: `FAIL_DUPLICATE`

---

### Referential Integrity Check (FK Validation)

**Orders.customer_id must exist in Customers.customer_id**  
**Orders.product_id must exist in Products.product_id**

**Method:** LEFT JOIN, check if reference is NULL

**Flag:** `FAIL_INVALID_<fk_table>_FK`

**Examples:**
- customer_id = 999 (doesn't exist) → `FAIL_INVALID_customers_FK`
- product_id = 888 (doesn't exist) → `FAIL_INVALID_products_FK`

---

### Type Validation Check

**Verify data types match schema**

**Flag:** `FAIL_TYPE_<column_name>`

**Examples:**
- order_id contains non-numeric → `FAIL_TYPE_order_id`
- order_date in wrong format → `FAIL_TYPE_order_date`

---

## 📊 DATA STATISTICS

### Volume

| Table | Rows | Description |
|-------|------|-------------|
| customers.csv | 10,000 | Source file |
| orders.csv | 100,000 | Source file |
| products.csv | 500 | Source file |
| **Total Bronze** | **110,500** | Raw data ingested |
| **Total Silver (PASS)** | **110,040** | Clean data after checks |
| **Total Silver (FAIL)** | **460** | Flagged issues |

### Quality Distribution

| Layer | PASS | FAIL | Notes |
|-------|------|------|-------|
| silver_customers | 9,940 | 60 | 50 NULLs + 10 duplicates |
| silver_orders | 99,600 | 400 | 300 NULLs + 100 duplicates/FK issues |
| silver_products | 500 | 0 | All clean |

### Gold Layer Row Counts

| Table | Rows | Basis |
|-------|------|-------|
| gold_sales_by_product | 500 | One per product |
| gold_revenue_by_customer | 9,950 | Clean customers only |
| gold_customer_segmentation | 4 | One per segment type |

---

## 🔐 CONSTRAINTS & RULES

### Data Type Constraints

- **IDs (customer_id, order_id, product_id):** BIGINT, non-null, unique
- **Amounts (price, revenue, cost):** DECIMAL(12,2), non-null, >= 0
- **Dates (order_date, signup_date):** DATE, non-null, reasonable range (2020-2024)
- **Names & categories:** STRING, non-null, 50-255 chars
- **Counts:** INT/BIGINT, non-null, >= 0

### Business Rules

- **Customer segments:** Must be one of: Premium, Standard, Basic
- **Order status:** Must be one of: Pending, Completed, Cancelled
- **Revenue:** total_amount = quantity × unit_price
- **Stock:** stock_quantity >= 0, reorder_level > 0
- **Lifetime value:** Non-negative decimal

---

## 📝 EXAMPLE QUERIES

### Query 1: Top 10 Products by Revenue
```sql
SELECT 
    product_name,
    total_revenue,
    total_orders,
    avg_order_value
FROM gold_sales_by_product
ORDER BY total_revenue DESC
LIMIT 10;
```

### Query 2: Customer Revenue Distribution
```sql
SELECT 
    total_revenue,
    COUNT(*) as customer_count
FROM gold_revenue_by_customer
WHERE total_revenue > 0
GROUP BY total_revenue
ORDER BY total_revenue;
```

### Query 3: Segmentation Breakdown
```sql
SELECT 
    segment_type,
    customer_count,
    avg_revenue,
    total_revenue
FROM gold_customer_segmentation
ORDER BY total_revenue DESC;
```

### Query 4: Quality Issues by Type
```sql
SELECT 
    quality_check_result,
    COUNT(*) as issue_count
FROM silver_orders
WHERE quality_check_result != 'PASS'
GROUP BY quality_check_result
ORDER BY issue_count DESC;
```

---

## 🎯 SUMMARY

| Aspect | Details |
|--------|---------|
| **Total Tables** | 9 (3 bronze + 3 silver + 3 gold) |
| **Total Columns** | 50+ (including quality_check_result) |
| **Total Rows** | 110,500+ |
| **Primary Keys** | 9 defined |
| **Foreign Keys** | 2 (orders→customers, orders→products) |
| **Quality Flags** | 7 types (PASS + 6 FAIL types) |
| **Aggregations** | 3 gold tables |
| **Row Filter** | quality_check_result = 'PASS' (Bronze→Gold) |

---

**Data Model Version:** 1.0  
**Last Updated:** August 30, 2026  
**Status:** ✅ Production Ready

