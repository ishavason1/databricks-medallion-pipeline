# Tool Workflow: AI-Assisted Data Engineering

**Part A of Assignment - AI Workflow Foundation**  
**Status:** FRAMEWORK COMPLETE  
**Owner:** [Your Name]

---

## 1. AI Tool Overview

**Primary AI Tool:** Cursor / Claude (specify which)  
**Purpose:** Assist with design, code generation, validation, debugging across the entire data pipeline lifecycle

**Key Principle:** AI as collaborator, not autopilot. Understand, validate, and own every suggestion.

---

## 2. How You Provide Project Context to AI

### 2.1 Initial Context Setup

**What You'll Share:**
- Full requirements (from requirements-analysis.md)
- Data schema and relationships
- Medallion architecture design (from design-notes.md)
- Quality check definitions (from data-quality-strategy.md)
- Code structure and naming conventions

**Example Context Prompt:**
```
I'm building a Databricks medallion architecture pipeline.
Here's the structure:

DATA SCHEMA:
- customers.csv: 10,000 rows (customer_id, email, ...)
- orders.csv: 100,000 rows (order_id, customer_id, product_id, ...)
- products.csv: 500 rows (product_id, product_name, ...)

QUALITY CHECKS NEEDED:
1. Completeness: No NULLs in email, customer_id, product_id
2. Uniqueness: No duplicate rows (customer_id, order_id)
3. Referential Integrity: Foreign keys exist
4. Type Validation: Data types match schema

IMPLEMENTATION APPROACH:
- Bronze layer: Raw data ingestion, no transformations
- Silver layer: Add quality_check_result column, flag issues
- Gold layer: 3 aggregations on PASS rows only
- Filter data: WHERE quality_check_result = 'PASS'

Help me write [specific task] with this context.
```

### 2.2 Persistent Project Context

**How You'll Maintain Context:**
- Keep requirements and design documents available for reference
- Share relevant excerpts when asking for code help
- Remind AI of constraints (flag not delete, filter to PASS, etc.)
- Review AI's understanding before proceeding

**Anti-Pattern:**
```
"Generate Python code to read CSVs and create tables"  ❌
(AI doesn't know structure, quality checks, or constraints)

"I need PySpark code to read customers.csv (10K rows: customer_id INT, 
email STRING nullable, ...) and create bronze_customers Delta table 
with logging. No transformations. Here's the schema..."  ✅
(AI has full context)
```

---

## 3. Requirement Analysis & AI

**Your Role:** Understand the problem deeply

**AI's Role:** Help organize and clarify

**Workflow:**

1. **Read the assignment** (requirements-analysis.md created)
2. **Ask AI clarifying questions:**
   - "What are the key differences between Bronze/Silver/Gold layers?"
   - "Why flag rows instead of deleting them?"
   - "What does a good quality report look like?"
3. **Document assumptions** you make
4. **Create requirements-analysis.md** yourself (we did this together)

**Example:**
```
PROMPT: "Help me understand the medallion architecture pattern. 
Why do we flag data issues in Silver instead of cleaning them?"

AI's answer helps you understand trade-offs, not does the work for you.
```

---

## 4. Pipeline Design & AI

**Your Role:** Make architectural decisions

**AI's Role:** Validate and refine

**Workflow:**

1. **Create design sketch:** Bronze → Silver → Gold → Dashboard
2. **Ask AI:**
   - "Does this architecture make sense for this use case?"
   - "What are the pitfalls with this approach?"
   - "How should I structure the quality checks?"
3. **Review AI's suggestions** against requirements
4. **Iterate** until you're confident

**Example:**
```
PROMPT: "I'm using LEFT JOINs to detect orphan foreign keys. 
Will this catch all 50 invalid customer_id references in orders?"

AI validates your approach and suggests alternatives if needed.
```

---

## 5. Code Generation & Validation

**Your Role:** Review, understand, validate before using

**AI's Role:** Generate code based on your specifications

**Workflow:**

```
┌─────────────────────────────────────────────────────────┐
│ 1. PROMPT                                               │
│    "Write PySpark code to read customers.csv and..."    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. AI GENERATES CODE                                    │
│    (Python script with schema, error handling, etc.)    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. YOU REVIEW                                           │
│    ✓ Does it match the spec?                           │
│    ✓ Is it readable and commented?                     │
│    ✓ Are error cases handled?                          │
│    ✗ Does it do something unexpected?                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. TEST IN ENVIRONMENT                                 │
│    Run it. Does it work? Does output match expected?   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. ACCEPT, REFINE, OR REJECT                           │
│    Keep it / Ask for changes / Write it yourself       │
└─────────────────────────────────────────────────────────┘
```

**Critical:** Never copy-paste without understanding

---

## 6. Data Quality Validation & AI

**Your Role:** Verify that quality checks catch intended issues

**AI's Role:** Help design check logic

**Workflow:**

```
PROMPT: "I need a Completeness check for orders table.
Should catch: 100 NULL customer_ids, 200 NULL product_ids.
Write SQL that flags these rows with quality_check_result = 'FAIL'."

AI generates SQL → You test it → Verify it flags 300 rows → Accept
```

**Validation Steps:**
1. Generate SQL for check
2. Run on bronze_orders with intentional issues
3. Count rows: `SELECT COUNT(*) WHERE quality_check_result LIKE 'FAIL%'`
4. Verify count matches expected (~700 total)
5. Spot-check flagged rows to confirm they're actually bad

---

## 7. Testing & Debugging with AI

**Your Role:** Identify and diagnose issues

**AI's Role:** Suggest solutions

**Workflow:**

**Example 1: Code Error**
```
ERROR: "Table not found: bronze_customers"

PROMPT TO AI:
"I'm getting 'Table not found: bronze_customers' when running my 
Silver layer script. The Bronze script ran successfully. 
What's causing this?"

AI helps diagnose:
- Did Bronze script actually create the table?
- Is the database/catalog path correct?
- Is there a schema mismatch?
```

**Example 2: Logic Error**
```
ISSUE: Completeness check found 400 failures, expected 350

PROMPT TO AI:
"My Completeness check found 400 NULL rows, but I expected 350 
(50 emails + 100 customer_ids + 200 product_ids). 
What could explain the extra 50?"

AI helps diagnose:
- Are you checking the right table (customers vs orders)?
- Could rows have multiple NULLs (one row = 2 issues)?
- Are you counting duplicates separately?
```

---

## 8. AI for Testing & Verification

**Your Role:** Define test cases

**AI's Role:** Generate test code

**Workflow:**

```
PROMPT: "Generate tests to verify my quality checks work correctly:
1. Verify Completeness check finds 350 NULLs (50 email + 100 customer_id + 200 product_id)
2. Verify Uniqueness check finds 30 duplicates (10 customer + 20 order)
3. Verify Referential Integrity finds 80 orphans (50 customer + 30 product)
Write Python/PySpark test code."

AI generates assertions → You run tests → Verify all pass → Accept
```

---

## 9. Documentation & AI

**Your Role:** Write the narrative (what you learned)

**AI's Role:** Help with formatting and structure

**Workflow:**

```
PROMPT: "I struggled with the referential integrity check because I 
forgot to handle NULL keys. The LEFT JOIN was correct, but I wasn't 
checking 'AND o.customer_id IS NOT NULL'. Help me write this up 
as a debugging note."

AI helps you articulate the lesson clearly
```

---

## 10. How You'll Avoid Common AI Pitfalls

### Pitfall 1: Blindly Copying Code
**Prevention:** Always test code before using it. Run in a sandbox. Verify output.

### Pitfall 2: Forgetting to Specify Constraints
**Prevention:** Include constraints in every prompt (flag not delete, filter to PASS, etc.)

### Pitfall 3: Not Validating AI's Understanding
**Prevention:** Ask "summarize what you understand about my project" before asking for code

### Pitfall 4: Using AI Without Thinking
**Prevention:** Maintain a "prompt journal" — track what you asked and what you learned

### Pitfall 5: Assuming AI Knows Best
**Prevention:** You know the requirements better. Disagree with AI when needed. Test.

---

## 11. Information You WON'T Share with AI

**PII or Sensitive Data:**
- Real customer names, emails, phone numbers
- Real credit card or financial data
- Real order history

**What You Will Do Instead:**
- Use fake data (Faker library)
- Use dummy/placeholder values
- Explain the structure without sharing real values

**Example:**
```
PROMPT: "I need to generate sample customer data with 10,000 rows. 
Each row has customer_id (INT), customer_name (STRING, realistic names), 
email (STRING, valid format), ..."

AI generates fake data with Faker library ✓
NOT: "Here are our 10,000 real customers, generate quality issues" ✗
```

---

## 12. AI Prompting Patterns That Work Well

### Pattern 1: Context + Specific Request
```
GOOD: "I have a customers table with [schema]. I need to check for 
duplicate customer_ids. Write SQL using ROW_NUMBER()..."

BAD: "Write SQL to find duplicates"
```

### Pattern 2: Example + Constraint
```
GOOD: "Generate 100 orders with these quality issues:
- 10 with NULL customer_id
- 5 with invalid customer_id (not in customers table)
All other fields should be realistic. Use Faker library."

BAD: "Generate sample orders"
```

### Pattern 3: Iteration Request
```
GOOD: "Write the completeness check. Then, if it works, write 
the uniqueness check. For each, I'll test before we move forward."

BAD: "Write all quality checks at once"
```

### Pattern 4: Validation Request
```
GOOD: "Write the code. Also include: logging statements, 
error handling for missing columns, and comments explaining 
the WHERE clause."

BAD: "Write the code"
```

---

## 13. How You'll Reuse This Workflow in Production

**Lessons Learned:**
1. **AI is best for:** Code generation from clear specs, refactoring, testing frameworks
2. **AI is NOT for:** Problem definition, architecture decisions, validation
3. **Best practice:** Use AI to accelerate good patterns you understand, not to make decisions

**Production Workflow:**
```
DESIGN → SPEC → AI CODE GENERATION → TEST → REVIEW → DEPLOY

AI helps with the middle steps; you do design, testing, and decisions.
```

**Reusable Templates:**
- Quality check SQL patterns (save for next source)
- PySpark ingestion patterns (reuse for new tables)
- Aggregation SQL templates (adapt for new metrics)
- Test frameworks (extend for new checks)

---

## 14. AI Tools & Specific Features You'll Use

### Cursor (if using Cursor)
- **File context:** Keep requirements and design open
- **@-mentions:** Reference files in prompts (@requirements-analysis.md)
- **Inline editing:** Generate code directly in files
- **Commands:** Use /explain, /doc, /test commands
- **Chat history:** Review prompts and responses later

### Claude (if using Claude)
- **Long context:** Paste full requirements
- **Artifacts:** Use for file creation and editing
- **Web search:** Ask about latest PySpark/Databricks practices
- **Reasoning:** Chain-of-thought for complex logic

---

## 15. Documenting Your AI Interactions

**You'll track:**
1. Prompt sent to AI
2. AI's response (summary or excerpt)
3. What you accepted (and why)
4. What you changed (and why)
5. What you rejected (and why)

**File:** ai-prompts/{phase}.md

**Example Entry:**
```
## Prompt 1: Bronze Ingestion Script

**PROMPT SENT:**
"Write PySpark code to read customers.csv and create bronze_customers 
Delta table. [include schema and requirements]"

**AI RESPONSE SUMMARY:**
Generated Python script with:
- spark.read.csv() to read file
- Explicit schema definition
- Logging statements
- Error handling

**YOUR EVALUATION:**
✓ ACCEPTED - Script works as expected
⚠ FIXED - Added comments for clarity
✗ REJECTED - [if anything]

**DECISION:** Use with minor comment additions
```

---

## 16. Summary: Your AI Workflow Mindset

| Mindset | Example |
|---------|---------|
| AI as collaborator | "Help me think through this design" |
| You as decision-maker | "I'll decide which approach is better" |
| AI for acceleration | "Generate the boilerplate code" |
| You for validation | "I'll test and verify it works" |
| AI for explanation | "Explain why left join is better here" |
| You for ownership | "I understand the code and stand behind it" |

---

**Document Status:** ✅ FRAMEWORK COMPLETE  
**Next Steps:** Fill in specific AI interactions as you work through Phases 2-7  
**Owner:** [Your Name]
