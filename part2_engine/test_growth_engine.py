import os

from growth_engine import (
    mom_growth,
    is_flagged,
    validate_feed
)


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


CORRUPTED_FEED = os.path.join(
    BASE_DIR,
    "fixtures",
    "corrupted_feed.csv"
)


VALID_FEED = os.path.join(
    BASE_DIR,
    "fixtures",
    "monthly_category_revenue.csv"
)


def test_ethnic_wear_growth():

    # GIVEN
    previous = 104520.77
    current = 185107.61

    # WHEN
    growth = mom_growth(previous, current)
    result = is_flagged(growth)

    # THEN
    assert growth == 77.1
    assert result == "flagged"


def test_beauty_personal_care_growth():

    # GIVEN
    previous = 35542.11
    current = 37559.07

    # WHEN
    growth = mom_growth(previous, current)
    result = is_flagged(growth)

    # THEN
    assert growth == 5.67
    assert result == "not_flagged"


def test_exact_boundary():

    # GIVEN
    previous = 100000
    current = 108000

    # WHEN
    growth = mom_growth(previous, current)
    result = is_flagged(growth)

    # THEN
    assert growth == 8.0
    assert result == "escalate_exact_boundary"


def test_corrupted_feed():

    # GIVEN
    feed = CORRUPTED_FEED

    # WHEN
    valid, errors = validate_feed(feed)

    # THEN
    expected_errors = [
        "line 3: negative revenue (-4200.0) "
        "for category=Western Wear",

        "line 4: missing category (month=July)",

        "line 6: missing revenue "
        "(category=Home & Kitchen)"
    ]

    assert valid is False
    assert len(errors) == 3
    assert errors == expected_errors


def test_valid_feed():

    # GIVEN
    feed = VALID_FEED

    # WHEN
    valid, errors = validate_feed(feed)

    # THEN
    assert valid is True
    assert errors == []


def test_may_vs_april():

    data = {
        "Ethnic Wear": (
            104520.77,
            185107.61,
            77.1
        ),

        "Western Wear": (
            113866.15,
            86998.18,
            -23.6
        ),

        "Kids Wear": (
            59847.27,
            45793.78,
            -23.48
        ),

        "Home & Kitchen": (
            100446.23,
            91152.57,
            -9.25
        ),

        "Beauty & Personal Care": (
            40737.01,
            35542.11,
            -12.75
        )
    }

    for category, values in data.items():

        previous = values[0]
        current = values[1]
        expected_growth = values[2]

        growth = mom_growth(
            previous,
            current
        )

        result = is_flagged(growth)

        assert growth == expected_growth
        assert result == "flagged"


def test_june_vs_may():

    data = {
        "Ethnic Wear": (
            185107.61,
            76371.53,
            -58.74,
            "flagged"
        ),

        "Western Wear": (
            86998.18,
            97415.64,
            11.97,
            "flagged"
        ),

        "Kids Wear": (
            45793.78,
            56737.78,
            23.9,
            "flagged"
        ),

        "Home & Kitchen": (
            91152.57,
            129971.22,
            42.59,
            "flagged"
        ),

        "Beauty & Personal Care": (
            35542.11,
            37559.07,
            5.67,
            "not_flagged"
        )
    }

    for category, values in data.items():

        previous = values[0]
        current = values[1]
        expected_growth = values[2]
        expected_status = values[3]

        growth = mom_growth(
            previous,
            current
        )

        result = is_flagged(growth)

        assert growth == expected_growth
        assert result == expected_status