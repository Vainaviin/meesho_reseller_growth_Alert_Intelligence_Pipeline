import csv
from typing import Tuple, List


def mom_growth(previous: float, current: float) -> float:
    """
    Calculate Month-on-Month growth percentage.
    """
    return round((current - previous) / previous * 100, 2)


def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
    """
    Classify the MoM percentage.
    """

    if abs(mom_pct) > threshold:
        return "flagged"

    elif abs(mom_pct) < threshold:
        return "not_flagged"

    else:
        return "escalate_exact_boundary"


def validate_feed(csv_path: str) -> Tuple[bool, List[str]]:
    """
    Validate a month/category/revenue/n_orders CSV file.

    Returns:
        (True, []) if the feed is valid.
        (False, errors) if validation errors exist.
    """

    errors = []

    with open(csv_path, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):

            month = row.get("month", "")
            category = row.get("category", "")
            revenue = row.get("revenue", "")

            # Check missing category
            if not category.strip():
                errors.append(
                    f"line {line_number}: "
                    f"missing category (month={month})"
                )

            # Check missing revenue
            if not revenue.strip():
                errors.append(
                    f"line {line_number}: "
                    f"missing revenue (category={category})"
                )

                # No need to check numeric/negative
                # because revenue is already missing.
                continue

            # Check numeric revenue
            try:
                revenue_value = float(revenue)

            except ValueError:
                errors.append(
                    f"line {line_number}: "
                    f"revenue not numeric: {revenue!r}"
                )
                continue

            # Check negative revenue
            if revenue_value < 0:
                errors.append(
                    f"line {line_number}: "
                    f"negative revenue ({revenue_value}) "
                    f"for category={category}"
                )

    if len(errors) == 0:
        return True, []

    return False, errors