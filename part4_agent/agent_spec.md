# Part 4 — Agentic Workflow Specification

## 4.1 Agent Specification

### Goal

Keep Meesho category managers informed of any category whose month-on-month revenue moves beyond the 8% threshold, with a human approving every drafted message before it is considered sent.

### Tools

The monitoring agent uses the following functions from Parts 2 and 3:

* `validate_feed()` — validates the monthly revenue CSV before processing.
* `mom_growth()` — calculates month-on-month revenue growth.
* `is_flagged()` — determines whether the MoM percentage is flagged, not flagged, or at the exact threshold boundary.
* Part 3 prompt-pack template-fill logic — creates the narrative message for flagged categories.

The Part 2 functions are imported and reused without re-implementing their logic.

### Memory / State

The agent requires:

* Previous month's revenue for each category.
* Current month's revenue for each category.
* Previous month name.
* Current run month.
* MoM percentage for each category.
* Flag status for each category.
* Categories suppressed because they exceed the top-3 drafting limit.
* Categories escalated because they fall exactly on the 8% boundary.

The previous month's revenue acts as the state required to calculate the next month's MoM growth.

### Planner

The agent follows these ordered subtasks:

1. Load the monthly revenue feed and run `validate_feed`.
2. If validation fails, perform a **Hard Stop** and report all validation errors.
3. If validation succeeds, calculate `mom_growth` for every category against the previous month.
4. Run `is_flagged` for every category.
5. Sort flagged categories by `abs(mom_pct)` in descending order.
6. Draft messages using the Part 3 template for at most the top 3 flagged categories.
7. Log remaining flagged categories as `suppressed, review manually` without drafting messages.
   7b. Separately log exact-boundary categories in `escalated_categories` without drafting messages.
8. Emit one structured JSON object for the run.

### Feedback Loop

Every drafted message is held for human approval.

The mock runner does **not** send email, call Gmail, call SMTP, or make any external network request.

The output records:

`action_taken = "drafted_and_held_for_approval"`

This means the messages have been drafted but have not been sent.

---

## Guardrails

### Input Guardrail

`validate_feed()` must pass before any MoM calculation or message drafting occurs.

If validation returns `False`, the agent performs a **Hard Stop**.

No MoM calculation is attempted on invalid data.

### Action Guardrail

No message is automatically sent.

The agent only:

1. Creates a draft.
2. Holds the draft for human approval.

There is no email or notification integration in this implementation.

### Output Guardrail

Every number in a drafted message must trace back to a Part 1 or Part 2 value.

The agent must not invent:

* revenue values,
* percentages,
* order counts,
* dates,
* thresholds,
* business metrics,
* unsupported causes.

---

## Success and Error Conditions

### Success

A run is successful when:

* The feed passes validation.
* MoM calculations are completed.
* Flagged categories are correctly identified.
* At most three flagged categories receive drafts.
* Additional flagged categories are suppressed.
* Exact-boundary categories are separately escalated.
* Every drafted number is traceable to the supplied data.

If no category crosses the threshold, the run is still successful with zero drafts.

### Error

If `validate_feed()` returns `False`:

* `validation_status = "invalid"`
* `action_taken = "hard_stop"`
* Validation errors are surfaced.
* `flagged_categories = []`
* `suppressed_categories = []`
* No MoM calculation is attempted.

---

## Given-When-Then Specifications

### Scenario 1 — Ethnic Wear Growth

**Given** April Ethnic Wear revenue is `104520.77` and May Ethnic Wear revenue is `185107.61`

**When** the agent calculates MoM growth

**Then** the result is `77.1%` and the category is flagged.

### Scenario 2 — Beauty & Personal Care

**Given** May Beauty & Personal Care revenue is `35542.11` and June revenue is `37559.07`

**When** the agent calculates MoM growth

**Then** the result is `5.67%` and the category is `not_flagged`.

### Scenario 3 — Exact Boundary

**Given** previous revenue is `100000` and current revenue is `108000`

**When** the agent evaluates the MoM growth against the `8%` threshold

**Then** the result is exactly `8.0%` and the category is `escalate_exact_boundary`.

### Scenario 4 — Corrupted Feed

**Given** the current monthly feed contains a negative revenue, a missing category, and a missing revenue

**When** the agent runs `validate_feed`

**Then** validation fails, the agent performs a Hard Stop, and the three validation errors are surfaced without performing MoM calculations.

---

# 4.2 Ordered Subtasks

The planner executes the following sequence:

1. Load the monthly revenue feed and run `validate_feed`.
2. If invalid, Hard Stop and report errors.
3. If valid, calculate `mom_growth` for every category against the previous month.
4. Run `is_flagged` on every category.
5. Sort flagged categories by `abs(mom_pct)` descending.
6. Draft messages for at most the top 3 flagged categories.
7. Log remaining flagged categories as `suppressed, review manually`.
   7b. Log exact-boundary categories into `escalated_categories` without drafting.
8. Emit one structured JSON object per run.

The top-3 limit prevents notification flooding.

---

# 4.3 Structured JSON Output

Every run produces one object with these top-level keys:

```json
{
  "run_month": "May",
  "validation_status": "valid",
  "validation_errors": [],
  "flagged_categories": [],
  "suppressed_categories": [],
  "escalated_categories": [],
  "action_taken": "drafted_and_held_for_approval"
}
```

Each drafted flagged-category object contains:

```json
{
  "category": "Ethnic Wear",
  "mom_pct": 77.1,
  "previous_revenue": 104520.77,
  "current_revenue": 185107.61,
  "drafted": true,
  "message": "..."
}
```

For a flagged category that is suppressed:

```json
{
  "category": "Home & Kitchen",
  "mom_pct": -9.25,
  "previous_revenue": 100446.23,
  "current_revenue": 91152.57,
  "drafted": false
}
```

---

# 4.4 Mock Agent Runner

The implementation is provided in:

`part4_agent/mock_agent_runner.py`

The runner:

* imports Part 2's `growth_engine`,
* validates the current feed,
* calculates MoM,
* classifies categories,
* sorts flagged categories,
* drafts only the top three,
* suppresses additional flagged categories,
* separately tracks exact-boundary categories,
* returns the required JSON-compatible dictionary.

No external API, network call, Gmail integration, SMTP integration, or API key is used.
