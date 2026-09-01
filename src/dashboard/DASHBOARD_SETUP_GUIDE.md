# Databricks SQL Dashboard Setup Guide

**Dashboard Name:** `eCommerce Sales Dashboard`

---

## 📊 3 TILES CONFIGURATION

### **TILE 1: Top 10 Products by Revenue (Bar Chart)**

**Query:**
```sql
SELECT 
    product_name,
    ROUND(total_revenue, 2) as revenue
FROM gold_sales_by_product
ORDER BY total_revenue DESC
LIMIT 10
```

**Visualization Configuration:**
- Chart Type: **Bar Chart**
- X Axis: `product_name`
- Y Axis: `revenue`
- Sort: `revenue DESC`
- Title: "Top 10 Products by Revenue"

**Filter (Optional):** Product Category

---

### **TILE 2: Customer Revenue Distribution (Histogram)**

**Query:**
```sql
SELECT 
    total_revenue
FROM gold_revenue_by_customer
WHERE total_revenue > 0
ORDER BY total_revenue
```

**Visualization Configuration:**
- Chart Type: **Histogram** (or Distribution)
- X Axis: `total_revenue`
- Buckets: Auto (20)
- Title: "Customer Revenue Distribution"

**Filter (Optional):** Customer Segment

---

### **TILE 3: Customer Segmentation (Pie Chart)**

**Query:**
```sql
SELECT 
    segment_type,
    customer_count as count
FROM gold_customer_segmentation
ORDER BY total_revenue DESC
```

**Visualization Configuration:**
- Chart Type: **Pie Chart**
- Key: `segment_type`
- Value: `count`
- Title: "Customer Segmentation"

**Filter (Optional):** Segment Type

---

## 🚀 STEPS TO CREATE DASHBOARD IN DATABRICKS

### Step 1: Create Query 1 (Bar Chart)
1. Go to **SQL** → **+ New Query**
2. Copy Query 1 from dashboard_queries.sql
3. Click **Run**
4. Click **Visualizations**
5. Click **+ Add visualization**
6. Select **Bar Chart**
7. X Axis: `product_name`
8. Y Axis: `revenue`
9. Click **Save**
10. Name: "Top 10 Products by Revenue"

### Step 2: Save to Dashboard
1. Click **Save** button
2. Click **Save to Dashboard**
3. Click **Create new dashboard**
4. Name: `eCommerce Sales Dashboard`
5. Click **Save to Dashboard**

### Step 3: Create Query 2 (Histogram)
1. Go to **SQL** → **+ New Query**
2. Copy Query 2 from dashboard_queries.sql
3. Click **Run**
4. Click **Visualizations** → **+ Add visualization**
5. Select **Histogram**
6. X Axis: `total_revenue`
7. Buckets: Auto
8. Click **Save**
9. Name: "Customer Revenue Distribution"

### Step 4: Add Query 2 to Dashboard
1. Click **Save**
2. Click **Save to Dashboard**
3. Select: `eCommerce Sales Dashboard` (existing)
4. Click **Save to Dashboard**

### Step 5: Create Query 3 (Pie Chart)
1. Go to **SQL** → **+ New Query**
2. Copy Query 3 from dashboard_queries.sql
3. Click **Run**
4. Click **Visualizations** → **+ Add visualization**
5. Select **Pie Chart**
6. Key: `segment_type`
7. Value: `count`
8. Click **Save**
9. Name: "Customer Segmentation"

### Step 6: Add Query 3 to Dashboard
1. Click **Save**
2. Click **Save to Dashboard**
3. Select: `eCommerce Sales Dashboard` (existing)
4. Click **Save to Dashboard**

---

## 🔧 CONFIGURE DASHBOARD & ADD FILTERS

### Step 1: Open Dashboard
1. Click **Dashboards** (left sidebar)
2. Click **eCommerce Sales Dashboard**

### Step 2: Edit Dashboard
1. Click **Edit dashboard** (top right)

### Step 3: Add Filters (Optional)

**Filter Option A: Segment Type Filter**
1. Click **+ Add filter**
2. Name: `Segment`
3. Type: `Dropdown`
4. Data source: 
   ```sql
   SELECT DISTINCT segment_type FROM gold_customer_segmentation ORDER BY segment_type
   ```
5. Link to: Tile 2 and Tile 3
6. Click **Save**

**Filter Option B: Product Category Filter**
1. Click **+ Add filter**
2. Name: `Category`
3. Type: `Dropdown`
4. Data source:
   ```sql
   SELECT DISTINCT category FROM gold_sales_by_product ORDER BY category
   ```
5. Link to: Tile 1
6. Click **Save**

### Step 4: Arrange Tiles
1. Drag tiles to arrange
2. Resize tiles as needed
3. Place Tile 1 on top
4. Place Tile 2 and 3 on bottom

### Step 5: Save Dashboard
1. Click **Save dashboard** (top right)
2. Click **View dashboard**

---

## ✅ FINAL DASHBOARD

You should see:
- **Top:** Bar chart (Top 10 products)
- **Bottom left:** Histogram (Customer revenue)
- **Bottom right:** Pie chart (Customer segmentation)
- **Top left:** Filters (optional)

---

## 💾 FILES INCLUDED

- `dashboard_queries.sql` - All 3 SQL queries (ready to copy-paste)
- `DASHBOARD_SETUP_GUIDE.md` - This file with complete setup instructions

---

## 📁 GIT COMMIT

```bash
git add dashboard/
git commit -m "Phase 6: Dashboard queries and setup guide"
```

---

## 🎯 DASHBOARD COMPLETE!

3 tiles created from gold layer tables showing:
- Top performing products
- Customer revenue patterns
- Customer segmentation insights

Ready for analysis and decision-making! 🚀
