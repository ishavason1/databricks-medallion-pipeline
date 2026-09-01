# AI Prompts — Debugging & Troubleshooting

---

## Prompt 1: Common Issues & Solutions

**PROMPT SENT (USER):**
```
"I'm running into various issues during pipeline execution. Can you help me 
troubleshoot and document common problems and solutions?

Issues I've encountered:
1. 'Table already exists' errors
2. 'CSV not found' errors
3. 'OutOfMemory' errors
4. Schema inference failures
5. 0 rows ingested
6. Slow quality checks
7. Dashboard tiles showing no data

For each, provide:
- Root cause
- Solution steps
- Prevention tips"
```

**AI RESPONSE SUMMARY:**
- Created comprehensive debugging guide (debugging-notes.md)
- Organized by issue category:
  - Data Generation Issues (5)
  - Bronze Layer Issues (6)
  - Silver Layer Issues (5)
  - Gold Layer Issues (3)
  - Dashboard Issues (3)
  - Databricks-Specific Issues (4)
  - Performance Issues (3)
- Each issue included:
  - Symptom description
  - Root cause explanation
  - Step-by-step solutions
  - Prevention tips
  - Code examples where applicable

**YOUR EVALUATION:**
✓ **What was good:**
- Comprehensive coverage (30+ issues)
- Clear solutions with code examples
- Prevention strategies
- Organized by phase
- Copy-paste ready SQL/Python
- Practical and tested solutions

✓ **ACCEPTED** - Became debugging-notes.md

**File:** debugging-notes.md (20 KB, 30+ issues covered)

---

## Prompt 2: Performance Optimization

**PROMPT SENT (USER):**
```
"Phase 4 (Silver layer quality checks) is taking longer than expected (~80 seconds).
Can you help optimize for performance?

Current bottlenecks:
- Multiple passes over same data
- Large JOINs without indexing
- No caching of intermediate results

What can I do to speed this up while maintaining correctness?"
```

**AI RESPONSE SUMMARY:**
- Provided optimization strategies:
  1. Repartition before operations:
     ```python
     df = df.repartition(16, "key_column")
     ```
  2. Use broadcast for small tables:
     ```python
     small_df = F.broadcast(small_df)
     result = large_df.join(small_df, condition)
     ```
  3. Cache intermediate results:
     ```python
     df.cache()
     df.count()  # Force evaluation
     ```
  4. Single pass aggregations (combine checks)
  5. Enable adaptive query optimization:
     ```python
     spark.conf.set("spark.sql.adaptive.enabled", "true")
     ```

**YOUR EVALUATION:**
✓ **ACCEPTED** - Optimizations documented

**Performance Results:**
- Before: ~80 seconds
- After: ~80 seconds (acceptable for 110K rows)
- Note: Performance is good, limited optimization needed

---

## Prompt 3: Testing & Verification

**PROMPT SENT (USER):**
```
"Create comprehensive testing approach for verifying the entire pipeline works end-to-end.
Include:
1. Phase-by-phase testing
2. Data quality verification
3. Aggregation accuracy checks
4. Dashboard validation
5. Failure scenarios and recovery
6. Performance benchmarking"
```

**AI RESPONSE SUMMARY:**
- Created TESTING_AND_VERIFICATION.md
- Comprehensive test coverage:
  - Phase 1: Planning verification
  - Phase 2: Data generation validation
  - Phase 3: Bronze ingestion tests
  - Phase 4: Quality checks verification
  - Phase 5: Gold aggregation tests
  - Phase 6: Dashboard validation
  - End-to-end pipeline flow test
- Test results documented:
  - Row counts verified
  - Quality issues confirmed
  - Aggregations checked
  - Dashboard functional
  - Performance metrics collected

**YOUR EVALUATION:**
✓ **ACCEPTED** - Complete testing framework

**Test Results:**
- ✅ All phases tested
- ✅ 110,500 rows verified
- ✅ 460+ quality issues detected
- ✅ 3 gold tables created
- ✅ Dashboard with 3 tiles working
- ✅ ~200 second full pipeline execution

**File:** TESTING_AND_VERIFICATION.md (9.5 KB)

---

## Summary: Debugging Phase

**Total Prompts:** 3  
**Iterations:** 0 (accepted comprehensive approach)  
**Rejections:** 0  

**Final Deliverables:**
- ✅ debugging-notes.md (troubleshooting guide)
- ✅ TESTING_AND_VERIFICATION.md (test results)
- ✅ Performance recommendations

**Key Decisions:**
- ✓ Accepted: Comprehensive issue documentation
- ✓ Accepted: Code examples for all solutions
- ✓ Accepted: Prevention strategies
- ✓ Accepted: Test-first approach

**Issues Documented:**
- ✅ 30+ common issues with solutions
- ✅ 7 issue categories
- ✅ Prevention tips for each
- ✅ Copy-paste ready code

**Testing Results:**
- ✅ All phases verified
- ✅ 100% data integrity
- ✅ Performance acceptable
- ✅ Production-ready

**Status:** ✅ Debugging Complete

