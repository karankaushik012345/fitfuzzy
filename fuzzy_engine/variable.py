"""
FuzzyVariable class
Each input/output has a name, a universe of discourse (range),
and a set of labeled membership functions.
"""
from fuzzy_engine.membership import triangular, trapezoidal


class FuzzyVariable:
    def __init__(self, name, range_min, range_max):
        self.name = name
        self.range_min = range_min
        self.range_max = range_max
        self.membership_functions = {}

    def add_triangular(self, label, a, b, c):
        self.membership_functions[label] = ('tri', a, b, c)

    def add_trapezoidal(self, label, a, b, c, d):
        self.membership_functions[label] = ('trap', a, b, c, d)

    def fuzzify(self, value):
        result = {}
        for label, params in self.membership_functions.items():
            mf_type = params[0]
            if mf_type == 'tri':
                _, a, b, c = params
                result[label] = triangular(value, a, b, c)
            elif mf_type == 'trap':
                _, a, b, c, d = params
                result[label] = trapezoidal(value, a, b, c, d)
        return result

    def get_active_labels(self, value, threshold=0.01):
        memberships = self.fuzzify(value)
        return {k: v for k, v in memberships.items() if v > threshold}
