# Reusable Prompt Pack — Reseller Growth Narrative

## Trigger

Start this prompt when a category's `is_flagged` result is:

`"flagged"`

The narrative should be generated only after the Part 2 feed validation has passed and the verified revenue values and MoM percentage are available.

---

## Input list

The prompt requires these verified placeholder variables:

- `{category}` — category name
- `{previous_revenue}` — previous month's revenue
- `{current_revenue}` — current month's revenue
- `{mom_pct}` — Month-on-Month percentage
- `{month}` — current month
- `{prev_month}` — previous month
- `{threshold}` — configured significance threshold
- `{direction}` — growth direction, such as growth or decline

Only supplied and verified values may be used in the narrative.

---

## Prompt

You are preparing a concise stakeholder update for a regional manager.

Create a narrative using the following structure:

### Context

Explain what `{category}` revenue is being measured and explicitly name the comparison period as `{month}` versus `{prev_month}`.

### Insight

State the verified revenue movement:

- Previous revenue: `{previous_revenue}`
- Current revenue: `{current_revenue}`
- MoM change: `{mom_pct}%`
- Direction: `{direction}`

Label this statement explicitly as **Fact**.

### Implication

Give one specific and actionable next step for the regional manager.

If you suggest a possible reason for the movement, label it explicitly as a **Hypothesis** because the supplied data does not prove causation.

Do not invent any numbers, names, causes, orders, customers, products, regions, or other facts.

Never state a number that is not one of the supplied placeholder values.

Do not change the supplied percentage or revenue values.

Do not claim that the movement was caused by a particular factor unless that factor is explicitly supplied as verified input.

Keep the update concise and suitable for a regional manager.

---

## Checklist

Before using the generated narrative, verify all of the following:

1. **Number validation:** Every number in the narrative exactly matches a supplied verified placeholder value.

2. **Period validation:** The narrative explicitly names `{month}` versus `{prev_month}` and does not change the reporting period.

3. **Fact validation:** Measured results are explicitly labeled as **Fact**.

4. **Hypothesis validation:** Any proposed cause or explanation is explicitly labeled as **Hypothesis**.

5. **Actionability:** The recommendation identifies a specific next action rather than using vague wording such as "look into it."

6. **Category validation:** The category name exactly matches the verified category.

7. **No fabricated claims:** The narrative contains no unsupported causes, numbers, customers, products, or performance claims.

8. **Privacy validation:** If a reseller is referenced, only its approved alias and region may be used; the raw reseller name must not appear.

9. **Feed validation:** The underlying Part 1/Part 2 input must have passed `validate_feed()` before the narrative is accepted.

10. **Human review:** Any `"escalate_exact_boundary"` result must be held for human review rather than automatically narrated as flagged or not flagged.