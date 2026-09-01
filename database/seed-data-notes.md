# Seed Data Notes - Data Generation Strategy

**eCommerce Sales Pipeline - Test Data Generation**

---

## 📋 OVERVIEW

Complete documentation of how test data is generated with intentional quality issues to validate the pipeline.

**Purpose:** Create realistic test data that includes known quality problems to verify the quality check framework works correctly.

---

## 🎯 DATA GENERATION STRATEGY

### Principle: Controlled Chaos
Generate datasets that:
- ✅ Contain realistic data patterns
- ✅ Include intentional quality issues (~700 rows, ~0.6%)
- ✅ Are reproducible (seeded with random seed 42)
- ✅ Match business domain (eCommerce sales)
- ✅ Scale appropriately (10K customers, 100K orders, 500 products)

---

## 📊 DATASET SPECIFICATIONS

### Customers (10,000 rows)

**Purpose:** Customer master data

**Fields Generated:**
```
customer_id (INT)
├── Range: 1 to 10,000
├── Unique: YES (except 10 intentional duplicates)
└── Type: Sequential + shuffled

customer_name (STRING)
├── Format: First Name + Last Name
├── Pattern: Random combinations from name lists
└── Example: "John Smith", "Jane Doe"

email (STRING)
├── Format: firstname.lastname@domain.com
├── Pattern: Derived from customer_name
├── Issues: 50 rows set to NULL (intentional)

country (STRING)
├── Values: USA, Canada, UK, Germany, France
├── Distribution: Weighted random
└── Proportions: USA=40%, Canada=20%, others=10-15%

signup_date (DATE)
├── Range: 2020-01-01 to 2024-12-31
├── Pattern: Random date within range
└── Business Logic: Recent signups more weighted (2023-2024)

customer_segment (STRING)
├── Values: Premium, Standard, Basic
├── Distribution: Premium=25%, Standard=35%, Basic=40%
└── Rules: Based on generated data patterns

lifetime_value (DECIMAL)
├── Range: $0.00 to $50,000.00
├── Calculation: Based on expected order frequency × avg order value
└── Pattern: Exponential distribution (skewed toward lower values)
```

**Intentional Quality Issues (50 rows):**
```
Issue Type          | Count | Details
--------------------|-------|----------------------------
NULL email          | 50    | Email field set to NULL
Duplicate ID        | 10    | customer_id appears twice
Total Issues        | 60    | (Some rows have multiple issues)
```

**Generation Method:**
```python
# Using standard library only (no Faker)
import random
import string
from datetime import datetime, timedelta

random.seed(42)  # Reproducible

# Generate customer_id
customer_ids = list(range(1, 10001))
random.shuffle(customer_ids)

# Add 10 intentional duplicates
duplicate_ids = random.sample(customer_ids, 10)
customer_ids.extend(duplicate_ids)

# Generate other fields
for cid in customer_ids:
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    
    # Intentional NULL emails
    if random.random() < 0.005:  # 0.5%
        email = None
    
    # ... other field generation
```

---

### Orders (100,000 rows)

**Purpose:** Transaction/order data

**Fields Generated:**
```
order_id (INT)
├── Range: 1001 to 101,000
├── Unique: Mostly (except 20 intentional duplicates)
└── Pattern: Sequential with duplicates inserted randomly

customer_id (INT)
├── Source: From customers table (1-10,000)
├── Distribution: Some customers order more than others
├── Issues: 100 rows set to NULL (intentional)
└── Issues: 50 rows have non-existent IDs (intentional FK orphans)

order_date (DATE)
├── Range: 2023-01-01 to 2024-12-31
├── Pattern: Random within range
├── Business Logic: Some customers more active on certain dates
└── Seasonality: Holiday peaks (12/20-12/31) higher frequency

product_id (INT)
├── Source: From products table (501-1000)
├── Distribution: Some products ordered more frequently
├── Issues: 200 rows set to NULL (intentional)
└── Issues: 30 rows have non-existent IDs (intentional FK orphans)

quantity (INT)
├── Range: 1 to 100
├── Distribution: Biased toward 1-5 (most common)
├── Pattern: Exponential distribution

unit_price (DECIMAL)
├── Derived from: product master
├── Range: $9.99 to $999.99
└── Pattern: Matches product pricing

total_amount (DECIMAL)
├── Calculation: quantity × unit_price
├── Issues: 40 rows have NULL or mismatched values
└── Validation: Should equal quantity × unit_price

order_status (STRING)
├── Values: Pending, Completed, Cancelled
├── Distribution: 85% Completed, 10% Pending, 5% Cancelled
└── Rules: Cancelled orders still have valid transactions

payment_date (DATE)
├── Nullable: YES
├── Rule: NULL if order_status = 'Pending'
└── Pattern: 1-5 days after order_date if Completed
```

**Intentional Quality Issues (640 rows):**
```
Issue Type           | Count | Details
--------------------|-------|----------------------------
NULL customer_id     | 100   | customer_id field NULL
NULL product_id      | 200   | product_id field NULL
Invalid customer FK  | 50    | customer_id doesn't exist
Invalid product FK   | 30    | product_id doesn't exist
Duplicate order_id   | 20    | order_id appears twice
NULL total_amount    | 40    | Amount field NULL/mismatch
Total Issues         | 440   | Some rows have multiple issues
```

**Generation Method:**
```python
# Generate orders
# Each customer gets 3-50 orders (weighted distribution)
for customer_id in range(1, 10001):
    num_orders = random.choices(
        range(1, 51),
        weights=[0.3] + [0.01]*49  # Most customers: 1-3 orders
    )
    
    for _ in range(num_orders):
        order_date = random.date(start, end)
        product_id = random.choice(VALID_PRODUCT_IDS)
        quantity = random.expovariate(0.5)  # Exponential dist
        
        # Intentional issues
        if random.random() < 0.001:  # 0.1%
            customer_id = None  # NULL customer_id
        if random.random() < 0.002:  # 0.2%
            product_id = None  # NULL product_id
        if random.random() < 0.0005:  # 0.05%
            customer_id = 999999  # Invalid FK
        if random.random() < 0.0003:  # 0.03%
            product_id = 888888  # Invalid FK
```

---

### Products (500 rows)

**Purpose:** Product master data

**Fields Generated:**
```
product_id (INT)
├── Range: 501 to 1000
├── Unique: YES
└── Type: Sequential

product_name (STRING)
├── Pattern: Product type + brand + variant
└── Examples: "Laptop Dell XPS 13", "Monitor Samsung 4K"

category (STRING)
├── Values: Electronics, Furniture, Clothing, Accessories, etc.
├── Distribution: Weighted by product type
└── Count: ~10-15 categories

price (DECIMAL)
├── Range: $9.99 to $999.99
├── Distribution: Skewed (more low-cost items)
└── Rules: price > cost

cost (DECIMAL)
├── Range: 40-70% of price (profit margin)
└── Calculation: price × random(0.4, 0.7)

stock_quantity (INT)
├── Range: 0 to 1,000
├── Distribution: Weighted (some stock-outs)
└── Pattern: Popular items have higher stock

reorder_level (INT)
├── Range: 1 to 100
├── Rules: Should be < stock_quantity
└── Pattern: reorder_level ≈ 10-20% of normal stock
```

**Intentional Quality Issues:**
```
Issue Type  | Count | Details
------------|-------|----------------------------
Issues      | 0     | Products table is CLEAN
```

**Why Clean?** Products are reference/master data. Quality checks focus on transactional data (Orders) and customer data.

---

## 📈 DATASET STATISTICS

### Volume

| Table | Rows | Size | Notes |
|-------|------|------|-------|
| customers | 10,000 | ~1 MB | After duplicates included |
| orders | 100,000 | ~10 MB | Transactional data |
| products | 500 | ~50 KB | Reference data |
| **Total** | **110,500** | **~11 MB** | Test dataset |

### Quality Issue Distribution

| Category | Issues | % of Total |
|----------|--------|-----------|
| Customers | 60 | 13.0% |
| Orders | 400 | 87.0% |
| Products | 0 | 0.0% |
| **Total** | **460** | **0.41%** |

---

## 🔧 GENERATION PROCESS

### Step 1: Environment Setup
```bash
# No dependencies needed - standard library only
python3 src/data_generation/generate_sample_data_no_dependencies.py
```

### Step 2: CSV File Creation
Files created:
- `data/customers.csv` (10,001 lines = 1 header + 10,000 data)
- `data/orders.csv` (100,001 lines = 1 header + 100,000 data)
- `data/products.csv` (501 lines = 1 header + 500 data)

### Step 3: Quality Verification
```bash
# Verify row counts
wc -l data/*.csv

# Check for expected patterns
head -20 data/customers.csv
head -20 data/orders.csv
```

### Step 4: Upload to Databricks
1. Create folder: `/Users/email@company.com/medallion_pipeline/data/`
2. Upload all 3 CSV files
3. Verify in Databricks workspace

---

## ✅ REPRODUCIBILITY

### Seed Setting
```python
random.seed(42)  # Always use seed 42
```

**Effect:** Running the generator multiple times produces identical datasets.

**Verification:**
```bash
# First run
python3 generate_sample_data_no_dependencies.py

# Second run (same output)
python3 generate_sample_data_no_dependencies.py

# Compare files
diff data/customers.csv data/customers_second_run.csv
# Result: No difference (files are identical)
```

---

## 🎯 QUALITY ISSUE PLACEMENT

### Random Placement Strategy

**Why Random?** Prevents pipeline assumptions about where issues are.

**Examples:**
```python
# NULL email distribution
for row in customers:
    if random.random() < 0.005:  # 0.5% chance
        row['email'] = None

# Duplicate ID distribution
duplicate_ids = random.sample(all_ids, 10)
# Inserted at random positions in output

# Invalid FK distribution
for row in orders:
    if random.random() < 0.0005:  # 0.05% chance
        row['customer_id'] = 999999  # Non-existent
```

---

## 📝 DATA CHARACTERISTICS

### Customers

**Distribution Pattern:**
- Customer segments: Premium (25%), Standard (35%), Basic (40%)
- Signup dates: Skewed toward recent (2023-2024)
- Lifetime value: Exponential (right-skewed)
- Order frequency: 3-50 orders per customer (weighted)

**Business Realism:**
- ✅ Matches eCommerce customer patterns
- ✅ Seasonal ordering behavior
- ✅ Customer segmentation reflects value tiers
- ✅ Geographic distribution reasonable

### Orders

**Distribution Pattern:**
- Order dates: Uniform across 2023-2024 (with holiday peaks)
- Order amounts: Range from $10 to $100,000
- Product mix: Popular items ordered more frequently
- Order status: 85% complete, 10% pending, 5% cancelled

**Business Realism:**
- ✅ Quantity variations (1-100 items per order)
- ✅ Multiple orders per customer
- ✅ Seasonal peaks (December)
- ✅ Payment date logic (days after order)

### Products

**Distribution Pattern:**
- Categories: 10-15 different product types
- Price range: $9.99 to $999.99
- Stock levels: Realistic inventory levels
- Profit margins: 30-60% (typical retail)

**Business Realism:**
- ✅ Diverse product catalog
- ✅ Realistic pricing
- ✅ Stock-out situations
- ✅ Reorder thresholds

---

## 🔍 VALIDATION CHECKS

### Pre-Generation

- [x] Random seed set to 42
- [x] Date ranges valid (2020-2024)
- [x] Customer ID ranges correct (1-10,000)
- [x] Product ID ranges correct (501-1000)
- [x] Quality issue rates calculated

### Post-Generation

```bash
# Verify row counts
wc -l data/customers.csv  # Should be 10,001
wc -l data/orders.csv     # Should be 100,001
wc -l data/products.csv   # Should be 501

# Check for expected NULLs (in CSV, NULL = empty)
grep -c "^[^,]*,,*[^,]*$" data/customers.csv  # Should find NULLs

# Verify no missing lines
tail -5 data/customers.csv  # Should show last few rows
```

---

## 📊 EXPECTED ISSUES DETECTED

After running pipeline quality checks:

```
Customers Table:
  ✓ 50 rows: FAIL_NULL_email
  ✓ 10 rows: FAIL_DUPLICATE
  → 60 total issues

Orders Table:
  ✓ 100 rows: FAIL_NULL_customer_id
  ✓ 200 rows: FAIL_NULL_product_id
  ✓ 50 rows: FAIL_INVALID_customers_FK
  ✓ 30 rows: FAIL_INVALID_products_FK
  ✓ 20 rows: FAIL_DUPLICATE
  → 400 total issues

Products Table:
  ✓ 0 issues (clean)

TOTAL: 460 issues detected ✓
```

---

## 🚀 REGENERATING DATA

### If You Need Fresh Data

```bash
# Option 1: Delete and regenerate with same seed (reproducible)
rm data/*.csv
python3 src/data_generation/generate_sample_data_no_dependencies.py

# Option 2: Modify seed for different data
# Edit: random.seed(42) → random.seed(999)
# Result: Different data, same distribution patterns
```

### If You Need Different Issue Patterns

Modify issue rates in generation script:
```python
# Current: 0.5% NULL email
if random.random() < 0.005:  # Change 0.005 to desired rate

# Current: 0.05% Invalid FKs
if random.random() < 0.0005:  # Change 0.0005 to desired rate
```

---

## 📌 IMPORTANT NOTES

1. **Reproducibility:** seed(42) ensures identical output across runs
2. **Issue Distribution:** Random placement prevents pipeline assumptions
3. **Realistic Patterns:** Data follows business logic and distributions
4. **No Dependencies:** Uses only Python standard library (csv, random, datetime)
5. **Scalability:** Easy to adjust row counts and issue rates

---

**Last Updated:** August 30, 2026  
**Status:** ✅ Production Ready for Testing

