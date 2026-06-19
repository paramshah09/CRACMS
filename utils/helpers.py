"""
Helper functions for CRACMS.

Small, reusable utilities that don't belong to any single module.
Right now this just holds the code-formatting helper used to turn a
prefix and a numeric ID into a human-readable record code like
RSK-001, AF-007, or CTRL-023.
"""


def generate_code(prefix, numeric_id):
    """
    Builds a formatted record code from a prefix and a numeric ID,
    zero-padding the number to 3 digits.

    Examples:
        generate_code("RSK", 1)   -> "RSK-001"
        generate_code("AF", 7)    -> "AF-007"
        generate_code("CTRL", 23) -> "CTRL-023"

    Args:
        prefix (str): Short label identifying the record type (e.g. "RSK").
        numeric_id (int): The record's numeric ID. Must be a positive integer.

    Returns:
        str: The formatted code, e.g. "RSK-001".

    Raises:
        ValueError: if prefix is empty/not a string, or numeric_id is
                    not a positive integer.
    """
    # --- Validate prefix ---
    # .strip() catches the case where someone passes in a string of
    # only spaces, like "   ", which would otherwise slip past a
    # simple "not prefix" check.
    if not isinstance(prefix, str) or not prefix.strip():
        raise ValueError("prefix must be a non-empty string")

    # --- Validate numeric_id ---
    # bool is checked separately because in Python, bool is technically
    # a subclass of int -- without this line, True/False would pass an
    # isinstance(numeric_id, int) check and silently produce a bad code.
    if isinstance(numeric_id, bool) or not isinstance(numeric_id, int):
        raise ValueError("numeric_id must be an integer")

    if numeric_id <= 0:
        raise ValueError("numeric_id must be a positive integer")

    # --- Build the code ---
    # f"{numeric_id:03d}" formats numeric_id as a decimal integer,
    # zero-padded to at least 3 digits: 1 -> "001", 23 -> "023".
    # Numbers with more than 3 digits are never truncated -- 1000
    # simply prints as "1000" instead of being cut down to 3 characters.
    return f"{prefix}-{numeric_id:03d}"
