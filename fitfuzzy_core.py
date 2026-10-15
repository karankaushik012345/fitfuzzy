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
        return ("Complete Rest", "🛌",
                "Your physiological markers indicate high fatigue. Focus on cellular restoration, parasympathetic nervous system recovery, and deep sleep.", "0 min active",
                ["Prioritize 8+ hours of uninterrupted sleep tonight",
                 "Maintain optimal hydration with key electrolytes",
                 "Gentle 5-10 min light mobility or diaphragmatic breathing",
                 "Focus on whole-food nutrient density and high protein intake",
                 "Review your split and plan tomorrow's session instead"])
    elif score <= 40:
        return ("Active Recovery", "🧘",
                "Sub-maximal restorative movement designed to promote blood flow, clear metabolic waste, and reduce joint stiffness without systemic fatigue.", "20-30 min",
                ["15-20 min restorative yoga, dynamic flow, or full-body mobility",
                 "15-20 min leisurely outdoor walk in Zone 1 (<60% HR max)",
                 "Targeted foam rolling & myofascial release on tight muscle chains",
                 "Strictly avoid heavy compound loads, sprinting, or HIIT",
                 "Stay in parasympathetic state with light hydration"])
    elif score <= 55:
        return ("Light Cardio", "🚶",
                "Aerobic base conditioning and steady-state movement to build mitochondrial density while preserving your nervous system.", "30-40 min",
                ["25-35 min steady-state low-impact cardio (incline walk, light cycle, rowing)",
                 "Low-load bodyweight movement circuits or technique practice",
                 "Keep heart rate locked strictly in aerobic Zone 2 (60-70% HR max)",
                 "Emphasize movement quality, cadence, and steady nasal breathing",
                 "Conclude with 5-10 min targeted static cooldown stretches"])
    elif score <= 70:
        return ("Moderate Training", "💪",
                "Productive hypertrophy and strength stimulus. Push compound patterns with disciplined volume and controlled proximity to failure.", "45-60 min",
                ["Target compound lifts at 65-75% 1RM (RPE 6.5-7.5)",
                 "Execute 3-4 working sets per exercise with 2-3 reps in reserve (RIR)",
                 "Maintain 90-120 seconds structured rest between compound sets",
                 "Begin with an 8-10 min progressive dynamic warm-up protocol",
                 "Excellent day for technical volume, accessory hypertrophy, or tempo work"])
    elif score <= 85:
        return ("Solid Workout", "🔥",
                "High-performance training session. Prime neurological readiness allows for progressive overload, heavier loads, and high mechanical tension.", "60-75 min",
                ["Compound lifts executed at 75-85% 1RM (RPE 8.0-8.5)",
                 "Execute 4-5 working sets with progressive overload on core exercises",
                 "Take 2-3 minutes complete rest on heavy multijoint compounds",
                 "Optimal session to test technical load or hit rep PRs",
                 "Ensure post-workout carbohydrate & protein replenishment within 90 min"])
    else:
        return ("Heavy Training Day", "⚡",
                "Peak physical readiness and maximal capacity. Your body is fully primed for high central nervous system output, maximal strength, or high-intensity threshold work.", "75-90 min",
                ["Heavy primary compound movements (Squat, Deadlift, Bench, Clean/Snatch)",
                 "Train at 85-95% 1RM with intense neurological drive (RPE 9.0-9.5)",
                 "Comprehensive 12-15 min ramp-up warm-up and activation protocol",
                 "Log all load milestones and push for new personal records (PRs)",
                 "Ensure solid pre-workout nutrition 90-120 min prior to session"])


def get_intensity_color(score):
    if score <= 20:   return "#38BDF8"  # Sky blue / Rest
    elif score <= 40: return "#34D399"  # Emerald / Active Recovery
    elif score <= 55: return "#818CF8"  # Indigo / Light Cardio
    elif score <= 70: return "#F59E0B"  # Amber / Moderate Training
    elif score <= 85: return "#F97316"  # Orange / Solid Workout
    else:             return "#EF4444"  # Red / Heavy Training Day


def get_rpe_target(score):
    if score <= 20:   return "RPE 1 – 2  (Rest / Effortless)"
    elif score <= 40: return "RPE 3 – 4  (Extremely Light / Conversational)"
    elif score <= 55: return "RPE 5 – 6  (Moderate Aerobic / Steady)"
    elif score <= 70: return "RPE 7 – 8  (Challenging / 2-3 Reps in Reserve)"
    elif score <= 85: return "RPE 8.5 – 9 (Heavy Stimulus / 1 Rep in Reserve)"
    else:             return "RPE 9.5 – 10 (Peak Neurological Maximum Effort)"


def get_hr_zone(score):
    if score <= 20:   return "Zone 1: Restorative (< 55% HRmax)"
    elif score <= 40: return "Zone 1-2: Active Recovery (55% – 65% HRmax)"
    elif score <= 55: return "Zone 2: Aerobic Base (65% – 75% HRmax)"
    elif score <= 70: return "Zone 3: Tempo / Aerobic Power (75% – 82% HRmax)"
    elif score <= 85: return "Zone 4: Threshold / Anaerobic (82% – 90% HRmax)"
    else:             return "Zone 5: Maximum Capacity (90% – 100% HRmax)"

