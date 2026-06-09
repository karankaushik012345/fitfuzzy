"""
Fuzzy Logic Operators
AND = min, OR = max, NOT = 1 - mu
"""


def fuzzy_and(*mu_values):
    """AND operator: minimum of all membership values."""
    return min(mu_values)


def fuzzy_or(*mu_values):
    """OR operator: maximum of all membership values."""
    return max(mu_values)


def fuzzy_not(mu):
    """NOT operator: complement of membership value."""
    return 1.0 - mu
