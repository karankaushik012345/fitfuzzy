"""
Rule and SugenoEngine classes.
"""
from fuzzy_engine.operators import fuzzy_and, fuzzy_or


class Rule:
    def __init__(self, name, antecedents, consequent_func, operator='and'):
        self.name = name
        self.antecedents = antecedents
        self.consequent_func = consequent_func
        self.operator = operator

    def firing_strength(self, fuzzified_inputs):
        mu_values = []
        for var_name, label in self.antecedents:
            mu = fuzzified_inputs.get(var_name, {}).get(label, 0.0)
            mu_values.append(mu)
        if not mu_values:
            return 0.0
        if self.operator == 'and':
            return fuzzy_and(*mu_values)
        else:
            return fuzzy_or(*mu_values)


class SugenoEngine:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def predict(self, crisp_inputs, fuzzified_inputs):
        numerator = 0.0
        denominator = 0.0
        rule_details = []
        for rule in self.rules:
            omega = rule.firing_strength(fuzzified_inputs)
            z_i = rule.consequent_func(crisp_inputs)
            numerator += omega * z_i
            denominator += omega
            rule_details.append({
                'name': rule.name,
                'omega': round(omega, 4),
                'z_i': round(z_i, 2),
                'contribution': round(omega * z_i, 4),
                'fired': omega > 0.01
            })
        if denominator < 0.001:
            output = 50.0
        else:
            output = numerator / denominator
        return round(output, 2), rule_details
