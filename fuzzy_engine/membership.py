"""
Membership Functions for FitFuzzy
Triangular and trapezoidal MF shapes used by all fuzzy variables.
"""


def triangular(x, a, b, c):
    """
    Triangular membership function.
    a = left foot, b = peak (mu=1), c = right foot
    """
    x = float(x)
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)


def trapezoidal(x, a, b, c, d):
    """
    Trapezoidal membership function.
    a = left foot, b = left shoulder, c = right shoulder, d = right foot
    """
    x = float(x)
    if x <= a or x >= d:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    elif b < x <= c:
        return 1.0
    else:
        return (d - x) / (d - c)
