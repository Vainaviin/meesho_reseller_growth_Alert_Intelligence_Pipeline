import csv
import os
import sys
from typing import Dict, List, Any

# Allow importing part2_engine when this file is executed directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from part2_engine.growth_engine import (
    validate_feed,
    mom_growth,
    is_flagged,
)


TOP_N = 3
THRESHOLD = 8.0


def load_feed(csv_path: str) -> List[Dict[str, str]]:
    """Load a monthly category revenue CSV."""
    with open(csv_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def get_category_revenue(
    rows: List[Dict[str, str]]
) -> Dict[str, float]:
    """Convert category revenue rows into a dictionary."""
    result = {}

    for row in rows:
        category = row["category"].strip()
        revenue = float(row["revenue"])
        result[category] = revenue

    return result


def fill_prompt_template(
    category: str,
    previous_revenue: float,
    current_revenue: float,
    mom_pct: float,
    month: str,
    prev_month: str,
) -> str:
    """
    Part 3 prompt-pack template-fill logic.

    Only supplied values are used in the message.
    No additional business numbers are invented.
    """

    direction = "increase" if mom_pct > 0 else "decrease"

    message = (
        f"Context: {category} revenue changed from "
        f"{previous_revenue:.2f} in {prev_month} to "
        f"{current_revenue:.2f} in {month}. "
        f"Fact: The MoM revenue {direction} is {mom_pct}%. "
        f"Implication: Review {category} performance for {month} "
        f"against {prev_month} before taking action."
    )

    return message


def run(
    month: str,
    previous_month_csv: str,
    current_month_csv: str
) -> Dict[str, Any]:

    # ---------------------------------------------------------
    # 1. Validate current feed
    # ---------------------------------------------------------

    validation_status, validation_errors = validate_feed(
        current_month_csv
    )

    # ---------------------------------------------------------
    # 2. HARD STOP if feed is invalid
    # ---------------------------------------------------------

    if not validation_status:
        return {
            "run_month": month,
            "validation_status": "invalid",
            "validation_errors": validation_errors,
            "flagged_categories": [],
            "suppressed_categories": [],
            "escalated_categories": [],
            "action_taken": "hard_stop",
        }

    # ---------------------------------------------------------
    # 3. Load valid feeds
    # ---------------------------------------------------------

    previous_rows = load_feed(previous_month_csv)
    current_rows = load_feed(current_month_csv)

    previous_revenue = get_category_revenue(previous_rows)
    current_revenue = get_category_revenue(current_rows)

    # Extract previous month from the previous CSV.
    prev_month = ""

    if previous_rows:
        prev_month = previous_rows[0].get("month", "")

    # ---------------------------------------------------------
    # 4. Calculate MoM and classify every category
    # ---------------------------------------------------------

    flagged = []
    escalated = []

    for category, current_value in current_revenue.items():

        if category not in previous_revenue:
            continue

        previous_value = previous_revenue[category]

        mom_pct = mom_growth(
            previous_value,
            current_value
        )

        status = is_flagged(
            mom_pct,
            THRESHOLD
        )

        if status == "flagged":

            flagged.append({
                "category": category,
                "mom_pct": mom_pct,
                "previous_revenue": previous_value,
                "current_revenue": current_value,
            })

        elif status == "escalate_exact_boundary":

            escalated.append(category)

    # ---------------------------------------------------------
    # 5. Sort flagged categories by absolute MoM descending
    # ---------------------------------------------------------

    flagged.sort(
        key=lambda item: abs(item["mom_pct"]),
        reverse=True
    )

    # ---------------------------------------------------------
    # 6. Draft only top 3
    # ---------------------------------------------------------

    drafted_categories = flagged[:TOP_N]
    suppressed_categories = flagged[TOP_N:]

    final_flagged_categories = []

    for item in drafted_categories:

        message = fill_prompt_template(
            category=item["category"],
            previous_revenue=item["previous_revenue"],
            current_revenue=item["current_revenue"],
            mom_pct=item["mom_pct"],
            month=month,
            prev_month=prev_month,
        )

        final_flagged_categories.append({
            "category": item["category"],
            "mom_pct": item["mom_pct"],
            "previous_revenue": item["previous_revenue"],
            "current_revenue": item["current_revenue"],
            "drafted": True,
            "message": message,
        })

    # ---------------------------------------------------------
    # 7. Suppress remaining flagged categories
    # ---------------------------------------------------------

    suppressed_names = [
        item["category"]
        for item in suppressed_categories
    ]

    # ---------------------------------------------------------
    # 7b. Exact boundary categories are separate
    # ---------------------------------------------------------

    # They are intentionally not included in flagged or suppressed.

    # ---------------------------------------------------------
    # 8. Emit structured result
    # ---------------------------------------------------------

    return {
        "run_month": month,
        "validation_status": "valid",
        "validation_errors": [],
        "flagged_categories": final_flagged_categories,
        "suppressed_categories": suppressed_names,
        "escalated_categories": escalated,
        "action_taken": "drafted_and_held_for_approval",
    }


if __name__ == "__main__":

    import json
    import argparse

    parser = argparse.ArgumentParser(
        description="Meesho mock monitoring agent"
    )

    parser.add_argument(
        "--month",
        required=True
    )

    parser.add_argument(
        "--previous",
        required=True
    )

    parser.add_argument(
        "--current",
        required=True
    )

    args = parser.parse_args()

    result = run(
        month=args.month,
        previous_month_csv=args.previous,
        current_month_csv=args.current,
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )