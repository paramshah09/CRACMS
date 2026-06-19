"""
Risk scoring logic for CRACMS.

Implements the standard "Likelihood x Impact" risk matrix used in GRC
(Governance, Risk, and Compliance) work: every risk is rated on two
1-5 scales, and those two numbers are multiplied together to produce
a single score that's easy to sort, filter, and color-code.
"""


def calculate_risk_score(likelihood, impact):
    """
    Multiplies likelihood and impact to get the numeric risk score.

    Both likelihood and impact must be whole numbers from 1 to 5,
    matching the 5x5 risk matrix used throughout the app.

    Raises:
        ValueError: if likelihood or impact is not an integer between 1 and 5.
    """
    if likelihood not in range(1, 6):
        raise ValueError("likelihood must be an integer between 1 and 5")
    if impact not in range(1, 6):
        raise ValueError("impact must be an integer between 1 and 5")

    return likelihood * impact


def calculate_risk_level(score):
    """
    Converts a numeric risk score into a qualitative risk level,
    using these bands:

        Score 1-4   -> Low
        Score 5-9   -> Medium
        Score 10-16 -> High
        Score 17-25 -> Critical

    Raises:
        ValueError: if score is not an integer between 1 and 25.
    """
    if score not in range(1, 26):
        raise ValueError("score must be an integer between 1 and 25")

    if score <= 4:
        return "Low"
    elif score <= 9:
        return "Medium"
    elif score <= 16:
        return "High"
    else:
        return "Critical"


def evaluate_risk(likelihood, impact):
    """
    Convenience function that runs both steps in one call: calculates
    the score from likelihood and impact, then converts that score
    into a risk level.

    Returns:
        tuple: (score, level) -- e.g. (12, "High")
    """
    score = calculate_risk_score(likelihood, impact)
    level = calculate_risk_level(score)
    return score, level
