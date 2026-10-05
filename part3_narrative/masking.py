from typing import List

def alias_for(reseller_id: str) -> str:
    """
    Convert reseller ID into an external-safe alias.

    Example:
        RS019 -> ALIAS-19
        RS006 -> ALIAS-06
    """

    return f"ALIAS-{reseller_id[3:]}"


def assert_no_raw_names_leak(
    text: str,
    reseller_names: List[str]
) -> bool:
    """
    Return False if any raw reseller name appears in the text.
    """

    for name in reseller_names:

        if name in text:
            return False

    return True