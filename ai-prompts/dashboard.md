# AI Prompts — Phase 6: Dashboard & Visualization

---

## Prompt 1: Dashboard Queries

**PROMPT SENT (USER):**
```
"Ok done with gold layer now next phase is I need to create a Databricks SQL Dashboard 
with 3 tiles for an eCommerce Medallion Architecture project.

Exact Requirements:
* Dashboard name: eCommerce Sales Dashboard
* 3 visualizations from gold layer tables

Tile 1: Top 10 Products by Revenue (Bar Chart)
Tile 2: Customer Revenue Distribution (Histogram)
Tile 3: Customer Segmentation (Pie Chart)

Write queries, configure visualizations, add filters. 
Also give me a file with the sql queries that i can add in git repo."
```

**AI RESPONSE SUMMARY:**
- Created dashboard_queries.sql with 3 queries:
  1. Top 10 Products:
     ```sql
     SELECT product_name, ROUND(total_revenue, 2) as revenue
     FROM gold_sales_by_product
     ORDER BY total_revenue DESC
     LIMIT 10
     ```
  2. Customer Revenue Distribution:
     ```sql
     SELECT total_revenue
     FROM gold_revenue_by_customer
     WHERE total_revenue > 0
     ORDER BY total_revenue
     ```
  3. Customer Segmentation:
     ```sql
     SELECT segment_type, customer_count as count
     FROM gold_customer_segmentation
     ORDER BY total_revenue DESC
     ```
- Provided visualization configuration (chart types, axes, sorting)
- Included optional filters (Product Category, Customer Segment)
- Created DASHBOARD_SETUP_GUIDE.md with step-by-step instructions

**YOUR EVALUATION:**
✓ **What was good:**
- Simple, direct queries
- All data from gold layer (clean)
- Proper aggregations
- Includes optional filters
- Step-by-step setup guide
- Ready to copy-paste into Databricks

✓ **ACCEPTED** - All queries work correctly

**Files:**
- ✅ dashboard/dashboard_queries.sql
- ✅ dashboard/DASHBOARD_SETUP_GUIDE.md

---

## Prompt 2: Dashboard Setup Instructions

**PROMPT SENT (USER):**
```
"Can you provide step-by-step instructions for creating the dashboard in Databricks?
Include:
1. How to create each query
2. How to create visualizations
3. How to add filters
4. How to arrange tiles
5. How to save and share the dashboard"
```

**AI RESPONSE SUMMARY:**
- Created comprehensive DASHBOARD_SETUP_GUIDE.md
- Included 10 detailed steps:
  1. Create Query 1 (Bar Chart)
  2. Save to Dashboard
  3. Create Query 2 (Histogram)
  4. Add to Dashboard
  5. Create Query 3 (Pie Chart)
  6. Add to Dashboard
  7. Configure filters
  8. Arrange tiles
  9. Save dashboard
  10. View and share
- Each step has:
  - Exact menu paths
  - Configuration details
  - Expected results
  - Screenshots references (where applicable)

**YOUR EVALUATION:**
✓ **ACCEPTED** - Clear, actionable steps

**Documentation:**
- ✅ DASHBOARD_SETUP_GUIDE.md (5 KB, 10 steps)
- ✅ dashboard_queries.sql (2 KB, 3 queries)

---

## Prompt 3: Dashboard Verification

**PROMPT SENT (USER):**
```
"After creating the dashboard, how do I verify it's working correctly?
What should I see in each tile?
How do I test the filters?"
```

**AI RESPONSE SUMMARY:**
- Created verification checklist:
  1. Tile 1 (Bar): Top 10 products by revenue
     - Expected: Laptop > Monitor > Mouse > ... in descending order
     - Check: Highest revenue product at top
  2. Tile 2 (Histogram): Customer revenue distribution
     - Expected: Right-skewed distribution (most customers low revenue, few high)
     - Check: Bars get smaller as revenue increases
  3. Tile 3 (Pie): Customer segmentation
     - Expected: 4 segments with different sizes
     - Check: High-Value ~25%, Repeat ~33%, One-Time ~42%, Inactive ~0%
- Filter testing:
  - Product Category: Reduces products shown
  - Customer Segment: Reduces customers/segments shown
- Performance check: Dashboard loads within 5 seconds

**YOUR EVALUATION:**
✓ **ACCEPTED** - Verification successful

**Dashboard Status:**
- ✅ All 3 tiles display data
- ✅ Charts render correctly
- ✅ Filters functional
- ✅ Dashboard accessible
- ✅ Performance acceptable

---

## Summary: Dashboard Phase

**Total Prompts:** 3  
**Iterations:** 0 (accepted first draft)  
**Rejections:** 0  

**Final Deliverables:**
- ✅ dashboard_queries.sql (3 queries)
- ✅ DASHBOARD_SETUP_GUIDE.md (step-by-step)
- ✅ Dashboard: eCommerce Sales Dashboard (created)

**Key Decisions:**
- ✓ Accepted: Databricks SQL Dashboard (native)
- ✓ Accepted: 3 tile configuration
- ✓ Accepted: Optional filters
- ✓ Accepted: All data from gold layer

**Dashboard Tiles:**
- ✅ Tile 1: Bar chart - Top 10 products by revenue
- ✅ Tile 2: Histogram - Customer revenue distribution
- ✅ Tile 3: Pie chart - Customer segmentation (4 segments)

**Features:**
- ✅ 3 visualizations
- ✅ Optional filters (Product Category, Customer Segment)
- ✅ Real-time data from gold layer
- ✅ Professional appearance
- ✅ Easy to share

**Status:** ✅ Phase 6 Complete

