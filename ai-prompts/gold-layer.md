# AI Prompts — Phase 5: Gold Layer Aggregations

---

## Prompt 1: Gold Layer Aggregation Tables

**PROMPT SENT (USER):**
```
"I'm building a Databricks Medallion Architecture pipeline. Phase 4 (Silver layer) 
is complete with quality-checked tables and a quality_check_result column.

Now I need Phase 5: Gold Layer with 3 aggregations.
Create 1 master notebook: create_gold_tables.py that implements:

1. gold_sales_by_product - Group by product 
   Columns: product_id, product_name, category, total_orders, total_revenue, avg_order_value

2. gold_revenue_by_customer - Group by customer 
   Columns: customer_id, customer_name, customer_segment, total_orders, total_revenue, avg_order_value, lifetime_value_actual

3. gold_customer_segmentation - Segment customers by value/behavior 
   Columns: segment_type (High-Value/Repeat/One-Time/Inactive), customer_count, avg_revenue, total_revenue
   Logic:
   * High-Value: total_revenue > 75th percentile
   * Repeat: order_count >= 5 (but not high-value)
   * One-Time: order_count = 1
   * Inactive: no orders (if any)

Requirements:
* Filter all queries: WHERE quality_check_result = 'PASS'
* Only clean data to gold layer
* Write to gold_* tables (Delta tables)
* Include error handling and logging
* Print row counts for each gold table
* Use PySpark, not SQL strings (DataFrame API preferred)"
```

**AI RESPONSE SUMMARY:**
- Generated create_gold_tables.py with 3 aggregation tables
- Used PySpark DataFrame API (not SQL strings)
- Each aggregation:
  - Filters silver tables to PASS only
  - Implements proper grouping and aggregation
  - Uses appropriate aggregation functions (COUNT, SUM, AVG)
  - Includes error handling
  - Logs execution and row counts
- Customer segmentation:
  - Calculates 75th percentile using F.percentile_approx()
  - Implements CASE WHEN logic for 4 segments
  - Handles edge cases (no orders = inactive)
- Output:
  - gold_sales_by_product: 500 rows
  - gold_revenue_by_customer: 9,950 rows
  - gold_customer_segmentation: 4 rows

**YOUR EVALUATION:**
✓ **What was good:**
- Pure PySpark DataFrame API (no SQL strings)
- Proper filtering to PASS only
- Correct aggregation logic
- 75th percentile calculation for High-Value
- Clear segment logic
- Error handling comprehensive
- Logging detailed

✗ **What needed fixing:**
- Initial version had SQL strings embedded
- Not consistent with DataFrame API approach
- Harder to test and maintain

**What you changed:**
- Rewrote to use pure PySpark DataFrame API
- No embedded SQL statements
- F.col(), F.sum(), F.avg(), F.count(), etc.
- Better for testing and IDE support
- Why: Consistency, type safety, testability

---

## Prompt 2: Gold Layer Verification

**PROMPT SENT (USER):**
```
"After running create_gold_tables.py, verify the results:
1. gold_sales_by_product - should have 500 rows (one per product)
2. gold_revenue_by_customer - should have ~9,950 rows (only PASS customers)
3. gold_customer_segmentation - should have 4 rows (one per segment)

Also verify:
- No NULL values in gold tables
- Aggregations are correct (revenue = SUM of orders)
- Segmentation counts add up to total customers
- All data comes from PASS rows only"
```

**AI RESPONSE SUMMARY:**
- Created verification queries
- Provided SQL verification approach:
  - COUNT(*) for row verification
  - SUM checks for aggregation accuracy
  - Segment count verification
  - Sample data inspection
- Result validation:
  - gold_sales_by_product: 500 rows ✓
  - gold_revenue_by_customer: 9,950 rows ✓
  - gold_customer_segmentation: 4 rows ✓
  - All from PASS data only ✓
  - Aggregations correct ✓

**YOUR EVALUATION:**
✓ **ACCEPTED** - Verification successful

**Gold Table Results:**
- ✅ gold_sales_by_product: 500 products with revenue metrics
- ✅ gold_revenue_by_customer: 9,950 clean customers
- ✅ gold_customer_segmentation:
  - High-Value: ~2,487 customers
  - Repeat: ~3,245 customers
  - One-Time: ~4,218 customers
  - Inactive: ~0 customers
- ✅ All data filtered to PASS only
- ✅ No NULL values
- ✅ Aggregations verified accurate

---

## Prompt 3: Documentation & Data Model

**PROMPT SENT (USER):**
```
"Create comprehensive documentation for the gold layer:
1. Data model - what columns, data types, relationships
2. Aggregation logic - how each table is computed
3. SQL equivalent - show the SQL that would do the same thing
4. Performance considerations - indexes, partitioning
5. Example queries - how to use the gold tables"
```

**AI RESPONSE SUMMARY:**
- Created data-model.md with complete gold layer schema
- Documented all columns with data types
- Explained aggregation logic for each table
- Provided PySpark and SQL equivalents
- Recommended indexes for performance
- Provided example queries for analytics
- Included performance tips

**YOUR EVALUATION:**
✓ **ACCEPTED** - Comprehensive documentation

**Files:**
- ✅ data-model.md (gold layer section)
- ✅ create_gold_tables.py (commented code)

---

## Summary: Gold Layer Phase

**Total Prompts:** 3  
**Iterations:** 1 (SQL strings → pure PySpark DataFrame API)  
**Rejections:** 0  

**Final Deliverable:**
- ✅ create_gold_tables.py (single master notebook)
- ✅ Documentation (data model + examples)

**Key Decisions:**
- ✓ Accepted: PySpark DataFrame API (not SQL)
- ✓ Accepted: Filter to PASS only
- ✓ Accepted: 4-way customer segmentation
- ✓ Accepted: 75th percentile for High-Value
- ✗ Rejected: SQL string embedding

**Gold Tables Created:**
- ✅ gold_sales_by_product: 500 rows
- ✅ gold_revenue_by_customer: 9,950 rows
- ✅ gold_customer_segmentation: 4 rows
- ✅ Total gold data: ~10,454 rows (aggregated)

**Data Quality:**
- ✅ All gold data filtered from PASS rows only
- ✅ No NULL values in gold tables
- ✅ Aggregations verified accurate
- ✅ Ready for analytics and BI

**Status:** ✅ Phase 5 Complete

