"""
FitFuzzy Domain Configuration
Defines all fuzzy variables, membership functions, and rules.
"""
from fuzzy_engine.variable import FuzzyVariable
from fuzzy_engine.engine import Rule, SugenoEngine


def build_fitfuzzy_engine():
    # INPUT VARIABLES
    sleep = FuzzyVariable('sleep', 0, 10)
    sleep.add_trapezoidal('poor',    0,   0,   2.5, 4.5)
    sleep.add_triangular ('average', 3.0, 5.0, 7.0)
    sleep.add_trapezoidal('good',    6.0, 8.0, 10,  10)

    soreness = FuzzyVariable('soreness', 0, 10)
    soreness.add_trapezoidal('low',      0,   0,   2.0, 4.0)
    soreness.add_triangular ('moderate', 2.5, 5.0, 7.5)
    soreness.add_trapezoidal('high',     6.0, 8.0, 10,  10)

    stress = FuzzyVariable('stress', 0, 10)
    stress.add_trapezoidal('low',      0,   0,   2.5, 4.5)
    stress.add_triangular ('moderate', 3.0, 5.0, 7.0)
    stress.add_trapezoidal('high',     6.0, 8.0, 10,  10)

    time_avail = FuzzyVariable('time', 0, 120)
    time_avail.add_trapezoidal('short',    0,  0,  20, 35)
    time_avail.add_triangular ('moderate', 25, 45, 65)
    time_avail.add_trapezoidal('long',     55, 75, 120, 120)

    rest_days = FuzzyVariable('rest_days', 0, 10)
    rest_days.add_trapezoidal('fresh',    0, 0, 1.5, 3.0)
    rest_days.add_triangular ('moderate', 2, 4, 6)
    rest_days.add_trapezoidal('overdue',  5, 7, 10, 10)

    variables = {
        'sleep': sleep, 'soreness': soreness,
        'stress': stress, 'time': time_avail, 'rest_days': rest_days
    }

    # CONSEQUENT FUNCTIONS
    def intensity_full_rest(inputs):      return 10.0
    def intensity_active_recovery(inputs): return 28.0
    def intensity_light(inputs):           return 42.0
    def intensity_moderate(inputs):        return 58.0
    def intensity_solid(inputs):           return 74.0
    def intensity_heavy(inputs):
        base = 84.0
        sleep_bonus = (inputs.get('sleep', 7) - 7) * 1.5
        time_bonus  = max(0, (inputs.get('time', 60) - 60) * 0.1)
        return min(100.0, base + sleep_bonus + time_bonus)

    # BUILD ENGINE
    engine = SugenoEngine()

    engine.add_rule(Rule('R1: Sore + Stressed -> Full Rest',
        [('soreness','high'),('stress','high')], intensity_full_rest, 'and'))
    engine.add_rule(Rule('R2: Poor Sleep + High Soreness -> Full Rest',
        [('sleep','poor'),('soreness','high')], intensity_full_rest, 'and'))
    engine.add_rule(Rule('R3: Overdue Rest + High Soreness -> Rest',
        [('rest_days','overdue'),('soreness','high')], intensity_full_rest, 'and'))
    engine.add_rule(Rule('R4: Poor Sleep or High Stress -> Active Recovery',
        [('sleep','poor'),('stress','high')], intensity_active_recovery, 'or'))
    engine.add_rule(Rule('R5: Short Time + Moderate Soreness -> Light',
        [('time','short'),('soreness','moderate')], intensity_light, 'and'))
    engine.add_rule(Rule('R6: High Stress + Average Sleep -> Light',
        [('stress','high'),('sleep','average')], intensity_light, 'and'))
    engine.add_rule(Rule('R7: Average Sleep + Low Soreness + Moderate Stress -> Moderate',
        [('sleep','average'),('soreness','low'),('stress','moderate')], intensity_moderate, 'and'))
    engine.add_rule(Rule('R8: Good Sleep + Moderate Soreness + Moderate Time -> Moderate',
        [('sleep','good'),('soreness','moderate'),('time','moderate')], intensity_moderate, 'and'))
    engine.add_rule(Rule('R9: Low Stress + Average Sleep + Time -> Solid',
        [('stress','low'),('sleep','average'),('time','moderate')], intensity_solid, 'and'))
    engine.add_rule(Rule('R10: Good Sleep + Low Soreness + Low Stress -> Solid',
        [('sleep','good'),('soreness','low'),('stress','low')], intensity_solid, 'and'))
    engine.add_rule(Rule('R11: Peak Conditions + Long Time -> Heavy',
        [('sleep','good'),('soreness','low'),('time','long')], intensity_heavy, 'and'))
    engine.add_rule(Rule('R12: Short Time + High Stress -> Light',
        [('time','short'),('stress','high')], intensity_active_recovery, 'or'))

    return engine, variables


def interpret_intensity(score):
    if score <= 20:
        return ("Complete Rest", "ðŸ›Œ",
                "Your body needs full recovery today.", "0 min active",
                ["Sleep 8+ hours tonight","Stay hydrated throughout the day",
                 "Light stretching if restless","Focus on nutrition and protein intake",
                 "Plan tomorrow's session instead"])
    elif score <= 40:
        return ("Active Recovery", "ðŸ§˜",
                "Light movement only - let your body heal.", "20-30 min",
                ["15 min gentle yoga or stretching","10-15 min slow walk",
                 "Foam rolling on sore areas","No heavy weights or HIIT today",
                 "Great day for mobility work"])
    elif score <= 55:
        return ("Light Cardio", "ðŸš¶",
                "Low-intensity movement to maintain momentum.", "30-40 min",
                ["20-30 min brisk walk or light jog","Bodyweight exercises only",
                 "Keep heart rate below 130 bpm","Focus on form not load",
                 "Finish with 10 min stretching"])
    elif score <= 70:
        return ("Moderate Training", "ðŸ’ª",
                "Solid session - push consistently not maximally.", "45-60 min",
                ["Compound lifts at 65-75% of max","3-4 sets per exercise",
                 "2 min rest between sets","Include 10 min warm-up",
                 "Good day for skill work"])
    elif score <= 85:
        return ("Solid Workout", "ðŸ”¥",
                "You're ready - make this session count.", "60-75 min",
                ["Compound lifts at 75-85% of max","4-5 sets progressive overload",
                 "1.5 min rest between sets","Good day to attempt a PR",
                 "Prioritise sleep tonight to recover"])
    else:
        return ("Heavy Training Day", "âš¡",
                "Peak conditions - go for maximum effort.", "75-90 min",
                ["Heavy compound movements (squat deadlift bench)",
                 "Work at 85-95% of max","Full warm-up protocol (15 min)",
                 "Track every set - aim for PRs",
                 "Eat a solid meal 2 hrs before training"])


def get_intensity_color(score):
    if score <= 20:   return "#A8D5BA"
    elif score <= 40: return "#74B9FF"
    elif score <= 55: return "#81ECEC"
    elif score <= 70: return "#FDCB6E"
    elif score <= 85: return "#E17055"
    else:             return "#D63031"
