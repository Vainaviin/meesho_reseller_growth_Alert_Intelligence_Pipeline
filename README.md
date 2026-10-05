# Meesho Reseller Growth & Alert Intelligence Pipeline

An end-to-end monthly reseller operations monitoring pipeline that combines **SQL analytics, Python validation and growth detection, deterministic AI-style narrative generation, and a guarded mock agent workflow**.

The pipeline is designed to identify significant month-on-month category revenue movements, generate controlled stakeholder narratives, suppress notification flooding, and hold all drafted messages for human approval.

---

## Project Workflow

```text
Seeded Dataset
      ↓
Part 1 — SQL Business Query Engine
      ↓
Part 2 — Python Guardrail & Growth-Detection Engine
      ↓
Part 3 — Reliable AI Narrative & Prompt Pack
      ↓
Part 4 — Agentic Workflow + Mock Agent Runner
      ↓
Human Review / Approval
```

---

# Repository Structure

```text
meesho-reseller-growth-alert/
│
├── data/
│   ├── generate_dataset.py
│   ├── resellers.csv
│   ├── orders.csv
│   └── meesho_reseller.db
│
├── part1_sql/
│   ├── queries.sql
│   ├── run_queries.py
│   ├── output/
│      ├── monthly_category_revenue.csv
│      ├── region_revenue.csv
│      ├── top_resellers.csv
│      ├── inactive_resellers.csv
│      ├── left_join_count_demo.csv
│      └── june_aov.csv
│  
│
├── part2_engine/
│   ├── growth_engine.py
│   ├── test_growth_engine.py
│   └── fixtures/
│       ├── corrupted_feed.csv
│       └── monthly_category_revenue.csv
│
├── part3_narrative/
│   ├── prompt_pack.md
│   ├── narrative_report.md
│   ├── masking.py
│   └── test_masking.py
│
├── part4_agent/
│   ├── agent_spec.md
│   ├── mock_agent_runner.py      
│
└── README.md
```

---

# Requirements

* Python 3.8+
* SQLite
* `pytest` is optional if the tests are executed through pytest.

The core pipeline uses only Python's standard library and SQLite.

No paid services or external AI APIs are required.

---

# 1. Regenerate the Dataset

The dataset is generated using the provided deterministic dataset generator.

From the repository root:

```bash
python data/generate_dataset.py
```

This creates:

```text
data/resellers.csv
data/orders.csv
data/meesho_reseller.db
```

The dataset uses a fixed random seed, so regeneration produces the same dataset required by the project.

---

# 2. Run Part 1 — SQL Business Query Engine

Part 1 calculates the verified business metrics from the SQLite database.

Run:

```bash
python part1_sql/run_queries.py
```

The generated outputs are written to:

```text
part1_sql/output/
```

Important output:

```text
monthly_category_revenue.csv
```

This file contains the monthly revenue by category and is the primary verified revenue feed passed into Part 2.

Other Part 1 outputs include:

```text
region_revenue.csv
top_resellers.csv
inactive_resellers.csv
left_join_count_demo.csv
june_aov.csv
```

Part 1 therefore establishes the **source-of-truth business numbers before any narrative or agent processing occurs**.

---

# 3. Run Part 2 — Guardrail & Growth Detection Engine

Part 2 provides three reusable functions:

```python
validate_feed()
mom_growth()
is_flagged()
```

Run the tests:

```bash
python part2_engine/test_growth_engine.py
```

Expected:

```text
All Part 2 tests passed.
```

Part 2 validates the Part 1 monthly feed before calculating growth.

The threshold is:

```text
8.0%
```

Classification:

```text
abs(MoM) > 8%   → flagged
abs(MoM) < 8%   → not_flagged
abs(MoM) = 8%   → escalate_exact_boundary
```

The exact boundary is intentionally treated separately so that an 8.0% movement is never silently treated as either flagged or not flagged.

---

# 4. Run Part 3 — Reliable AI Narrative Layer

Part 3 contains:

```text
part3_narrative/prompt_pack.md
part3_narrative/narrative_report.md
part3_narrative/masking.py
```

The prompt pack defines a reusable:

```text
Trigger
Input List
Prompt
Checklist
```

structure for converting a verified flagged category into a stakeholder update.

The worked narratives use the actual Part 1/Part 2 numbers for:

```text
May Ethnic Wear   → +77.1%
June Ethnic Wear  → -58.74%
```

The narrative follows:

```text
Context
   ↓
Insight — Fact
   ↓
Implication — Hypothesis when applicable
```

No external LLM or API is required.

### Run masking tests

```bash
python part3_narrative/test_masking.py
```

Expected:

```text
All Part 3 masking tests passed.
```

Raw reseller names are not allowed in external-facing narratives.

For example:

```text
RS019 → ALIAS-19
RS006 → ALIAS-06
```

---

# 5. Run Part 4 — Agentic Workflow + Mock Agent

Part 4 integrates Parts 2 and 3 into one guarded workflow.

The runner imports these functions directly from Part 2:

```python
from part2_engine.growth_engine import (
    validate_feed,
    mom_growth,
    is_flagged,
)
```

They are reused without re-implementation.

Part 4 also uses the deterministic Part 3 narrative template-fill logic.

---

## May Scenario — April → May

Run:

```bash
python part4_agent/mock_agent_runner.py May part4_agent/fixtures/april.csv part4_agent/fixtures/may.csv
```

Expected flagged order:

```text
1. Ethnic Wear              77.1%
2. Western Wear            -23.6%
3. Kids Wear              -23.48%
```

Expected suppressed categories:

```text
Home & Kitchen
Beauty & Personal Care
```

Only the top three flagged categories receive drafted messages.

The messages are:

```text
drafted_and_held_for_approval
```

They are never automatically sent.

---

## June Scenario — May → June

Run:

```bash
python part4_agent/mock_agent_runner.py June part4_agent/fixtures/may.csv part4_agent/fixtures/june.csv
```

Expected drafted order:

```text
1. Ethnic Wear            -58.74%
2. Home & Kitchen           42.59%
3. Kids Wear                23.9%
```

Expected suppressed category:

```text
Western Wear
```

Beauty & Personal Care:

```text
5.67%
```

is `not_flagged` and therefore does not appear in either list.

---

## Corrupted Feed — Hard Stop

Run:

```bash
python part4_agent/mock_agent_runner.py June part4_agent/fixtures/may.csv part2_engine/fixtures/corrupted_feed.csv
```

Expected result:

```text
validation_status = invalid
action_taken = hard_stop
```

The three validation errors are surfaced.

No MoM calculation is performed.

No messages are drafted.

No categories are suppressed.

---

# Structured Agent Output

Every Part 4 run produces exactly one JSON object containing:

```text
run_month
validation_status
validation_errors
flagged_categories
suppressed_categories
escalated_categories
action_taken
```

A successful run uses:

```text
action_taken = drafted_and_held_for_approval
```

An invalid feed uses:

```text
action_taken = hard_stop
```

Every drafted message contains only numbers traceable to the verified Part 1/Part 2 data.

---

# Zero API Keys Required

The **entire pipeline runs with zero API keys set**.

No:

```text
OpenAI API key
Grok/Groq API key
Gemini API key
Anthropic API key
Azure API key
AWS credentials
Gmail credentials
SMTP credentials
```

are required.

Part 3 uses a **deterministic prompt-pack/template-fill approach**, and Part 4 uses a **mock agent runner**.

There are:

```text
No external LLM calls
No network calls
No email sending
No paid API
No account-gated service
```

The project can therefore be executed locally using the repository files and Python/SQLite only.

---

# Workflow Pattern Mapping

## Part 1 → Compute

**Part 1 — SQL Business Query Engine**

Implements the **Compute / Source-of-Truth** pattern.

The system first calculates real business numbers from the seeded SQLite dataset before any downstream interpretation happens.

```text
Orders + Resellers
       ↓
SQL
       ↓
Verified Business Metrics
```

---

## Part 1 → Part 2 → Handoff

Part 1 → Part 2 mirrors the **"compute real numbers via SQL first, then hand off"** order of operations.

Part 1 produces:

```text
monthly_category_revenue.csv
```

Part 2 consumes that verified feed and applies validation and growth-detection guardrails.

```text
Part 1 Verified Feed
       ↓
Part 2 Validation
       ↓
MoM Calculation
       ↓
Flag Classification
```

---

## Part 3 → Report Draft

**Part 3 — Reliable AI Narrative Layer**

Implements the **Report Draft / Controlled Narrative** pattern.

Verified numbers are transformed into a stakeholder-friendly:

```text
Context
   ↓
Insight
   ↓
Implication
```

narrative while preventing unsupported numerical claims and raw reseller-name leakage.

---

## Part 4 → Agentic Workflow

**Part 4 — Agentic Workflow + Mock Agent Runner**

Implements an **Intake → Summary → Report Draft → Validate → Human Approval** reporting flow.

```text
Intake
  ↓
Validate Feed
  ↓
Calculate MoM
  ↓
Classify
  ↓
Prioritize
  ↓
Draft Top 3
  ↓
Suppress Remaining
  ↓
Escalate Exact Boundary
  ↓
Validate / Hold
  ↓
Human Approval
```

The agent never automatically sends a message.

---

# End-to-End Execution Order

For a complete clean run:

```bash
python data/generate_dataset.py
```

Then:

```bash
python part1_sql/run_queries.py
```

Then:

```bash
python part2_engine/test_growth_engine.py
```

Then:

```bash
python part3_narrative/test_masking.py
```

Then May:

```bash
python part4_agent/mock_agent_runner.py May part4_agent/fixtures/april.csv part4_agent/fixtures/may.csv
```

Then June:

```bash
python part4_agent/mock_agent_runner.py June part4_agent/fixtures/may.csv part4_agent/fixtures/june.csv
```

Finally, test the Hard Stop:

```bash
python part4_agent/mock_agent_runner.py June part4_agent/fixtures/may.csv part2_engine/fixtures/corrupted_feed.csv
```

---

# End-to-End Design Principle

The project deliberately separates responsibilities:

```text
Part 1
Business truth
      ↓
Part 2
Validation + calculation + classification
      ↓
Part 3
Controlled stakeholder narrative
      ↓
Part 4
Planning + prioritization + guardrails
      ↓
Human
Final approval
```

This prevents the narrative or agent layer from becoming the source of truth.

**SQL computes the numbers, Python verifies and classifies them, the narrative layer explains them, and the agent workflow controls what reaches human review.**
