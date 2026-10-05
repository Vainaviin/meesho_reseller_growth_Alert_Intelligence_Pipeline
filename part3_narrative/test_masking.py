from masking import (
    alias_for,
    assert_no_raw_names_leak
)


def test_alias_for():

    assert alias_for("RS019") == "ALIAS-19"
    assert alias_for("RS006") == "ALIAS-06"


def test_raw_name_leak_returns_false():

    text = "Mumbai Reseller 1 generated strong revenue."

    names = [
        "Mumbai Reseller 1"
    ]

    assert (
        assert_no_raw_names_leak(
            text,
            names
        )
        is False
    )


def test_final_narrative_has_no_raw_names():

    final_narrative = """
    The top reseller aliases were ALIAS-19, ALIAS-22,
    ALIAS-12, ALIAS-06 and ALIAS-05 across West,
    South and North regions.
    """

    reseller_names = [
        "Mumbai Reseller 1",
        "Mumbai Reseller 4",
        "Hyderabad Reseller 6",
        "Lucknow Reseller 6",
        "Jaipur Reseller 5"
    ]

    assert (
        assert_no_raw_names_leak(
            final_narrative,
            reseller_names
        )
        is True
    )