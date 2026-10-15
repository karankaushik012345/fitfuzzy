# ⚡ FitFuzzy - Explainable AI Workout Intensity Prescription Engine

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://fitfuzzy.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Explainable AI](https://img.shields.io/badge/XAI-100%25%20Transparent-brightgreen.svg)](#-scientific-core-how-the-math-works)

> **A zero-dependency Sugeno Fuzzy Inference System (FIS) built entirely from scratch in Python to compute personalized workout intensity prescriptions from biological fatigue, systemic stress, and schedule markers.**

FitFuzzy is an Explainable AI (XAI) health and athletic performance dashboard. Unlike opaque deep neural network "black boxes", FitFuzzy exposes the complete mathematical logic behind every training recommendation: membership degrees ($\mu$), active IF-THEN rules, antecedent conjunctions/disjunctions, and Sugeno defuzzification weights.

---

## 🌟 Key Features

* 🎛️ **Quick Athletic Presets:** One-click simulation for *Peak Readiness*, *Heavy DOMS / Fatigue*, *Stress Overdrive*, *25m Time-Crunch*, and *Baseline Routine*.
* 🧬 **Biophysiological Sliders:** Precision sliders for Sleep Quality, DOMS Soreness, Systemic Allostatic Stress, Available Time, and Days Since Last Rest Day with dynamic condition pills.
* 🎯 **Comprehensive Prescription Output:** Intensity score (0–100), Heart Rate Cardio Zone (Zones 1–5), Rate of Perceived Exertion (RPE 1–10), Session Window, and 5 tactical training directives.
* 🔬 **Full Explainable AI (XAI) Deep Dive:**
  * Interactive **Fuzzification Inspector** with real-time membership degree bars ($\mu \in [0, 1]$).
  * **Sugeno Rule Activation Inspector** with firing strengths ($\omega_i$), singletons ($z_i$), and percentage score contribution.
  * Real-time **Mathematical Defuzzification Box** displaying the exact quotient:
    $$Y = \frac{\sum \omega_i \cdot z_i}{\sum \omega_i}$$
* 💾 **Session History & Analytics:** Session tracking log with one-click export to formatted `.txt` prescription reports.

---

## 🔬 Scientific Core: How the Math Works

Unlike binary logic (where predicates are strictly `0` or `1`), **Fuzzy Logic** allows variables to hold continuous degrees of truth between `0.0` and `1.0`.

```text
[Physiological Inputs] ➔ [Fuzzification (MFs)] ➔ [Rule Evaluation (Min/Max)] ➔ [Defuzzification (Sugeno)] ➔ [Prescription Index]
```

### 1. Fuzzification (Membership Functions)
Converts crisp numerical inputs into fuzzy membership degrees ($\mu$) via custom curves:
* **Triangular MFs:** Defined by triplet $(a, b, c)$:
  $$\mu(x) = \max\left(0, \min\left(\frac{x - a}{b - a}, \frac{c - x}{c - b}\right)\right)$$
* **Trapezoidal MFs:** Defined by quadruplet $(a, b, c, d)$:
  $$\mu(x) = \max\left(0, \min\left(\frac{x - a}{b - a}, 1, \frac{d - x}{d - c}\right)\right)$$

### 2. Fuzzy Operator Rules (Evaluation)
12 expert IF-THEN rules evaluate physiological readiness:
* **Fuzzy AND (T-Norm / Gödel):** $\mu_{A \cap B}(x) = \min(\mu_A(x), \mu_B(x))$
* **Fuzzy OR (S-Norm):** $\mu_{A \cup B}(x) = \max(\mu_A(x), \mu_B(x))$

### 3. Defuzzification (Sugeno Weighted Average)
Outputs are mapped to constant singletons ($z_i$). The final crisp intensity score ($Y$) is computed using the weighted average:
$$Y = \frac{\sum_{i=1}^{N} \omega_i \cdot z_i}{\sum_{i=1}^{N} \omega_i}$$

---

## 📂 Project Architecture

```text
fitfuzzy/
├── .streamlit/
│   └── config.toml           # Streamlit theme & UI configurations
├── fuzzy_engine/             # Reusable zero-dependency Fuzzy Logic library
│   ├── __init__.py           # Package exports
│   ├── membership.py         # Triangular & Trapezoidal mathematical curves
│   ├── operators.py          # Fuzzy AND (min), OR (max), NOT (1 - mu)
│   ├── variable.py           # FuzzyVariable universe mappings
│   └── engine.py             # Rule parser & Sugeno FIS calculation engine
├── app.py                    # High-performance Streamlit web application
├── fitfuzzy_core.py          # Domain models, 12 rules, HR/RPE interpretation
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

## 📊 Fuzzy Variables Specification

### Inputs:
1. **Sleep Quality (0 to 10):** `poor` [0, 4.5] | `average` [3.0, 7.0] | `good` [6.0, 10.0]
2. **Muscle Soreness (0 to 10):** `low` [0, 4.0] | `moderate` [2.5, 7.5] | `high` [6.0, 10.0]
3. **Stress Level (0 to 10):** `low` [0, 4.5] | `moderate` [3.0, 7.0] | `high` [6.0, 10.0]
4. **Available Time (0 to 120 min):** `short` [0, 35] | `moderate` [25, 65] | `long` [55, 120]
5. **Days Since Rest (0 to 10 days):** `fresh` [0, 3.0] | `moderate` [2.0, 6.0] | `overdue` [5.0, 10.0]

### Outputs (0 to 100 Intensity Scale):
* **Complete Rest (0–20):** Restorative focus, 0 min active, Zone 1
* **Active Recovery (21–40):** Sub-maximal mobility, 20–30 min, RPE 3–4
* **Light Cardio (41–55):** Aerobic base, 30–40 min, Zone 2
* **Moderate Training (56–70):** Hypertrophy stimulus, 45–60 min, RPE 7–8
* **Solid Workout (71–85):** Progressive overload, 60–75 min, Zone 4
* **Heavy Training Day (86–100):** Neurological peak capacity, 75–90 min, RPE 9.5–10

---

## 🛠️ Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/karankaushik012345/fitfuzzy.git
   cd fitfuzzy
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
   Open your browser at `http://localhost:8501`.

---

## 🚀 Deployment to Streamlit Cloud

1. Push your latest code to GitHub:
   ```bash
   git add .
   git commit -m "Enhance UI with professional design system and XAI analytics"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account and select:
   * **Repository:** `karankaushik012345/fitfuzzy`
   * **Branch:** `main`
   * **Main file path:** `app.py`
4. Click **Deploy!**

---

## 🎓 Academic Attribution & Credits

* **Author:** Karan Kaushik
* **Institution:** National Institute of Technology (NIT) Silchar, Department of Electronics and Communication Engineering (ECE 2027)
* Built from scratch without external machine learning frameworks to demonstrate mastery in fuzzy mathematical logic, object-oriented software engineering, and Explainable AI.
