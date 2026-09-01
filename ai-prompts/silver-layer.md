# AI Prompts — Phase 4: Silver Layer Quality Checks

---

## Prompt 1: Silver Layer Quality Checks

**PROMPT SENT (USER):**
```
"I'm building a Databricks Medallion Architecture pipeline. Phase 3 (Bronze layer) 
is complete with 3 tables:
* bronze_customers (10,000 rows)
* bronze_orders (100,000 rows)
* bronze_products (500 rows)

Now I need Phase 4: Silver Layer with quality checks.
Create 5 PySpark notebooks that add a quality_check_result column to flag issues:

1. 01_quality_completeness.py
   * Flag NULL values as FAIL_NULL_<column_name>
2. 02_quality_uniqueness.py
   * Flag duplicate keys as FAIL_DUPLICATE
3. 03_quality_referential_integrity.py
   * Flag orphan FKs as FAIL_INVALID_<fk>_FK (use LEFT JOIN)
4. 04_quality_type_validation.py
   * Flag type mismatches as FAIL_TYPE_<column_name>
5. create_silver_tables.py
   * Master script that runs all 4 checks sequentially (call functions directly, no notebook.run)

Each script reads from bronze_* tables and writes to silver_* tables. 
Don't delete rows - just flag them with PASS or FAIL_*.

Expected issues (intentional):
* Customers: 50 NULL emails, 10 duplicate IDs
* Orders: 100 NULL customer_id, 200 NULL product_id, 50 invalid customer FKs, 30 invalid product FKs, 20 duplicate order IDs
* Products: no issues

Use PySpark with Delta Lake. Include error handling, logging, and print summaries 
(rows passed/failed per check type)."
```

**AI RESPONSE SUMMARY:**
- Generated 4 quality check scripts (completeness, uniqueness, referential integrity, type validation)
- Each adds quality_check_result column with appropriate flags
- Completeness: Checks NULL values in required fields
- Uniqueness: Uses window functions to detect duplicates
- Referential Integrity: Uses LEFT JOIN to find orphan FKs
- Type Validation: Type casting with error handling
- Master script: create_silver_tables.py calls all 4 sequentially
- Included:
  - Error handling (try-except blocks)
  - Logging (timestamps, row counts)
  - Print summaries (PASS vs FAIL counts)
  - No row deletion (flag-and-preserve approach)

**YOUR EVALUATION:**
✓ **What was good:**
- Proper quality check implementation
- Cumulative flagging approach
- Window functions for efficiency
- LEFT JOIN for FK validation
- Clear flag naming convention
- Error handling comprehensive
- No rows deleted (preserved for audit)

✓ **ACCEPTED** - All 5 scripts meet requirements

**Files:**
- ✅ src/silver/01_quality_completeness.py
- ✅ src/silver/02_quality_uniqueness.py
- ✅ src/silver/03_quality_referential_integrity.py
- ✅ src/silver/04_quality_type_validation.py
- ✅ src/silver/create_silver_tables.py

---

## Prompt 2: Quality Check Verification

**PROMPT SENT (USER):**
```
"After running the silver layer scripts, I'm getting these results:
- silver_customers: 9,950 PASS, 50 FAIL_NULL_email
- silver_orders: Some rows with FAIL_INVALID_customers_FK

Is this correct? Should I be seeing these patterns? How do I verify the quality 
checks are working correctly?"
```

**AI RESPONSE SUMMARY:**
- Confirmed results match expected patterns
- Explained verification approach:
  1. Row count verification (should still be 110,500 total)
  2. PASS vs FAIL distribution (should match intentional issues)
  3. Quality flag distribution (breakdown by issue type)
  4. Sample data inspection (view specific failures)
- Provided SQL queries to verify:
  - SELECT quality_check_result, COUNT(*) GROUP BY quality_check_result
  - SELECT * FROM silver_customers WHERE quality_check_result LIKE 'FAIL_%'
- Confirmed no data loss (all rows preserved)

**YOUR EVALUATION:**
✓ **ACCEPTED** - Verification approach solid

**Results Verified:**
- ✅ 9,940 customers PASS (expected)
- ✅ 60 customers FAIL (50 NULLs + 10 duplicates)
- ✅ 99,600 orders PASS (expected)
- ✅ 400 orders FAIL (various issues)
- ✅ 500 products PASS (expected)
- ✅ 0 products FAIL (no issues)
- ✅ Total: 110,500 rows (no data loss)

---

## Prompt 3: Quality Flag Documentation

**PROMPT SENT (USER):**
```
"Document all possible quality_check_result values and what they mean:
1. PASS - what does this mean exactly?
2. FAIL_NULL_* - which columns can be NULL?
3. FAIL_DUPLICATE - which tables/columns have duplicates?
4. FAIL_INVALID_*_FK - what are the FK relationships?
5. FAIL_TYPE_* - which columns can have type issues?

Create a reference guide."
```

**AI RESPONSE SUMMARY:**
- Created comprehensive quality flag reference:
  - PASS: Passed all quality checks
  - FAIL_NULL_email: NULL in customer email (customers)
  - FAIL_NULL_customer_id: NULL in orders.customer_id
  - FAIL_NULL_product_id: NULL in orders.product_id
  - FAIL_DUPLICATE: Duplicate primary key
  - FAIL_INVALID_customers_FK: Customer ID doesn't exist
  - FAIL_INVALID_products_FK: Product ID doesn't exist
  - FAIL_TYPE_*: Data type mismatch
- Documented which checks apply to each table
- Provided row count estimates per issue type

**YOUR EVALUATION:**
✓ **ACCEPTED** - Complete reference documentation

**Documentation:** Included in data-model.md and seed-data-notes.md

---

## Summary: Silver Layer Phase

**Total Prompts:** 3  
**Iterations:** 0 (accepted first draft)  
**Rejections:** 0  

**Final Deliverables:**
- ✅ 01_quality_completeness.py
- ✅ 02_quality_uniqueness.py
- ✅ 03_quality_referential_integrity.py
- ✅ 04_quality_type_validation.py
- ✅ create_silver_tables.py
- ✅ Quality flag reference documentation

**Key Decisions:**
- ✓ Accepted: Flag-and-preserve approach (no deletion)
- ✓ Accepted: Cumulative flagging in single column
- ✓ Accepted: Sequential quality check execution
- ✓ Accepted: Window functions for efficiency
- ✓ Accepted: LEFT JOIN for FK validation

**Data Quality Results:**
- ✅ Customers: 9,940 PASS, 60 FAIL (50 NULLs + 10 duplicates)
- ✅ Orders: 99,600 PASS, 400 FAIL (various issues)
- ✅ Products: 500 PASS, 0 FAIL (clean)
- ✅ Total: 110,500 rows (100% preserved, none deleted)
- ✅ Issues detected: 460+ (all intentional, all caught)

**Status:** ✅ Phase 4 Complete

