# ============================================================
# FitFuzzy Project Setup Script
# Run this in PowerShell as Administrator
# Creates the complete project in one shot
# ============================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  FitFuzzy - Project Setup" -ForegroundColor Cyan
Write-Host "  Personalized Workout Recommender" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Create folder structure ────────────────────────────
Write-Host "[1/7] Creating project folders..." -ForegroundColor Yellow

$base = "$env:USERPROFILE\Desktop\fitfuzzy"
New-Item -ItemType Directory -Force -Path "$base"                      | Out-Null
New-Item -ItemType Directory -Force -Path "$base\fuzzy_engine"         | Out-Null
New-Item -ItemType Directory -Force -Path "$base\.streamlit"           | Out-Null
New-Item -ItemType Directory -Force -Path "$base\data"                 | Out-Null

Write-Host "    Folders created at: $base" -ForegroundColor Green

# ── 2. membership.py ─────────────────────────────────────
Write-Host "[2/7] Writing fuzzy engine files..." -ForegroundColor Yellow

@'
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
'@ | Set-Content "$base\fuzzy_engine\membership.py" -Encoding UTF8

# ── operators.py ──────────────────────────────────────────
@'
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
'@ | Set-Content "$base\fuzzy_engine\operators.py" -Encoding UTF8

# ── variable.py ───────────────────────────────────────────
@'
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
'@ | Set-Content "$base\fuzzy_engine\variable.py" -Encoding UTF8

# ── engine.py ─────────────────────────────────────────────
@'
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
'@ | Set-Content "$base\fuzzy_engine\engine.py" -Encoding UTF8

# ── __init__.py ───────────────────────────────────────────
@'
from fuzzy_engine.membership import triangular, trapezoidal
from fuzzy_engine.operators import fuzzy_and, fuzzy_or, fuzzy_not
from fuzzy_engine.variable import FuzzyVariable
from fuzzy_engine.engine import Rule, SugenoEngine
'@ | Set-Content "$base\fuzzy_engine\__init__.py" -Encoding UTF8

Write-Host "    fuzzy_engine/ package written." -ForegroundColor Green

# ── 3. fitfuzzy_core.py ───────────────────────────────────
Write-Host "[3/7] Writing domain logic (variables + 12 rules)..." -ForegroundColor Yellow

@'
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
                "Your body needs full recovery today.", "0 min active",
                ["Sleep 8+ hours tonight","Stay hydrated throughout the day",
                 "Light stretching if restless","Focus on nutrition and protein intake",
                 "Plan tomorrow's session instead"])
    elif score <= 40:
        return ("Active Recovery", "🧘",
                "Light movement only - let your body heal.", "20-30 min",
                ["15 min gentle yoga or stretching","10-15 min slow walk",
                 "Foam rolling on sore areas","No heavy weights or HIIT today",
                 "Great day for mobility work"])
    elif score <= 55:
        return ("Light Cardio", "🚶",
                "Low-intensity movement to maintain momentum.", "30-40 min",
                ["20-30 min brisk walk or light jog","Bodyweight exercises only",
                 "Keep heart rate below 130 bpm","Focus on form not load",
                 "Finish with 10 min stretching"])
    elif score <= 70:
        return ("Moderate Training", "💪",
                "Solid session - push consistently not maximally.", "45-60 min",
                ["Compound lifts at 65-75% of max","3-4 sets per exercise",
                 "2 min rest between sets","Include 10 min warm-up",
                 "Good day for skill work"])
    elif score <= 85:
        return ("Solid Workout", "🔥",
                "You're ready - make this session count.", "60-75 min",
                ["Compound lifts at 75-85% of max","4-5 sets progressive overload",
                 "1.5 min rest between sets","Good day to attempt a PR",
                 "Prioritise sleep tonight to recover"])
    else:
        return ("Heavy Training Day", "⚡",
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
'@ | Set-Content "$base\fitfuzzy_core.py" -Encoding UTF8

Write-Host "    fitfuzzy_core.py written (5 variables, 12 rules)." -ForegroundColor Green

# ── 4. app.py (full Streamlit UI) ────────────────────────
Write-Host "[4/7] Writing Streamlit app (app.py)..." -ForegroundColor Yellow

# Read the full app from here
$appContent = @'
"""
FitFuzzy - Personalized Workout Intensity Recommender
Built with Python + Fuzzy Logic + Streamlit
"""

import streamlit as st
from datetime import datetime
from fitfuzzy_core import build_fitfuzzy_engine, interpret_intensity, get_intensity_color

st.set_page_config(page_title="FitFuzzy", page_icon="💪", layout="wide")

st.markdown("""
<style>
.fitfuzzy-header{background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);
padding:2rem 2.5rem;border-radius:16px;margin-bottom:2rem;border:1px solid #0f3460;}
.intensity-card{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:2rem;
border-radius:16px;text-align:center;border:1px solid #0f3460;margin:1rem 0;}
.rule-card-fired{background:#1a2744;padding:.7rem 1rem;border-radius:8px;
border-left:3px solid #4ade80;margin:.3rem 0;font-size:.85rem;}
.rule-card-unfired{background:#111827;padding:.7rem 1rem;border-radius:8px;
border-left:3px solid #374151;margin:.3rem 0;font-size:.85rem;opacity:.5;}
.tip-item{background:#1e293b;padding:.5rem 1rem;border-radius:8px;margin:.25rem 0;}
.history-item{background:#1a1a2e;padding:.6rem 1rem;border-radius:8px;
margin:.3rem 0;border:1px solid #1f2937;}
.gauge-container{background:#1e293b;border-radius:999px;height:12px;
width:100%;margin:.5rem 0;overflow:hidden;}
.mu-badge{display:inline-block;background:#0f3460;color:#74b9ff;
padding:.15rem .5rem;border-radius:12px;font-size:.75rem;font-weight:600;margin-left:.3rem;}
#MainMenu{visibility:hidden;}footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []
if 'engine' not in st.session_state:
    st.session_state.engine, st.session_state.variables = build_fitfuzzy_engine()

engine    = st.session_state.engine
variables = st.session_state.variables

st.markdown("""
<div class="fitfuzzy-header">
<h1 style="color:white;margin:0;font-size:2.2rem;">💪 FitFuzzy</h1>
<p style="color:#94a3b8;margin:.4rem 0 0 0;">Personalized workout intensity recommender using Fuzzy Logic</p>
<p style="color:#4b5563;margin:.2rem 0 0 0;font-size:.8rem;">
Sugeno Inference · Triangular & Trapezoidal MFs · 12 Expert Rules</p>
</div>
""", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown("### Daily Check-In")
    st.markdown("*Tell FitFuzzy how you feel today.*")
    sleep_val    = st.slider("😴 Sleep Quality",        0.0, 10.0, 7.0, 0.5)
    soreness_val = st.slider("🦵 Muscle Soreness",      0.0, 10.0, 3.0, 0.5)
    stress_val   = st.slider("🧠 Stress Level",         0.0, 10.0, 4.0, 0.5)
    time_val     = st.slider("⏱️ Available Time (min)", 10,  120,  60,  5)
    rest_val     = st.slider("📅 Days Since Last Rest", 0,   10,   2,   1)
    goal         = st.selectbox("🎯 Current Goal Phase",
                                ["Bulking","Cutting","Maintenance","Recomp"])
    predict_btn  = st.button("⚡ Get My Recommendation",
                             use_container_width=True, type="primary")

with col_result:
    if predict_btn:
        crisp = {'sleep':sleep_val,'soreness':soreness_val,'stress':stress_val,
                 'time':time_val,'rest_days':rest_val}
        fuzz = {k: v.fuzzify(crisp[k]) for k, v in variables.items()}
        intensity_score, rule_details = engine.predict(crisp, fuzz)
        workout_type, emoji, description, duration, tips = interpret_intensity(intensity_score)
        intensity_color = get_intensity_color(intensity_score)

        st.session_state.history.insert(0, {
            'time': datetime.now().strftime("%H:%M"),
            'type': workout_type, 'score': intensity_score,
            'emoji': emoji, 'sleep': sleep_val,
            'soreness': soreness_val, 'stress': stress_val,
            'time_avail': time_val, 'goal': goal
        })
        st.session_state.history = st.session_state.history[:8]

        st.markdown(f"""
        <div class="intensity-card">
        <div style="font-size:3.5rem;margin-bottom:.5rem;">{emoji}</div>
        <div style="font-size:1.8rem;font-weight:700;color:{intensity_color};">{workout_type}</div>
        <div style="font-size:2.8rem;font-weight:800;color:white;margin:.3rem 0;">
        {intensity_score:.0f} <span style="font-size:1rem;color:#94a3b8;">/ 100</span></div>
        <div style="color:#94a3b8;margin-bottom:.8rem;">{description}</div>
        <div style="background:{intensity_color}22;border:1px solid {intensity_color}44;
        padding:.4rem 1rem;border-radius:999px;display:inline-block;
        color:{intensity_color};font-size:.9rem;font-weight:600;">⏱️ {duration}</div>
        </div>""", unsafe_allow_html=True)

        bar_pct = intensity_score
        st.markdown(f"""
        <div style="margin:.5rem 0;">
        <div style="display:flex;justify-content:space-between;
        color:#64748b;font-size:.75rem;margin-bottom:.3rem;">
        <span>Rest</span><span>Light</span><span>Moderate</span><span>Heavy</span></div>
        <div class="gauge-container">
        <div style="height:100%;width:{bar_pct}%;
        background:linear-gradient(90deg,#74b9ff,{intensity_color});
        border-radius:999px;"></div></div></div>""", unsafe_allow_html=True)

        with st.expander("🔬 Fuzzification — How Your Inputs Were Interpreted"):
            fc1, fc2 = st.columns(2)
            inputs_list = [
                ('sleep','😴 Sleep',sleep_val,'/ 10'),
                ('soreness','🦵 Soreness',soreness_val,'/ 10'),
                ('stress','🧠 Stress',stress_val,'/ 10'),
                ('time','⏱️ Time',time_val,'min'),
                ('rest_days','📅 Rest Days',rest_val,'days'),
            ]
            for i,(vn,lbl,val,unit) in enumerate(inputs_list):
                col = fc1 if i % 2 == 0 else fc2
                with col:
                    st.markdown(f"**{lbl}** = {val} {unit}")
                    active = {k:v for k,v in fuzz[vn].items() if v > 0.01}
                    for lbl2, mu in sorted(active.items(), key=lambda x:-x[1]):
                        bw = int(mu*100)
                        st.markdown(
                            f'<span style="color:#94a3b8;font-size:.8rem;">{lbl2}</span>'
                            f'<span class="mu-badge">μ={mu:.3f}</span>'
                            f'<div class="gauge-container" style="height:6px;margin:2px 0;">'
                            f'<div style="height:100%;width:{bw}%;background:#4ade80;border-radius:999px;"></div>'
                            f'</div>', unsafe_allow_html=True)
                    st.markdown("")

        with st.expander("📋 Inference Engine — Which Rules Fired?", expanded=True):
            fired   = [r for r in rule_details if r['fired']]
            unfired = [r for r in rule_details if not r['fired']]
            st.markdown(f"*{len(fired)} of {len(rule_details)} rules fired.*")
            if fired:
                st.markdown("**Active rules:**")
                for r in sorted(fired, key=lambda x:-x['omega']):
                    st.markdown(
                        f'<div class="rule-card-fired">✅ <b>{r["name"]}</b><br/>'
                        f'<span style="color:#4ade80;font-size:.8rem;">ω={r["omega"]:.4f}</span> | '
                        f'<span style="color:#94a3b8;font-size:.8rem;">z={r["z_i"]:.1f}</span> | '
                        f'<span style="color:#fdcb6e;font-size:.8rem;">contrib={r["contribution"]:.3f}</span>'
                        f'</div>', unsafe_allow_html=True)
            if unfired:
                st.markdown("**Silent rules:**")
                for r in unfired:
                    st.markdown(f'<div class="rule-card-unfired">⬜ {r["name"]}</div>',
                                unsafe_allow_html=True)

        with st.expander("💡 Training Tips for Today", expanded=True):
            for tip in tips:
                st.markdown(f'<div class="tip-item">• {tip}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#4b5563;">
        <div style="font-size:4rem;margin-bottom:1rem;">🏋️</div>
        <div style="font-size:1.1rem;color:#6b7280;">
        Set your inputs on the left and click<br/>
        <strong style="color:#94a3b8;">⚡ Get My Recommendation</strong></div>
        <div style="margin-top:1.5rem;font-size:.85rem;color:#374151;">
        FitFuzzy uses 12 fuzzy expert rules to analyse<br/>
        your sleep, soreness, stress, and time to give<br/>
        the perfect workout intensity for today.</div></div>""",
        unsafe_allow_html=True)

if st.session_state.history:
    st.markdown("---")
    c1, c2 = st.columns([4,1])
    with c1: st.markdown("### Session History")
    with c2:
        if st.button("🗑️ Clear"):
            st.session_state.history = []
            st.rerun()
    hcols = st.columns(min(len(st.session_state.history), 4))
    for i, entry in enumerate(st.session_state.history[:4]):
        color = get_intensity_color(entry['score'])
        with hcols[i]:
            st.markdown(
                f'<div class="history-item" style="border-top:3px solid {color};">'
                f'<div style="font-size:1.4rem;text-align:center;">{entry["emoji"]}</div>'
                f'<div style="text-align:center;font-weight:700;color:{color};font-size:.9rem;">{entry["type"]}</div>'
                f'<div style="text-align:center;color:#64748b;font-size:.75rem;">{entry["score"]:.0f}/100 · {entry["time"]}</div>'
                f'<div style="text-align:center;color:#4b5563;font-size:.7rem;margin-top:4px;">'
                f'😴{entry["sleep"]} 🦵{entry["soreness"]} 🧠{entry["stress"]}</div></div>',
                unsafe_allow_html=True)

st.markdown("---")
with st.expander("📚 About FitFuzzy — How It Works"):
    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown("**🔬 Fuzzy Logic Pipeline**")
        st.markdown("1. **Fuzzification** — crisp → μ values\n2. **Inference** — 12 IF-THEN rules\n3. **Defuzzification** — Sugeno weighted avg")
    with a2:
        st.markdown("**🏗️ Architecture**")
        st.markdown("- Triangular + Trapezoidal MFs\n- AND=min, OR=max operators\n- Sugeno inference method\n- 5 inputs, 12 rules")
    with a3:
        st.markdown("**📊 Intensity Scale**")
        st.markdown("0–20: Rest\n21–40: Recovery\n41–55: Light\n56–70: Moderate\n71–85: Solid\n86–100: Heavy")

st.markdown("""
<div style="text-align:center;color:#4b5563;font-size:.75rem;margin-top:2rem;">
FitFuzzy · Python + Fuzzy Logic + Streamlit · NIT Silchar ECE 2027</div>""",
unsafe_allow_html=True)
'@

$appContent | Set-Content "$base\app.py" -Encoding UTF8
Write-Host "    app.py written." -ForegroundColor Green

# ── 5. Config + requirements ──────────────────────────────
Write-Host "[5/7] Writing config and requirements..." -ForegroundColor Yellow

@'
[theme]
base = "dark"
primaryColor = "#4ade80"
backgroundColor = "#0f1117"
secondaryBackgroundColor = "#1a1a2e"
textColor = "#e2e8f0"
font = "sans serif"
'@ | Set-Content "$base\.streamlit\config.toml" -Encoding UTF8

@'
streamlit>=1.28.0
pandas>=2.0.0
'@ | Set-Content "$base\requirements.txt" -Encoding UTF8

Write-Host "    Config and requirements written." -ForegroundColor Green

# ── 6. README ─────────────────────────────────────────────
Write-Host "[6/7] Writing README..." -ForegroundColor Yellow

@'
# FitFuzzy - Personalized Workout Intensity Recommender

A fuzzy logic-based workout recommendation system.

## Run locally
```
pip install streamlit
streamlit run app.py
```

## Project Structure
- app.py             - Streamlit UI
- fitfuzzy_core.py   - Domain: variables, MFs, 12 rules
- fuzzy_engine/      - Reusable fuzzy logic library
  - membership.py    - Triangular + Trapezoidal MFs
  - operators.py     - AND, OR, NOT
  - variable.py      - FuzzyVariable class
  - engine.py        - Rule + SugenoEngine

## How it works
5 inputs -> Fuzzification -> 12 IF-THEN rules -> Sugeno weighted avg -> Recommendation
'@ | Set-Content "$base\README.md" -Encoding UTF8

Write-Host "    README.md written." -ForegroundColor Green

# ── 7. Install Streamlit + run ────────────────────────────
Write-Host "[7/7] Installing Streamlit..." -ForegroundColor Yellow

pip install streamlit --quiet

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Project location:" -ForegroundColor White
Write-Host "  $base" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files created:" -ForegroundColor White
Get-ChildItem -Path $base -Recurse -File | ForEach-Object {
    Write-Host ("  " + $_.FullName.Replace($base, "").TrimStart('\')) -ForegroundColor Gray
}
Write-Host ""
Write-Host "To run FitFuzzy:" -ForegroundColor White
Write-Host "  cd $base" -ForegroundColor Cyan
Write-Host "  streamlit run app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then open: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Green

# Auto-launch
$launch = Read-Host "Launch FitFuzzy now? (y/n)"
if ($launch -eq 'y' -or $launch -eq 'Y') {
    Set-Location $base
    streamlit run app.py
}
