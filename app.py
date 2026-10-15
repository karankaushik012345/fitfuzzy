"""
FitFuzzy - Explainable AI Workout Intensity Prescription Engine
Powered by Sugeno Fuzzy Inference System (FIS)
"""

import streamlit as st
from datetime import datetime
import json
from fitfuzzy_core import (
    build_fitfuzzy_engine,
    interpret_intensity,
    get_intensity_color,
    get_rpe_target,
    get_hr_zone
)

# ── PAGE CONFIGURATION ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FitFuzzy | Explainable AI Workout Planner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CUSTOM CSS & DESIGN SYSTEM ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --primary: #4F46E5;
    --primary-light: #EEF2FF;
    --primary-glow: rgba(79, 70, 229, 0.25);
    --surface: #FFFFFF;
    --background: #F8FAFC;
    --border: #E2E8F0;
    --border-subtle: #F1F5F9;
    --text-main: #0F172A;
    --text-muted: #64748B;
    --text-light: #94A3B8;
}

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--background) !important;
    color: var(--text-main) !important;
    letter-spacing: -0.01em;
}

#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1360px !important;
}

/* ── MODERN NAVBAR ── */
.navbar-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.9rem 1.6rem;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 18px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
}
.brand-group {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}
.brand-icon-box {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 1.25rem;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
}
.brand-title {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #0F172A 30%, #4F46E5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.brand-subtitle {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.nav-badges {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.badge-pill {
    padding: 0.32rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.74rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition: all 0.2s ease;
}
.badge-pill-purple {
    background: #EEF2FF;
    color: #4F46E5;
    border: 1px solid #C7D2FE;
}
.badge-pill-emerald {
    background: #ECFDF5;
    color: #059669;
    border: 1px solid #A7F3D0;
}

/* ── HERO BANNER ── */
.hero-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 60%, #312E81 100%);
    border-radius: 22px;
    padding: 2.4rem 2.8rem;
    margin-bottom: 1.8rem;
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.35);
}
.hero-card::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 480px;
    height: 480px;
    background: radial-gradient(circle, rgba(124, 58, 237, 0.25) 0%, rgba(79, 70, 229, 0) 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(8px);
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    font-size: 0.73rem;
    font-weight: 700;
    color: #A5B4FC;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.9rem;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1.15;
    margin-bottom: 0.75rem;
    color: #FFFFFF;
}
.hero-desc {
    font-size: 0.98rem;
    color: #CBD5E1;
    line-height: 1.6;
    max-width: 680px;
    margin-bottom: 1.8rem;
}
.hero-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 1.2rem;
    max-width: 650px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    padding-top: 1.4rem;
}
.h-stat-num {
    font-size: 1.65rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.h-stat-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.25rem;
}

/* ── PRESETS BAR ── */
.preset-bar-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── GLASS & CARDS ── */
.app-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.6rem;
    box-shadow: 0 4px 15px -3px rgba(15, 23, 42, 0.03), 0 2px 6px -2px rgba(15, 23, 42, 0.02);
    margin-bottom: 1.4rem;
}
.card-header-group {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.2rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-subtle);
}
.card-heading {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
}
.card-tag {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    background: #F1F5F9;
    color: var(--text-muted);
}

/* ── LIVE SNAPSHOT HUD ── */
.hud-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.65rem;
    margin-top: 1.2rem;
}
.hud-item {
    background: #F8FAFC;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.65rem 0.8rem;
    text-align: center;
}
.hud-val {
    font-size: 1.15rem;
    font-weight: 800;
    line-height: 1.1;
    font-family: 'JetBrains Mono', monospace;
}
.hud-lbl {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.2rem;
}

/* ── RESULT HERO CARD ── */
.result-box {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2.2rem 2rem;
    text-align: center;
    box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.06);
    position: relative;
    overflow: hidden;
}
.result-top-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}
.score-circle-container {
    position: relative;
    width: 170px;
    height: 170px;
    margin: 0 auto 1.4rem auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    box-shadow: 0 12px 35px -10px var(--primary-glow);
}
.score-number {
    font-size: 4.2rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 0.95;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.score-denominator {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.rec-title {
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    margin: 0.4rem 0 0.6rem 0;
}
.rec-desc {
    font-size: 0.92rem;
    color: var(--text-muted);
    line-height: 1.6;
    max-width: 520px;
    margin: 0 auto 1.5rem auto;
}

/* ── PROGRESS GAUGE ── */
.gauge-track {
    background: #E2E8F0;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
    margin: 1.2rem 0 0.5rem 0;
}
.gauge-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.gauge-markers {
    display: flex;
    justify-content: space-between;
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1.2rem;
}

/* ── 4-METRICS MATRIX ── */
.metrics-4-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.8rem;
    margin: 1.4rem 0;
    text-align: left;
}
.m4-card {
    background: #F8FAFC;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.9rem 1rem;
}
.m4-title {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}
.m4-value {
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--text-main);
    margin-top: 0.25rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── PROTOCOL DIRECTIVES ── */
.directives-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.5rem;
    margin-top: 1.2rem;
    box-shadow: 0 4px 15px -3px rgba(15, 23, 42, 0.03);
}
.directive-row {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    background: #F8FAFC;
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    color: #1E293B;
    line-height: 1.5;
    transition: transform 0.15s ease;
}
.directive-row:hover {
    transform: translateX(3px);
    border-color: #CBD5E1;
}
.directive-icon {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #EEF2FF;
    color: #4F46E5;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 800;
    flex-shrink: 0;
    margin-top: 0.1rem;
}

/* ── EXPLAINABLE AI BARS ── */
.fuzzy-var-block {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}
.fuzzy-var-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 0.8rem;
}
.mf-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0.45rem 0;
}
.mf-label {
    width: 85px;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: capitalize;
    flex-shrink: 0;
}
.mf-track {
    flex: 1;
    background: #F1F5F9;
    height: 8px;
    border-radius: 999px;
    overflow: hidden;
}
.mf-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #4F46E5, #06B6D4);
}
.mf-val {
    width: 48px;
    text-align: right;
    font-size: 0.75rem;
    font-weight: 700;
    color: #4F46E5;
    font-family: 'JetBrains Mono', monospace;
    flex-shrink: 0;
}

/* ── RULE CARDS ── */
.rule-card-active {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-left: 4px solid #16A34A;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
}
.rule-card-silent {
    background: #F8FAFC;
    border: 1px solid var(--border);
    border-left: 4px solid #CBD5E1;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.45rem;
    font-size: 0.8rem;
    color: var(--text-light);
}
.rule-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #14532D;
    margin-bottom: 0.5rem;
}
.rule-badges-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}
.r-chip {
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    font-size: 0.73rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.r-chip-omega { background: #DCFCE7; color: #15803D; }
.r-chip-z { background: #DBEAFE; color: #1D4ED8; }
.r-chip-contrib { background: #FEF3C7; color: #B45309; }

/* ── MATH FORMULA BOX ── */
.math-box {
    background: #0F172A;
    color: #F8FAFC;
    border-radius: 14px;
    padding: 1.4rem;
    margin: 1.2rem 0;
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* ── HISTORY CARDS ── */
.history-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem;
    text-align: center;
    box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.04);
}
.hist-score-tag {
    font-size: 2.4rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.03em;
}
.hist-label {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0.35rem 0 0.5rem 0;
}
.hist-specs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.3rem;
    font-size: 0.7rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border-subtle);
    padding-top: 0.5rem;
}

/* ── STREAMLIT WIDGET OVERRIDES ── */
div[data-testid="stSlider"] label {
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    color: #1E293B !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 1.8rem !important;
    font-size: 0.95rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    box-shadow: 0 8px 24px -4px rgba(79, 70, 229, 0.4) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 30px -4px rgba(79, 70, 229, 0.55) !important;
}
.stButton > button[kind="secondary"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    border: 1px solid var(--border) !important;
    background: #FFFFFF !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #4F46E5 !important;
    color: #4F46E5 !important;
}

/* ── FOOTER ── */
.app-footer {
    text-align: center;
    padding: 2.8rem 1rem 1.2rem 1rem;
    border-top: 1px solid var(--border);
    margin-top: 3.5rem;
    color: var(--text-light);
    font-size: 0.82rem;
    line-height: 1.8;
}
.app-footer a {
    color: #4F46E5;
    text-decoration: none;
    font-weight: 600;
}
.app-footer a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE INITIALIZATION ───────────────────────────────────────────────
if 'history' not in st.session_state:
    st.session_state.history = []
if 'engine' not in st.session_state:
    st.session_state.engine, st.session_state.variables = build_fitfuzzy_engine()

# Slider state keys
if 'input_sleep' not in st.session_state:
    st.session_state.input_sleep = 7.0
if 'input_soreness' not in st.session_state:
    st.session_state.input_soreness = 3.0
if 'input_stress' not in st.session_state:
    st.session_state.input_stress = 3.5
if 'input_time' not in st.session_state:
    st.session_state.input_time = 60
if 'input_rest_days' not in st.session_state:
    st.session_state.input_rest_days = 2
if 'input_goal' not in st.session_state:
    st.session_state.input_goal = "Maintenance"

engine    = st.session_state.engine
variables = st.session_state.variables


# ── NAVBAR ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar-container">
    <div class="brand-group">
        <div class="brand-icon-box">⚡</div>
        <div>
            <div class="brand-title">FITFUZZY AI</div>
            <div class="brand-subtitle">Sugeno Fuzzy Inference Engine</div>
        </div>
    </div>
    <div class="nav-badges">
        <span class="badge-pill badge-pill-emerald">● System Online</span>
        <span class="badge-pill badge-pill-purple">Sugeno FIS v2.0</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── HERO BANNER ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-card">
    <div class="hero-badge">🧬 Explainable Artificial Intelligence • Sports Physiology</div>
    <div class="hero-title">Precision Workout Prescriptions,<br/>Backed by Mathematical Rigor.</div>
    <div class="hero-desc">
        FitFuzzy transforms physiological fatigue signals, systemic stress markers, and schedule constraints
        into optimal workout intensities using a custom Sugeno Fuzzy Logic inference architecture — 
        with 100% white-box mathematical transparency.
    </div>
    <div class="hero-stats-grid">
        <div>
            <div class="h-stat-num">12</div>
            <div class="h-stat-label">Sugeno Rules</div>
        </div>
        <div>
            <div class="h-stat-num">5</div>
            <div class="h-stat-label">Physio Inputs</div>
        </div>
        <div>
            <div class="h-stat-num">6</div>
            <div class="h-stat-label">Prescription Tiers</div>
        </div>
        <div>
            <div class="h-stat-num">100%</div>
            <div class="h-stat-label">Explainable (XAI)</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── PRESET SCENARIOS BAR ───────────────────────────────────────────────────────
st.markdown('<div class="preset-bar-title">⚡ Quick Athletic Scenarios (One-Click Presets)</div>', unsafe_allow_html=True)
p1, p2, p3, p4, p5 = st.columns(5)

with p1:
    if st.button("🔥 Peak Readiness", use_container_width=True, help="High sleep, low soreness & stress, 90 min time"):
        st.session_state.input_sleep = 9.0
        st.session_state.input_soreness = 1.0
        st.session_state.input_stress = 2.0
        st.session_state.input_time = 90
        st.session_state.input_rest_days = 2
        st.session_state.input_goal = "Bulking"
        st.rerun()

with p2:
    if st.button("🛌 Heavy Fatigue / DOMS", use_container_width=True, help="Low sleep, high muscle soreness, overdue rest"):
        st.session_state.input_sleep = 4.0
        st.session_state.input_soreness = 8.5
        st.session_state.input_stress = 5.0
        st.session_state.input_time = 45
        st.session_state.input_rest_days = 1
        st.session_state.input_goal = "Maintenance"
        st.rerun()

with p3:
    if st.button("🧠 Stress Overdrive", use_container_width=True, help="Very high systemic stress, average sleep"):
        st.session_state.input_sleep = 5.0
        st.session_state.input_soreness = 3.5
        st.session_state.input_stress = 8.5
        st.session_state.input_time = 35
        st.session_state.input_rest_days = 2
        st.session_state.input_goal = "Cutting"
        st.rerun()

with p4:
    if st.button("⏱️ 25m Time-Crunch", use_container_width=True, help="Short training window, moderate recovery"):
        st.session_state.input_sleep = 7.0
        st.session_state.input_soreness = 3.5
        st.session_state.input_stress = 3.0
        st.session_state.input_time = 25
        st.session_state.input_rest_days = 2
        st.session_state.input_goal = "Body Recomposition"
        st.rerun()

with p5:
    if st.button("🎯 Baseline Routine", use_container_width=True, help="Balanced baseline: 7h sleep, moderate stress"):
        st.session_state.input_sleep = 7.0
        st.session_state.input_soreness = 3.0
        st.session_state.input_stress = 3.5
        st.session_state.input_time = 60
        st.session_state.input_rest_days = 2
        st.session_state.input_goal = "Maintenance"
        st.rerun()

st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)


# ── CORE 2-COLUMN WORKSPACE ────────────────────────────────────────────────────
col_inputs, col_results = st.columns([1, 1.25], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN: INPUT CONTROLS
# ══════════════════════════════════════════════════════════════════════════════
with col_inputs:
    # ── CARD 1: BIOLOGICAL READINESS ──
    st.markdown("""
    <div class="app-card">
        <div class="card-header-group">
            <h3 class="card-heading">🧬 Biological Recovery Markers</h3>
            <span class="card-tag">Physiological Inputs</span>
        </div>
    """, unsafe_allow_html=True)

    sleep_val = st.slider(
        "Sleep Quality & Duration (0 = Insomnia, 10 = Restorative)",
        min_value=0.0,
        max_value=10.0,
        value=float(st.session_state.input_sleep),
        step=0.5,
        help="Biological restoration index based on REM & deep sleep duration and perceived awakening freshness."
    )
    st.session_state.input_sleep = sleep_val

    # Dynamic sleep badge
    if sleep_val < 3.5:
        sleep_badge = ("🔴 Deficit / Sleep Deprivation", "#EF4444")
    elif sleep_val < 6.5:
        sleep_badge = ("🟡 Baseline / Average Rest", "#F59E0B")
    else:
        sleep_badge = ("🟢 Optimal Restorative Recovery", "#10B981")

    st.markdown(f"""
    <div style="font-size:0.75rem;font-weight:700;color:{sleep_badge[1]};margin-top:-0.4rem;margin-bottom:0.9rem;">
        {sleep_badge[0]} ({sleep_val}/10)
    </div>
    """, unsafe_allow_html=True)

    soreness_val = st.slider(
        "Delayed-Onset Muscle Soreness - DOMS (0 = Fresh, 10 = Severe Soreness)",
        min_value=0.0,
        max_value=10.0,
        value=float(st.session_state.input_soreness),
        step=0.5,
        help="Subjective assessment of muscular inflammation, localized tenderness, and movement restriction."
    )
    st.session_state.input_soreness = soreness_val

    if soreness_val < 3.0:
        sore_badge = ("🟢 Fully Primed / Minimal DOMS", "#10B981")
    elif soreness_val < 6.5:
        sore_badge = ("🟡 Moderate Muscle Fatigue", "#F59E0B")
    else:
        sore_badge = ("🔴 Severe Trauma / High Inflammation", "#EF4444")

    st.markdown(f"""
    <div style="font-size:0.75rem;font-weight:700;color:{sore_badge[1]};margin-top:-0.4rem;margin-bottom:0.2rem;">
        {sore_badge[0]} ({soreness_val}/10)
    </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CARD 2: MENTAL & SCHEDULE CAPACITY ──
    st.markdown("""
    <div class="app-card">
        <div class="card-header-group">
            <h3 class="card-heading">⏱️ Cognitive & Schedule Bandwidth</h3>
            <span class="card-tag">Temporal & CNS</span>
        </div>
    """, unsafe_allow_html=True)

    stress_val = st.slider(
        "Systemic Stress & Allostatic Load (0 = Zen, 10 = Overwhelmed)",
        min_value=0.0,
        max_value=10.0,
        value=float(st.session_state.input_stress),
        step=0.5,
        help="Non-training systemic stress including work demands, mental fatigue, and autonomic nervous system strain."
    )
    st.session_state.input_stress = stress_val

    time_val = st.slider(
        "Available Training Window (minutes)",
        min_value=10,
        max_value=120,
        value=int(st.session_state.input_time),
        step=5,
        help="Total dedicated time for warm-up, working volume, and post-session cooldown."
    )
    st.session_state.input_time = time_val

    rest_val = st.slider(
        "Days Elapsed Since Last Full Rest Day",
        min_value=0,
        max_value=10,
        value=int(st.session_state.input_rest_days),
        step=1,
        help="Consecutive training accumulation without a full physiological off-day."
    )
    st.session_state.input_rest_days = rest_val

    st.markdown("</div>", unsafe_allow_html=True)

    # ── CARD 3: STRATEGIC TARGETS ──
    st.markdown("""
    <div class="app-card">
        <div class="card-header-group">
            <h3 class="card-heading">🎯 Strategy & Context</h3>
            <span class="card-tag">Periodization</span>
        </div>
    """, unsafe_allow_html=True)

    goal_options = ["Maintenance", "Bulking", "Cutting", "Body Recomposition"]
    default_idx = goal_options.index(st.session_state.input_goal) if st.session_state.input_goal in goal_options else 0
    goal = st.selectbox(
        "Current Periodization Objective",
        goal_options,
        index=default_idx
    )
    st.session_state.input_goal = goal

    st.markdown("</div>", unsafe_allow_html=True)

    # ── ACTION BUTTON ──
    analyze_click = st.button("⚡ GENERATE WORKOUT PRESCRIPTION", type="primary", use_container_width=True)

    # ── REALTIME HUD MATRIX ──
    st.markdown(f"""
    <div class="app-card" style="padding:1.2rem;background:#F8FAFC;">
        <div style="font-size:0.72rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem;">
            📊 Live Assessment Telemetry
        </div>
        <div class="hud-grid">
            <div class="hud-item">
                <div class="hud-val" style="color:#4F46E5;">{sleep_val}</div>
                <div class="hud-lbl">Sleep Quality</div>
            </div>
            <div class="hud-item">
                <div class="hud-val" style="color:#F59E0B;">{soreness_val}</div>
                <div class="hud-lbl">Muscle Soreness</div>
            </div>
            <div class="hud-item">
                <div class="hud-val" style="color:#EF4444;">{stress_val}</div>
                <div class="hud-lbl">Systemic Stress</div>
            </div>
            <div class="hud-item">
                <div class="hud-val" style="color:#10B981;">{time_val}m</div>
                <div class="hud-lbl">Available Time</div>
            </div>
            <div class="hud-item">
                <div class="hud-val" style="color:#8B5CF6;">{rest_val}d</div>
                <div class="hud-lbl">Days Since Rest</div>
            </div>
            <div class="hud-item">
                <div class="hud-val" style="color:#0EA5E9;font-size:0.9rem;text-transform:uppercase;">{goal[:7]}</div>
                <div class="hud-lbl">Active Goal</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN: INFERENCE ENGINE & PRESCRIPTION DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with col_results:
    # Always evaluate live so changes immediately produce crisp results
    crisp = {
        'sleep': sleep_val,
        'soreness': soreness_val,
        'stress': stress_val,
        'time': time_val,
        'rest_days': rest_val
    }
    fuzz = {k: v.fuzzify(crisp[k]) for k, v in variables.items()}
    score, rules = engine.predict(crisp, fuzz)
    wtype, icon, desc, dur, tips = interpret_intensity(score)
    color = get_intensity_color(score)
    rpe = get_rpe_target(score)
    hr_zone = get_hr_zone(score)

    fired   = [r for r in rules if r['fired']]
    unfired = [r for r in rules if not r['fired']]

    # Record in history if button was clicked
    if analyze_click:
        st.session_state.history.insert(0, {
            'time': datetime.now().strftime("%H:%M:%S"),
            'type': wtype,
            'icon': icon,
            'score': score,
            'color': color,
            'sleep': sleep_val,
            'soreness': soreness_val,
            'stress': stress_val,
            'time_val': time_val,
            'rest_days': rest_val,
            'goal': goal
        })
        st.session_state.history = st.session_state.history[:6]

    # ── RESULT HERO CARD ──
    st.markdown(f"""
    <div class="result-box" style="border-top: 5px solid {color};">
        <span class="result-top-badge" style="background:{color}18;color:{color};border:1px solid {color}40;">
            {icon} Daily Prescription Tiers
        </span>
        <div class="score-circle-container" style="background: radial-gradient(circle, {color}15 0%, rgba(255,255,255,0) 70%); border: 3px solid {color};">
            <div class="score-number" style="color:{color};">{score:.0f}</div>
            <div class="score-denominator">/ 100 Index</div>
        </div>
        <div class="rec-title" style="color:{color};">
            {wtype}
        </div>
        <div class="rec-desc">
            {desc}
        </div>
        <div class="gauge-track">
            <div class="gauge-fill" style="width: {min(100, max(5, score))}%; background: linear-gradient(90deg, #4F46E5 0%, {color} 100%);"></div>
        </div>
        <div class="gauge-markers">
            <span>Rest (0)</span>
            <span>Recovery (28)</span>
            <span>Light (42)</span>
            <span>Moderate (58)</span>
            <span>Solid (74)</span>
            <span>Heavy (84+)</span>
        </div>
        <div class="metrics-4-grid">
            <div class="m4-card">
                <div class="m4-title">⏱️ Session Duration</div>
                <div class="m4-value" style="color:{color};">{dur}</div>
            </div>
            <div class="m4-card">
                <div class="m4-title">⚡ Perceived Exertion</div>
                <div class="m4-value">{rpe.split('(')[0].strip()}</div>
            </div>
            <div class="m4-card">
                <div class="m4-title">🎯 Target HR Zone</div>
                <div class="m4-value">{hr_zone.split(':')[0]}</div>
            </div>
            <div class="m4-card">
                <div class="m4-title">⚙️ Active Inference</div>
                <div class="m4-value">{len(fired)} of 12 Rules</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ACTIONABLE TACTICAL DIRECTIVES ──
    st.markdown("""
    <div class="directives-card">
        <div style="font-size:0.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">
            📋 Tactical Directives & Session Rules
        </div>
    """, unsafe_allow_html=True)

    for i, tip in enumerate(tips, 1):
        st.markdown(f"""
        <div class="directive-row">
            <div class="directive-icon">{i}</div>
            <div>{tip}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── EXPORT / SHARE BAR ──
    protocol_text = f"""FITFUZZY WORKOUT PRESCRIPTION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Intensity Index: {score:.1f}/100 ({wtype})
Target Duration: {dur}
RPE Guidance: {rpe}
Cardio Zone: {hr_zone}
Directives:
""" + "\n".join([f"- {t}" for t in tips])

    st.download_button(
        label="📥 Download Daily Prescription (TXT)",
        data=protocol_text,
        file_name=f"fitfuzzy_prescription_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )


# ── FULL-WIDTH DEEP DIVE TABS (EXPLAINABLE AI) ─────────────────────────────────
st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
st.markdown('<div class="preset-bar-title">🔬 Deep-Dive Architecture & Explainable AI (XAI)</div>', unsafe_allow_html=True)

tab_fuzz, tab_rules, tab_math, tab_hist, tab_science = st.tabs([
    "🧮 Fuzzification Membership (μ)",
    "⚙️ Sugeno Rule Engine",
    "📐 Mathematical Defuzzification",
    "📈 Session Analytics & History",
    "📚 Scientific Architecture"
])

# ── TAB 1: FUZZIFICATION ──
with tab_fuzz:
    st.markdown("""
    <div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:1.2rem;line-height:1.6;">
        Fuzzification maps crisp biological numbers into degrees of membership (<strong>μ ∈ [0.0, 1.0]</strong>)
        across standard Triangular and Trapezoidal membership functions defined for each variable.
    </div>
    """, unsafe_allow_html=True)

    fcol1, fcol2 = st.columns(2, gap="medium")
    vars_list = [
        ('sleep', 'Sleep Quality', sleep_val, '/ 10', '#4F46E5'),
        ('soreness', 'Muscle Soreness (DOMS)', soreness_val, '/ 10', '#F59E0B'),
        ('stress', 'Systemic Stress', stress_val, '/ 10', '#EF4444'),
        ('time', 'Available Time', time_val, 'min', '#10B981'),
        ('rest_days', 'Days Since Rest Day', rest_val, 'days', '#8B5CF6')
    ]

    for idx, (v_key, v_title, v_crisp, v_unit, v_col) in enumerate(vars_list):
        target_col = fcol1 if idx % 2 == 0 else fcol2
        with target_col:
            st.markdown(f"""
            <div class="fuzzy-var-block">
                <div class="fuzzy-var-header">
                    <span>{v_title}</span>
                    <span style="font-family:'JetBrains Mono';color:{v_col};">Input: {v_crisp} {v_unit}</span>
                </div>
            """, unsafe_allow_html=True)

            active_mfs = fuzz[v_key]
            for label_name, mu_val in active_mfs.items():
                pct = int(mu_val * 100)
                st.markdown(f"""
                <div class="mf-row">
                    <div class="mf-label">{label_name}</div>
                    <div class="mf-track">
                        <div class="mf-fill" style="width:{pct}%;background:{v_col};"></div>
                    </div>
                    <div class="mf-val" style="color:{v_col};">{mu_val:.3f}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 2: RULES ──
with tab_rules:
    st.markdown(f"""
    <div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:1.2rem;">
        Sugeno 0th-order and 1st-order expert rules. Firing strength <strong>ω</strong> is calculated using
        <strong>Fuzzy AND = min(μ)</strong> and <strong>Fuzzy OR = max(μ)</strong>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"#### Active Rules ({len(fired)} Fired)")
    if fired:
        for r in sorted(fired, key=lambda x: -x['omega']):
            st.markdown(f"""
            <div class="rule-card-active">
                <div class="rule-title">⚡ {r['name']}</div>
                <div class="rule-badges-group">
                    <span class="r-chip r-chip-omega">Firing Strength (ω) = {r['omega']:.4f}</span>
                    <span class="r-chip r-chip-z">Consequent (z) = {r['z_i']:.1f}</span>
                    <span class="r-chip r-chip-contrib">Weighted Impact = {r['contribution']:.3f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No expert rules fired with strength > 0.01 for this combination.")

    if unfired:
        with st.expander(f"Silent / Inactive Rules ({len(unfired)} Inactive)", expanded=False):
            for r in unfired:
                st.markdown(f"""
                <div class="rule-card-silent">
                    ⚪ {r['name']} <span style="float:right;font-family:'JetBrains Mono';">ω = {r['omega']:.4f}</span>
                </div>
                """, unsafe_allow_html=True)

# ── TAB 3: MATHEMATICAL DEFUZZIFICATION ──
with tab_math:
    numerator_sum = sum(r['omega'] * r['z_i'] for r in rules)
    denominator_sum = sum(r['omega'] for r in rules)

    st.markdown("""
    ### 📐 Sugeno Weighted Average Defuzzification
    Unlike Mamdani systems that require continuous centroid integration over complex geometric polygons, 
    the **Sugeno Fuzzy Model** computes the final crisp output via an exact weighted average:
    """)

    st.latex(r"Y = \frac{\sum_{i=1}^{N} \omega_i \cdot z_i}{\sum_{i=1}^{N} \omega_i}")

    st.markdown(f"""
    <div class="math-box">
        <div><strong>Numerator (Weighted Sum of Singletons):</strong></div>
        <div style="color:#A7F3D0;margin:0.4rem 0;">Σ (ω_i × z_i) = {numerator_sum:.4f}</div>
        <br/>
        <div><strong>Denominator (Sum of Firing Weights):</strong></div>
        <div style="color:#A5B4FC;margin:0.4rem 0;">Σ ω_i = {denominator_sum:.4f}</div>
        <br/>
        <div><strong>Final Crisp Score:</strong></div>
        <div style="color:#FDE047;font-size:1.15rem;margin-top:0.4rem;">
            Y = {numerator_sum:.4f} / {denominator_sum:.4f} = <strong>{score:.2f}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── TAB 4: SESSION ANALYTICS & HISTORY ──
with tab_hist:
    h_col1, h_col2 = st.columns([4, 1])
    with h_col1:
        st.markdown("### 📈 Recent Assessments Log")
        st.markdown(f"Tracking **{len(st.session_state.history)}** assessments in current browser session.")
    with h_col2:
        if st.button("🗑️ Clear Log", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    if st.session_state.history:
        hcols = st.columns(min(len(st.session_state.history), 4))
        for h_idx, item in enumerate(st.session_state.history[:4]):
            with hcols[h_idx]:
                st.markdown(f"""
                <div class="history-card" style="border-top: 4px solid {item['color']};">
                    <div class="hist-score-tag" style="color:{item['color']};">{item['score']:.0f}</div>
                    <div class="hist-label" style="color:{item['color']};">{item['icon']} {item['type']}</div>
                    <div style="font-size:0.75rem;color:#94A3B8;margin-bottom:0.5rem;">{item['time']} • {item['goal']}</div>
                    <div class="hist-specs">
                        <span>💤 Sleep {item['sleep']}</span>
                        <span>💥 Sore {item['soreness']}</span>
                        <span>🧠 Stress {item['stress']}</span>
                        <span>⏱️ {item['time_val']}m</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No prior assessments logged yet. Adjust sliders and click 'Generate Workout Prescription' to start tracking.")

# ── TAB 5: SCIENTIFIC ARCHITECTURE ──
with tab_science:
    st.markdown("""
    ### 🔬 Why Fuzzy Inference Over Black-Box Machine Learning?
    
    1. **Safety & Explainability:** In exercise physiology, recommendations must be transparent. If an athlete is prescribed Complete Rest, they can trace exactly which rule triggered it (e.g. `High Soreness + High Systemic Stress`).
    2. **Graceful Degradation:** Real human biology does not operate on crisp binary thresholds. Moving from 6.9 hours to 7.1 hours of sleep changes membership degrees continuously without jarring discontinuity.
    3. **Zero Cold-Start / Training Bias:** No multi-gigabyte neural network training or hallucination risks. The system embodies proven sports science and periodization rules directly.
    
    ---
    
    #### Linguistic Universe of Discourse:
    - **Sleep Quality (0 - 10):** Poor [0, 4.5] | Average [3.0, 7.0] | Good [6.0, 10.0]
    - **Muscle Soreness (0 - 10):** Low [0, 4.0] | Moderate [2.5, 7.5] | High [6.0, 10.0]
    - **Systemic Stress (0 - 10):** Low [0, 4.5] | Moderate [3.0, 7.0] | High [6.0, 10.0]
    - **Available Time (0 - 120 min):** Short [0, 35m] | Moderate [25, 65m] | Long [55, 120m]
    - **Days Since Rest (0 - 10 days):** Fresh [0, 3d] | Moderate [2, 6d] | Overdue [5, 10d]
    """)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    <strong>FitFuzzy AI — Explainable Workout Prescription System</strong><br/>
    Sugeno 0th/1st-Order Fuzzy Inference System • Pure Python Engine (Zero ML Dependencies)<br/>
    Crafted for National Institute of Technology (NIT) Silchar, Electronics & Communication Engineering (ECE 2027)<br/>
    Open Source under MIT License • <a href="https://github.com/karankaushik012345/fitfuzzy" target="_blank">GitHub Repository</a>
</div>
""", unsafe_allow_html=True)
