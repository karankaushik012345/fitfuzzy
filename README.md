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
