# AI Prompts — Phase 2: Data Generation

---

## Prompt 1: Initial Assessment & Memory Building

**PROMPT SENT (USER):**
```
"Hello act as an expert data engineer, i have an assignment to complete want you to help me with that. 
Dont assume anything, dont hallucinate and also read the complete document.
we have to create the scripts as asked and also have to share the prompt used.
Read the document very carefully and all the pages. Also memorize everything carefully."
```

**AI RESPONSE SUMMARY:**
- Acknowledged role as expert data engineer
- Confirmed understanding of requirements: don't assume, don't hallucinate
- Agreed to document all prompts used
- Ready to reference requirements document throughout project
- Committed to careful, methodical approach

**YOUR EVALUATION:**
✓ **What was good:**
- Set proper expectations and constraints
- Established accountability mechanism (prompt documentation)
- Created baseline for quality control

✓ **ACCEPTED** - This became the framework for all subsequent interactions

---

## Prompt 2: Data Generation Requirements

**PROMPT SENT (USER):**
```
"Git integration is done lets move to creating scripts for generating the data first. 
Data should be as per the requirements mentioned in the requirement doc, in the same format, 
schema and same data quality parameters. 
Also with the same count mentioned in requirement doc. 
Dont assume anything and dont hallucinate."
```

**AI RESPONSE SUMMARY:**
- Confirmed I would read requirements-analysis.md
- Verified all specifications:
  - Customers: 10,000 rows with 7 columns
  - Orders: 100,000 rows with 9 columns
  - Products: 500 rows with 7 columns
- Confirmed intentional quality issues (~700 rows, ~0.6%):
  - Customers: 50 NULL emails, 10 duplicates
  - Orders: 100 NULL customer_id, 200 NULL product_id, 50 invalid FKs, 30 invalid FKs, 20 duplicates
  - Products: Clean (0 issues)
- Outlined generation approach

**YOUR EVALUATION:**
✓ **What was good:**
- Confirmed exact specifications from requirements
- Listed all quality issues explicitly
- Row counts verified
- No assumptions made

✓ **ACCEPTED** - Provided foundation for data generation script

---

## Prompt 3: Data Generation Script with Faker

**PROMPT SENT (USER):**
```
"Design a sample data generator for Databricks. I need to create 3 CSVs with realistic data 
and intentional quality issues. 
Here's the schema: [requirements from doc]
Here are the issues I need: [quality issues from doc]"
```

**AI RESPONSE SUMMARY:**
- Generated Python script using Faker library
- Created realistic customer names, emails, addresses
- Generated dates with proper ranges
- Added intentional quality issues as CSV output
- Included comments explaining quality issue placement
- Used random.seed() for reproducibility
- Output: 3 CSV files with specified schemas

**YOUR EVALUATION:**
✓ **What was good:**
- Realistic data patterns
- All fields populated correctly
- Quality issues intentionally placed
- Seed-based reproducibility

✗ **What needed fixing:**
- Faker library dependency issue (SSL certificate errors)
- Installation problematic in environment
- Better if no external dependencies

**What you changed:**
- Rewrote without Faker library
- Used only Python standard library (random, string, datetime, csv)
- Kept same data patterns and quality issues
- Result: generate_sample_data_no_dependencies.py
- Why: Works immediately without dependency resolution

---

## Prompt 4: Data Generation with No Dependencies

**PROMPT SENT (USER):**
```
"I got SSL errors with Faker. Can you rewrite the data generator using ONLY 
Python standard library? No external dependencies. 
Keep the same data patterns, quality issues, row counts, and reproducibility (seed=42)."
```

**AI RESPONSE SUMMARY:**
- Rewrote entire script using only:
  - random (for randomization)
  - string (for name components)
  - datetime (for date generation)
  - csv (for file writing)
- Maintained all quality issues
- Used seed(42) for reproducibility
- Created same CSV output format
- Included detailed comments

**YOUR EVALUATION:**
✓ **What was good:**
- No dependencies needed
- Same data quality and patterns
- Reproducible (seed 42)
- Faster execution
- Row counts exact (10,000, 100,000, 500)

✓ **ACCEPTED** - This became generate_sample_data_no_dependencies.py

**File:** `/src/data_generation/generate_sample_data_no_dependencies.py`

---

## Prompt 5: Data Validation & Verification

**PROMPT SENT (USER):**
```
"Verify the generated data:
1. Do row counts match? (10,000 customers, 100,000 orders, 500 products)
2. Are quality issues present? (50 NULL emails, 10 duplicate IDs, etc.)
3. Are all fields populated correctly?
4. Is the data reproducible?"
```

**AI RESPONSE SUMMARY:**
- Created verification script
- Checked row counts using wc -l
- Sampled files to verify data format
- Confirmed quality issues by counting patterns
- Verified seed reproducibility (same output on multiple runs)
- Created validation report

**YOUR EVALUATION:**
✓ **ACCEPTED** - Verified data quality and correctness

**Verification Results:**
- ✅ customers.csv: 10,001 lines (10,000 + 1 header)
- ✅ orders.csv: 100,001 lines
- ✅ products.csv: 501 lines
- ✅ Quality issues confirmed (~460)
- ✅ All fields populated
- ✅ Reproducible with seed(42)

---

## Summary: Data Generation Phase

**Total Prompts:** 5  
**Iterations:** 1 (Faker → No-dependencies rewrite)  
**Rejections:** 0  
**Final Deliverable:** generate_sample_data_no_dependencies.py  

**Key Decisions:**
- ✓ Accepted: No-dependency approach (solved SSL issues)
- ✓ Accepted: Seed-based reproducibility
- ✓ Accepted: Standard library only
- ✗ Rejected: Faker-based approach (dependency issues)

**Data Quality:**
- 10,000 customers with 50 NULL emails + 10 duplicates
- 100,000 orders with multiple quality issues
- 500 products (clean)
- Total intentional issues: ~460 rows (~0.4%)
- All intentional and necessary for quality check testing

**Status:** ✅ Phase 2 Complete

