#!/usr/bin/env python3
"""
Generate sample data for Databricks Medallion Architecture Pipeline

This version uses ONLY Python standard library - NO external dependencies required
(No Faker needed)

This script generates sample CSV files with intentional data quality issues
exactly as specified in requirements-analysis.md

SPECIFICATIONS (EXACT FROM REQUIREMENTS):
- customers.csv: 10,000 rows
  * 50 rows with NULL email (completeness issue)
  * 10 rows with duplicate customer_id (uniqueness issue)
  
- products.csv: 500 rows
  * No quality issues
  
- orders.csv: 100,000 rows
  * 100 rows with NULL customer_id (completeness)
  * 200 rows with NULL product_id (completeness)
  * 50 rows with invalid customer_id (referential integrity)
  * 30 rows with invalid product_id (referential integrity)
  * 20 rows with duplicate order_id (uniqueness)
  * Total: ~700 quality issues

NO ASSUMPTIONS - All parameters from requirements document
NO EXTERNAL DEPENDENCIES - Uses only standard library
"""

import csv
import random
import string
from datetime import datetime, timedelta

# ============================================================================
# CONFIGURATION - FROM REQUIREMENTS DOCUMENT
# ============================================================================

# Row counts (EXACT from requirements)
CUSTOMERS_COUNT = 10_000
PRODUCTS_COUNT = 500
ORDERS_COUNT = 100_000

# Quality issues counts (EXACT from requirements)
CUSTOMERS_NULL_EMAIL = 50
CUSTOMERS_DUPLICATE_ID = 10

ORDERS_NULL_CUSTOMER_ID = 100
ORDERS_NULL_PRODUCT_ID = 200
ORDERS_INVALID_CUSTOMER_FK = 50
ORDERS_INVALID_PRODUCT_FK = 30
ORDERS_DUPLICATE_ID = 20

TOTAL_QUALITY_ISSUES = (
    CUSTOMERS_NULL_EMAIL + 
    CUSTOMERS_DUPLICATE_ID + 
    ORDERS_NULL_CUSTOMER_ID + 
    ORDERS_NULL_PRODUCT_ID + 
    ORDERS_INVALID_CUSTOMER_FK + 
    ORDERS_INVALID_PRODUCT_FK + 
    ORDERS_DUPLICATE_ID
)

# ============================================================================
# HELPER FUNCTIONS - DATA GENERATION (Standard Library Only)
# ============================================================================

def random_name():
    """Generate a random person name"""
    first_names = ["James", "Mary", "Robert", "Patricia", "Michael", "Jennifer", 
                   "William", "Linda", "David", "Barbara", "Richard", "Susan",
                   "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
                   "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty",
                   "John", "Margaret", "Donald", "Sandra", "Mark", "Ashley",
                   "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna"]
    
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Garcia",
                  "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
                  "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
                  "Jackson", "Martin", "Lee", "White", "Harris", "Martin",
                  "Thompson", "Perez", "Roberts", "Edwards", "Collins", "Reeves"]
    
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def random_email():
    """Generate a random email address"""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com", 
               "company.com", "mail.com", "email.com", "test.com"]
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@{random.choice(domains)}"


def random_country():
    """Generate a random country"""
    countries = ["USA", "Canada", "Mexico", "UK", "France", "Germany", "Spain",
                 "Italy", "Japan", "China", "India", "Brazil", "Australia",
                 "South Korea", "Netherlands", "Switzerland", "Sweden", "Norway"]
    return random.choice(countries)


def random_product_name():
    """Generate a random product name"""
    adjectives = ["Premium", "Standard", "Deluxe", "Professional", "Basic",
                  "Advanced", "Ultra", "Super", "Smart", "Wireless"]
    nouns = ["Device", "Service", "Product", "Tool", "Solution", "System",
             "Software", "Hardware", "Console", "Hub"]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"


def random_category():
    """Generate a random product category"""
    categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports",
                  "Toys", "Beauty", "Food", "Software", "Hardware"]
    return random.choice(categories)


def random_date(start_year=2020, end_year=2024):
    """Generate a random date between start_year and end_year"""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + timedelta(days=random_days)


def random_segment():
    """Generate a random customer segment"""
    return random.choice(["Premium", "Standard", "Basic"])


def random_order_status():
    """Generate a random order status"""
    return random.choice(["Pending", "Completed", "Cancelled"])


# ============================================================================
# GENERATE PRODUCTS (500 rows, NO quality issues)
# ============================================================================

def generate_products():
    """Generate products.csv - 500 rows"""
    print("\n[1/3] Generating products.csv (500 rows)...")
    
    products = []
    
    for product_id in range(1, PRODUCTS_COUNT + 1):
        product = {
            'product_id': product_id,
            'product_name': random_product_name(),
            'category': random_category(),
            'price': round(random.uniform(10, 1000), 2),
            'cost': round(random.uniform(5, 500), 2),
            'stock_quantity': random.randint(0, 1000),
            'reorder_level': random.randint(10, 100)
        }
        products.append(product)
    
    print(f"  ✓ Created {len(products)} products")
    return products


# ============================================================================
# GENERATE CUSTOMERS (10,000 rows + quality issues)
# ============================================================================

def generate_customers():
    """
    Generate customers.csv - 10,000 rows
    With quality issues:
    - 50 rows with NULL email
    - 10 rows with duplicate customer_id
    """
    print("\n[2/3] Generating customers.csv (10,000 rows)...")
    
    customers = []
    used_ids = set()
    
    # Generate 9,940 clean customers (10,000 - 60 for issues)
    clean_count = CUSTOMERS_COUNT - CUSTOMERS_NULL_EMAIL - CUSTOMERS_DUPLICATE_ID
    
    for i in range(clean_count):
        customer_id = i + 1
        customer = {
            'customer_id': customer_id,
            'customer_name': random_name(),
            'email': random_email(),
            'country': random_country(),
            'signup_date': random_date(2020, 2024).strftime('%Y-%m-%d'),
            'customer_segment': random_segment(),
            'lifetime_value': round(random.uniform(100, 50000), 2)
        }
        customers.append(customer)
        used_ids.add(customer_id)
    
    # Add 50 customers with NULL email (COMPLETENESS ISSUE)
    print(f"  ✓ Adding {CUSTOMERS_NULL_EMAIL} rows with NULL email (completeness issue)...")
    for i in range(CUSTOMERS_NULL_EMAIL):
        customer_id = clean_count + i + 1
        customer = {
            'customer_id': customer_id,
            'customer_name': random_name(),
            'email': '',  # EMPTY EMAIL - QUALITY ISSUE
            'country': random_country(),
            'signup_date': random_date(2020, 2024).strftime('%Y-%m-%d'),
            'customer_segment': random_segment(),
            'lifetime_value': round(random.uniform(100, 50000), 2)
        }
        customers.append(customer)
        used_ids.add(customer_id)
    
    # Add 10 customers with DUPLICATE customer_id (UNIQUENESS ISSUE)
    print(f"  ✓ Adding {CUSTOMERS_DUPLICATE_ID} rows with duplicate customer_id (uniqueness issue)...")
    duplicate_ids = random.sample(list(used_ids), CUSTOMERS_DUPLICATE_ID)
    for dup_id in duplicate_ids:
        customer = {
            'customer_id': dup_id,  # DUPLICATE ID - QUALITY ISSUE
            'customer_name': random_name(),
            'email': random_email(),
            'country': random_country(),
            'signup_date': random_date(2020, 2024).strftime('%Y-%m-%d'),
            'customer_segment': random_segment(),
            'lifetime_value': round(random.uniform(100, 50000), 2)
        }
        customers.append(customer)
    
    print(f"  ✓ Created {len(customers)} customer rows")
    print(f"    - Clean rows: {clean_count}")
    print(f"    - NULL email issues: {CUSTOMERS_NULL_EMAIL}")
    print(f"    - Duplicate ID issues: {CUSTOMERS_DUPLICATE_ID}")
    
    return customers, used_ids


# ============================================================================
# GENERATE ORDERS (100,000 rows + quality issues)
# ============================================================================

def generate_orders(customer_ids, product_ids):
    """
    Generate orders.csv - 100,000 rows
    With quality issues as per specifications
    """
    print("\n[3/3] Generating orders.csv (100,000 rows)...")
    
    orders = []
    base_order_id = 1000
    all_customer_ids = list(customer_ids)
    all_product_ids = product_ids
    
    quality_issues_count = (
        ORDERS_NULL_CUSTOMER_ID + 
        ORDERS_NULL_PRODUCT_ID + 
        ORDERS_INVALID_CUSTOMER_FK + 
        ORDERS_INVALID_PRODUCT_FK + 
        ORDERS_DUPLICATE_ID
    )
    clean_count = ORDERS_COUNT - quality_issues_count
    
    # Generate clean orders
    print(f"  ✓ Generating {clean_count} clean orders...")
    for i in range(clean_count):
        order_id = base_order_id + i
        quantity = random.randint(1, 50)
        unit_price = round(random.uniform(10, 500), 2)
        total_amount = round(quantity * unit_price, 2)
        
        order = {
            'order_id': order_id,
            'customer_id': random.choice(all_customer_ids),
            'order_date': random_date(2022, 2024).strftime('%Y-%m-%d'),
            'product_id': random.choice(all_product_ids),
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'order_status': random_order_status(),
            'payment_date': random_date(2022, 2024).strftime('%Y-%m-%d')
        }
        orders.append(order)
    
    # Add 100 orders with NULL customer_id (COMPLETENESS ISSUE)
    print(f"  ✓ Adding {ORDERS_NULL_CUSTOMER_ID} rows with NULL customer_id (completeness issue)...")
    for i in range(ORDERS_NULL_CUSTOMER_ID):
        order_id = base_order_id + clean_count + i
        quantity = random.randint(1, 50)
        unit_price = round(random.uniform(10, 500), 2)
        total_amount = round(quantity * unit_price, 2)
        
        order = {
            'order_id': order_id,
            'customer_id': '',  # NULL CUSTOMER_ID - QUALITY ISSUE
            'order_date': random_date(2022, 2024).strftime('%Y-%m-%d'),
            'product_id': random.choice(all_product_ids),
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'order_status': random_order_status(),
            'payment_date': random_date(2022, 2024).strftime('%Y-%m-%d')
        }
        orders.append(order)
    
    # Add 200 orders with NULL product_id (COMPLETENESS ISSUE)
    print(f"  ✓ Adding {ORDERS_NULL_PRODUCT_ID} rows with NULL product_id (completeness issue)...")
    start_idx = clean_count + ORDERS_NULL_CUSTOMER_ID
    for i in range(ORDERS_NULL_PRODUCT_ID):
        order_id = base_order_id + start_idx + i
        quantity = random.randint(1, 50)
        unit_price = round(random.uniform(10, 500), 2)
        total_amount = round(quantity * unit_price, 2)
        
        order = {
            'order_id': order_id,
            'customer_id': random.choice(all_customer_ids),
            'order_date': random_date(2022, 2024).strftime('%Y-%m-%d'),
            'product_id': '',  # NULL PRODUCT_ID - QUALITY ISSUE
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'order_status': random_order_status(),
            'payment_date': random_date(2022, 2024).strftime('%Y-%m-%d')
        }
        orders.append(order)
    
    # Add 50 orders with INVALID customer_id (REFERENTIAL INTEGRITY ISSUE)
    print(f"  ✓ Adding {ORDERS_INVALID_CUSTOMER_FK} rows with invalid customer_id (referential integrity issue)...")
    start_idx = clean_count + ORDERS_NULL_CUSTOMER_ID + ORDERS_NULL_PRODUCT_ID
    invalid_customer_ids = [99999, 99998, 99997, 88888, 88887]
    for i in range(ORDERS_INVALID_CUSTOMER_FK):
        order_id = base_order_id + start_idx + i
        quantity = random.randint(1, 50)
        unit_price = round(random.uniform(10, 500), 2)
        total_amount = round(quantity * unit_price, 2)
        
        order = {
            'order_id': order_id,
            'customer_id': random.choice(invalid_customer_ids),  # INVALID FK - QUALITY ISSUE
            'order_date': random_date(2022, 2024).strftime('%Y-%m-%d'),
            'product_id': random.choice(all_product_ids),
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'order_status': random_order_status(),
            'payment_date': random_date(2022, 2024).strftime('%Y-%m-%d')
        }
        orders.append(order)
    
    # Add 30 orders with INVALID product_id (REFERENTIAL INTEGRITY ISSUE)
    print(f"  ✓ Adding {ORDERS_INVALID_PRODUCT_FK} rows with invalid product_id (referential integrity issue)...")
    start_idx = (clean_count + ORDERS_NULL_CUSTOMER_ID + ORDERS_NULL_PRODUCT_ID + 
                 ORDERS_INVALID_CUSTOMER_FK)
    invalid_product_ids = [99999, 99998, 99997, 88888, 88887]
    for i in range(ORDERS_INVALID_PRODUCT_FK):
        order_id = base_order_id + start_idx + i
        quantity = random.randint(1, 50)
        unit_price = round(random.uniform(10, 500), 2)
        total_amount = round(quantity * unit_price, 2)
        
        order = {
            'order_id': order_id,
            'customer_id': random.choice(all_customer_ids),
            'order_date': random_date(2022, 2024).strftime('%Y-%m-%d'),
            'product_id': random.choice(invalid_product_ids),  # INVALID FK - QUALITY ISSUE
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'order_status': random_order_status(),
            'payment_date': random_date(2022, 2024).strftime('%Y-%m-%d')
        }
        orders.append(order)
    
    # Add 20 orders with DUPLICATE order_id (UNIQUENESS ISSUE)
    print(f"  ✓ Adding {ORDERS_DUPLICATE_ID} rows with duplicate order_id (uniqueness issue)...")
    clean_order_ids = [o['order_id'] for o in orders[:clean_count]]
    duplicate_order_ids = random.sample(clean_order_ids, ORDERS_DUPLICATE_ID)
    for dup_id in duplicate_order_ids:
        quantity = random.randint(1, 50)
        unit_price = round(random.uniform(10, 500), 2)
        total_amount = round(quantity * unit_price, 2)
        
        order = {
            'order_id': dup_id,  # DUPLICATE ORDER_ID - QUALITY ISSUE
            'customer_id': random.choice(all_customer_ids),
            'order_date': random_date(2022, 2024).strftime('%Y-%m-%d'),
            'product_id': random.choice(all_product_ids),
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'order_status': random_order_status(),
            'payment_date': random_date(2022, 2024).strftime('%Y-%m-%d')
        }
        orders.append(order)
    
    print(f"  ✓ Created {len(orders)} order rows")
    print(f"    - Clean rows: {clean_count}")
    print(f"    - NULL customer_id issues: {ORDERS_NULL_CUSTOMER_ID}")
    print(f"    - NULL product_id issues: {ORDERS_NULL_PRODUCT_ID}")
    print(f"    - Invalid customer_id (FK) issues: {ORDERS_INVALID_CUSTOMER_FK}")
    print(f"    - Invalid product_id (FK) issues: {ORDERS_INVALID_PRODUCT_FK}")
    print(f"    - Duplicate order_id issues: {ORDERS_DUPLICATE_ID}")
    print(f"    - Total quality issues: {quality_issues_count}")
    
    return orders


# ============================================================================
# WRITE TO CSV FILES
# ============================================================================

def write_csv(filename, fieldnames, rows):
    """Write data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"  ✓ Saved: {filename} ({len(rows)} rows)")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("DATA GENERATION FOR DATABRICKS MEDALLION ARCHITECTURE PIPELINE")
    print("(Standard Library Version - No External Dependencies)")
    print("="*80)
    print("\nGENERATING SAMPLE DATA (Exact specifications from requirements document)")
    print(f"\nTarget:")
    print(f"  • customers.csv: {CUSTOMERS_COUNT:,} rows")
    print(f"  • products.csv: {PRODUCTS_COUNT:,} rows")
    print(f"  • orders.csv: {ORDERS_COUNT:,} rows")
    print(f"  • Total quality issues: ~{TOTAL_QUALITY_ISSUES:,} rows (0.7% error rate)")
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate products (no quality issues)
    products = generate_products()
    product_ids = [p['product_id'] for p in products]
    
    # Generate customers (with quality issues)
    customers, customer_ids = generate_customers()
    
    # Generate orders (with quality issues)
    orders = generate_orders(customer_ids, product_ids)
    
    # Write CSV files
    print("\n" + "-"*80)
    print("WRITING CSV FILES")
    print("-"*80)
    
    # Write customers
    customer_fieldnames = ['customer_id', 'customer_name', 'email', 'country', 
                          'signup_date', 'customer_segment', 'lifetime_value']
    write_csv('data/customers.csv', customer_fieldnames, customers)
    
    # Write products
    product_fieldnames = ['product_id', 'product_name', 'category', 'price', 
                         'cost', 'stock_quantity', 'reorder_level']
    write_csv('data/products.csv', product_fieldnames, products)
    
    # Write orders
    order_fieldnames = ['order_id', 'customer_id', 'order_date', 'product_id', 
                       'quantity', 'unit_price', 'total_amount', 'order_status', 'payment_date']
    write_csv('data/orders.csv', order_fieldnames, orders)
    
    # Summary
    print("\n" + "="*80)
    print("✅ DATA GENERATION COMPLETE")
    print("="*80)
    print(f"\nGenerated Files:")
    print(f"  ✓ data/customers.csv ({len(customers):,} rows)")
    print(f"  ✓ data/products.csv ({len(products):,} rows)")
    print(f"  ✓ data/orders.csv ({len(orders):,} rows)")
    print(f"\nQuality Issues Breakdown:")
    print(f"  • customers - NULL email: {CUSTOMERS_NULL_EMAIL} rows")
    print(f"  • customers - Duplicate ID: {CUSTOMERS_DUPLICATE_ID} rows")
    print(f"  • orders - NULL customer_id: {ORDERS_NULL_CUSTOMER_ID} rows")
    print(f"  • orders - NULL product_id: {ORDERS_NULL_PRODUCT_ID} rows")
    print(f"  • orders - Invalid customer_id (FK): {ORDERS_INVALID_CUSTOMER_FK} rows")
    print(f"  • orders - Invalid product_id (FK): {ORDERS_INVALID_PRODUCT_FK} rows")
    print(f"  • orders - Duplicate order_id: {ORDERS_DUPLICATE_ID} rows")
    print(f"  ─────────────────────────────────────────")
    print(f"  • TOTAL QUALITY ISSUES: ~{TOTAL_QUALITY_ISSUES:,} rows")
    print(f"\n✅ All quality issues were intentionally added as per requirements")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()

