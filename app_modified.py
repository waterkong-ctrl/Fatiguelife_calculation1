# DESIGN V11 - 모노파일 설명/해역별 파라미터 제목 반영본
# 실행: streamlit run streamlit_design_v11.py

import base64
import copy
import html
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st


# =============================================================================
# 1. 기본 설정값
# =============================================================================
GRAVITY = 9.81
NUM_Z = 200
NUM_T = 400

DEFAULT_MONOPILE = {"D": 5.0, "thickness": 0.06, "L": 30.0}
DEFAULT_FLUID = {"rho": 1025.0, "Cd": 1.0, "Cm": 2.0}
DEFAULT_FATIGUE = {"A": 5.8e11, "m": 3.0}

DEFAULT_LOCATIONS = {
    "west": {
        "name": "서해",
        "h": 15.0,
        "Uc": 0.3,
        "sea_states": [
            {"name": "SS1", "H": 0.6, "T": 4.5, "days_per_year": 222},
            {"name": "SS2", "H": 1.3, "T": 6.0, "days_per_year": 102},
            {"name": "SS3", "H": 2.3, "T": 7.5, "days_per_year": 38},
            {"name": "SS4", "H": 3.5, "T": 9.0, "days_per_year": 3},
        ],
    },
    "south": {
        "name": "남해",
        "h": 20.0,
        "Uc": 0.5,
        "sea_states": [
            {"name": "SS1", "H": 0.7, "T": 5.0, "days_per_year": 179},
            {"name": "SS2", "H": 1.4, "T": 6.5, "days_per_year": 132},
            {"name": "SS3", "H": 2.6, "T": 8.5, "days_per_year": 52},
            {"name": "SS4", "H": 4.0, "T": 10.0, "days_per_year": 2},
        ],
    },
    "east": {
        "name": "동해",
        "h": 25.0,
        "Uc": 0.5,
        "sea_states": [
            {"name": "SS1", "H": 0.8, "T": 5.0, "days_per_year": 155},
            {"name": "SS2", "H": 1.5, "T": 7.0, "days_per_year": 145},
            {"name": "SS3", "H": 2.8, "T": 9.0, "days_per_year": 61},
            {"name": "SS4", "H": 4.5, "T": 11.0, "days_per_year": 5},
        ],
    },
}

SEA_LAYOUT = ["west", "south", "east"]


# =============================================================================
# 2. 공통 UI 스타일
# =============================================================================
def apply_page_style() -> None:
    st.set_page_config(
        page_title="해역별 모노파일 예상 피로수명 계산",
        page_icon="🌊",
        layout="wide",
    )

    st.markdown(
        """
        <style>
            :root {
                --navy: #1E293B;
                --blue: #38BDF8;
                --blue-dark: #0284C7;
                --cyan-soft: #F0F9FF;
                --slate-50: #F8FAFC;
                --slate-100: #F1F5F9;
                --slate-200: #E2E8F0;
                --slate-500: #64748B;
                --slate-600: #475569;
                --white: #FFFFFF;
                --shadow: 0 14px 35px rgba(56, 189, 248, 0.10);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(186, 230, 253, 0.55), transparent 34rem),
                    radial-gradient(circle at top right, rgba(224, 242, 254, 0.75), transparent 28rem),
                    linear-gradient(180deg, #F8FCFF 0%, #FFFFFF 46%, #F0F9FF 100%);
            }

            .main .block-container {
                padding-top: 1.35rem;
                padding-bottom: 3rem;
                max-width: 1320px;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #F0F9FF 0%, #E0F2FE 100%);
                border-right: 1px solid #BAE6FD;
            }

            section[data-testid="stSidebar"] * {
                color: #1E293B !important;
            }

            section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
            section[data-testid="stSidebar"] label,
            section[data-testid="stSidebar"] .stCaptionContainer {
                color: #475569 !important;
            }

            section[data-testid="stSidebar"] input {
                color: #0F172A !important;
                background: #FFFFFF !important;
                border-radius: 10px !important;
            }

            section[data-testid="stSidebar"] div[data-baseweb="radio"] label {
                background: rgba(255,255,255,0.86);
                border: 1px solid #BAE6FD;
                border-radius: 999px;
                padding: 0.35rem 0.55rem;
                margin-right: 0.2rem;
            }

            div.stButton > button:first-child {
                border-radius: 14px;
                height: 3rem;
                font-weight: 800;
                border: 0;
                box-shadow: 0 10px 22px rgba(14, 165, 233, 0.14);
            }

            section[data-testid="stSidebar"] div.stButton button[kind="primary"],
            section[data-testid="stSidebar"] div.stButton button[data-testid="stBaseButton-primary"] {
                background: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 100%) !important;
                color: #FFFFFF !important;
                border: 1px solid #7DD3FC !important;
                box-shadow: 0 10px 22px rgba(14, 165, 233, 0.18) !important;
            }

            section[data-testid="stSidebar"] div.stButton button[kind="secondary"],
            section[data-testid="stSidebar"] div.stButton button[data-testid="stBaseButton-secondary"] {
                background: #FFFFFF !important;
                color: #475569 !important;
                border: 1px solid #BAE6FD !important;
                box-shadow: none !important;
            }

            h1, h2, h3 {
                letter-spacing: -0.045em;
                color: var(--navy);
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 18px !important;
                border-color: #E2E8F0 !important;
                box-shadow: 0 8px 24px rgba(14, 165, 233, 0.06);
                background: rgba(255, 255, 255, 0.88);
            }

            .section-card {
                padding: 1.25rem 1.35rem;
                border: 1px solid rgba(226, 232, 240, 0.95);
                border-radius: 22px;
                background: rgba(255, 255, 255, 0.92);
                box-shadow: var(--shadow);
                margin-bottom: 0.85rem;
            }

            .soft-card {
                padding: 1rem;
                border-radius: 18px;
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
            }

            .hint-text {
                font-size: 0.96rem;
                line-height: 1.72;
                color: var(--slate-600);
            }

            .selected-sea {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.48rem 0.85rem;
                border-radius: 999px;
                background: linear-gradient(135deg, #E0F2FE, #F0F9FF);
                color: #0284C7;
                border: 1px solid #BAE6FD;
                font-weight: 800;
                margin-bottom: 0.55rem;
                box-shadow: 0 8px 16px rgba(14, 165, 233, 0.10);
            }

            .compact-calc-table th {
                background:#F0F9FF;
                border:1px solid #CBD5E1;
                padding:9px 15px;
                text-align:center !important;
                white-space:nowrap;
                vertical-align:middle !important;
                color: #075985;
            }

            .compact-calc-table td {
                border:1px solid #CBD5E1;
                padding:9px 15px;
                text-align:center !important;
                white-space:nowrap;
                vertical-align:middle !important;
                color: #334155;
            }

            .hero-box {
                position: relative;
                overflow: hidden;
                padding: 1.75rem 1.9rem;
                border-radius: 28px;
                background:
                    linear-gradient(135deg, #FFFFFF 0%, #E0F7FF 48%, #BAE6FD 100%);
                border: 1px solid #BAE6FD;
                box-shadow: 0 22px 52px rgba(14, 165, 233, 0.14);
                margin-bottom: 1rem;
            }

            .hero-box:after {
                content: "";
                position: absolute;
                width: 18rem;
                height: 18rem;
                right: -5rem;
                top: -6rem;
                background: radial-gradient(circle, rgba(56,189,248,0.23), transparent 62%);
                border-radius: 999px;
            }

            .hero-kicker {
                display: inline-block;
                position: relative;
                z-index: 1;
                padding: 0.32rem 0.7rem;
                border-radius: 999px;
                background: #F0F9FF;
                border: 1px solid #BAE6FD;
                color: #0284C7;
                font-size: 0.82rem;
                font-weight: 800;
                margin-bottom: 0.65rem;
            }

            .hero-title {
                position: relative;
                z-index: 1;
                font-size: clamp(1.85rem, 3vw, 2.55rem);
                font-weight: 900;
                color: #0F172A;
                letter-spacing: -0.06em;
                margin-bottom: 0.45rem;
            }

            .hero-caption {
                position: relative;
                z-index: 1;
                max-width: 820px;
                font-size: 1.02rem;
                color: #475569;
                line-height: 1.75;
            }

            .step-strip {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 0.85rem;
                margin: 1rem 0 1.35rem 0;
            }

            .step-card {
                padding: 1rem 1.05rem;
                border-radius: 20px;
                border: 1px solid rgba(219, 234, 254, 0.95);
                background: rgba(255, 255, 255, 0.92);
                box-shadow: 0 10px 28px rgba(14, 165, 233, 0.08);
            }

            .step-no {
                font-size: 0.78rem;
                font-weight: 900;
                color: #0EA5E9;
                margin-bottom: 0.28rem;
            }

            .step-name {
                font-size: 1.05rem;
                font-weight: 900;
                color: #0F172A;
            }

            .step-desc {
                margin-top: 0.28rem;
                font-size: 0.9rem;
                color: #64748B;
                line-height: 1.58;
            }

            .summary-pill {
                display: inline-block;
                margin: 0.18rem 0.25rem 0.18rem 0;
                padding: 0.42rem 0.72rem;
                border-radius: 999px;
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                color: #334155;
                font-size: 0.9rem;
                font-weight: 700;
            }

            .guide-box {
                padding: 1rem 1.05rem;
                border-radius: 18px;
                background: linear-gradient(135deg, #F8FAFC, #F0F9FF);
                border: 1px solid #E0F2FE;
                color: #475569;
                line-height: 1.72;
                font-size: 0.95rem;
            }

            .metric-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.9rem;
                margin: 0.7rem 0 1rem 0;
            }

            .metric-card {
                padding: 1.15rem 1.2rem;
                border-radius: 22px;
                background: #FFFFFF;
                border: 1px solid #E0F2FE;
                box-shadow: 0 14px 32px rgba(14, 165, 233, 0.10);
            }

            .metric-label {
                color: #64748B;
                font-size: 0.9rem;
                font-weight: 800;
                margin-bottom: 0.45rem;
            }

            .metric-value {
                color: #0284C7;
                font-size: 1.85rem;
                font-weight: 900;
                letter-spacing: -0.04em;
            }

            .result-badge {
                display: inline-block;
                padding: 0.45rem 0.78rem;
                border-radius: 999px;
                background: #DCFCE7;
                color: #166534;
                border: 1px solid #BBF7D0;
                font-weight: 850;
                margin-bottom: 0.65rem;
            }



            .sidebar-mini-card {
                padding: 0.75rem 0.8rem;
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid #BAE6FD;
                margin: 0.6rem 0;
                box-shadow: 0 8px 20px rgba(14, 165, 233, 0.08);
            }

            .sidebar-chip {
                display: inline-block;
                padding: 0.28rem 0.52rem;
                margin: 0.14rem 0.1rem 0.14rem 0;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.85);
                border: 1px solid #BAE6FD;
                font-size: 0.78rem;
                font-weight: 800;
                color: #0284C7 !important;
            }

            .review-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .review-card {
                padding: 1.1rem 1.15rem;
                border-radius: 22px;
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                box-shadow: 0 12px 30px rgba(14, 165, 233, 0.08);
            }

            .review-card.fixed { border-top: 5px solid #64748B; }
            .review-card.user { border-top: 5px solid #38BDF8; }

            .review-card-title {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.5rem;
                margin-bottom: 0.45rem;
            }

            .review-card-title strong {
                color: #0F172A;
                font-size: 1.05rem;
                letter-spacing: -0.03em;
            }

            .review-tag {
                display: inline-block;
                padding: 0.26rem 0.55rem;
                border-radius: 999px;
                font-size: 0.74rem;
                font-weight: 900;
            }

            .review-tag.fixed {
                color: #475569;
                background: #F1F5F9;
                border: 1px solid #CBD5E1;
            }

            .review-tag.user {
                color: #0284C7;
                background: #F0F9FF;
                border: 1px solid #BAE6FD;
            }

            .value-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9rem;
            }

            .value-table tr:not(:last-child) { border-bottom: 1px solid #E2E8F0; }

            .value-table td {
                padding: 0.34rem 0.15rem;
                vertical-align: middle;
            }

            .value-table td:first-child {
                color: #64748B;
                font-weight: 800;
                width: 46%;
            }

            .value-table td:last-child {
                color: #0F172A;
                font-weight: 900;
                text-align: right;
            }


            .sidebar-fixed-note {
                margin: 0.55rem 0 0.85rem 0;
                padding: 0.58rem 0.72rem;
                border-radius: 13px;
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid #BAE6FD;
                color: #475569 !important;
                font-size: 0.82rem;
                line-height: 1.6;
            }

            .condition-layout {
                display: block;
                margin-bottom: 0.55rem;
            }

            .user-param-card {
                padding: 0.88rem 1rem 0.78rem 1rem;
                border-radius: 20px;
                background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
                border: 1px solid #BAE6FD;
                box-shadow: 0 10px 24px rgba(14, 165, 233, 0.08);
                border-top: 4px solid #38BDF8;
            }

            .inline-fixed-note {
                margin-top: 0.55rem;
                padding: 0.48rem 0.62rem;
                border-radius: 12px;
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                color: #64748B;
                font-size: 0.84rem;
                line-height: 1.55;
            }

            .inline-fixed-note b {
                color: #334155;
            }

            .inline-fixed-note .label {
                display: inline-block;
                margin-right: 0.45rem;
                color: #475569;
                font-weight: 900;
            }

            @media (max-width: 900px) {
                .step-strip, .metric-grid, .review-grid { grid-template-columns: 1fr; }
                .hero-box { padding: 1.35rem; }
            }

            .process-flow {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.8rem;
                margin: 0.75rem 0 1.1rem 0;
            }

            .process-flow-card {
                padding: 0.9rem 0.95rem;
                border-radius: 18px;
                background: linear-gradient(180deg, #FFFFFF 0%, #F0F9FF 100%);
                border: 1px solid #BAE6FD;
                box-shadow: 0 10px 24px rgba(14, 165, 233, 0.08);
                min-height: 108px;
            }

            .process-step-no {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 28px;
                height: 28px;
                border-radius: 999px;
                background: #E0F2FE;
                color: #0369A1;
                font-weight: 900;
                font-size: 0.85rem;
                margin-bottom: 0.45rem;
            }

            .process-step-title {
                font-weight: 900;
                color: #0F172A;
                font-size: 1rem;
                margin-bottom: 0.18rem;
            }

            .process-step-desc {
                color: #64748B;
                font-size: 0.86rem;
                line-height: 1.45;
            }

            .formula-card {
                padding: 0.85rem 1rem;
                border-radius: 16px;
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                margin: 0.45rem 0 0.75rem 0;
            }

            .formula-card-title {
                font-size: 0.9rem;
                font-weight: 900;
                color: #0369A1;
                margin-bottom: 0.35rem;
            }

            .formula-line {
                padding: 0.42rem 0.55rem;
                margin: 0.32rem 0;
                border-radius: 10px;
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                color: #334155;
                font-size: 0.94rem;
            }

            .calc-summary-card {
                padding: 0.9rem 1rem;
                border-radius: 18px;
                background: linear-gradient(135deg, #ECFEFF 0%, #F0F9FF 100%);
                border: 1px solid #BAE6FD;
                margin: 0.6rem 0 0.8rem 0;
            }

            .calc-summary-title {
                color: #0369A1;
                font-weight: 900;
                margin-bottom: 0.35rem;
            }

            .calc-summary-text {
                color: #475569;
                line-height: 1.6;
                font-size: 0.95rem;
            }

            div[data-testid="stExpander"] {
                border: 1px solid #BAE6FD !important;
                border-radius: 18px !important;
                background: rgba(255,255,255,0.90) !important;
                box-shadow: 0 8px 22px rgba(14, 165, 233, 0.06) !important;
                margin-bottom: 0.65rem;
            }

            div[data-testid="stExpander"] summary {
                font-weight: 900 !important;
                color: #0F172A !important;
                font-size: 1.02rem !important;
            }

            @media (max-width: 900px) {
                .process-flow {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }


            /* DESIGN V10: 답답함 줄이기 - 여백, 글씨 굵기, 카드 밀도 조정 */
            .main .block-container {
                padding-top: 1.6rem;
                max-width: 1240px;
            }

            h1, h2, h3, h4, h5, h6 {
                font-weight: 650 !important;
                letter-spacing: -0.035em !important;
            }

            .hero-box {
                padding: 1.45rem 1.65rem !important;
                border-radius: 24px !important;
                box-shadow: 0 14px 34px rgba(14, 165, 233, 0.09) !important;
                margin-bottom: 1.2rem !important;
            }

            .hero-kicker {
                font-weight: 600 !important;
                letter-spacing: 0.02em;
            }

            .hero-title {
                font-size: clamp(1.65rem, 2.5vw, 2.2rem) !important;
                font-weight: 650 !important;
                letter-spacing: -0.04em !important;
            }

            .hero-caption {
                font-size: 0.98rem !important;
                line-height: 1.65 !important;
            }

            .step-strip { display: none !important; }

            .section-card,
            .review-card,
            .metric-card,
            .user-param-card,
            .formula-card,
            .calc-summary-card,
            .process-flow-card {
                box-shadow: 0 8px 22px rgba(14, 165, 233, 0.055) !important;
            }

            .user-param-card {
                padding: 0.8rem 0.9rem !important;
                border-radius: 18px !important;
            }

            .value-table td {
                padding: 0.28rem 0.12rem !important;
                font-size: 0.88rem !important;
            }

            .value-table td:first-child { font-weight: 600 !important; }
            .value-table td:last-child { font-weight: 650 !important; }

            .sidebar-section {
                padding: 0.78rem 0.8rem;
                border-radius: 16px;
                background: rgba(255,255,255,0.72);
                border: 1px solid #BAE6FD;
                margin: 0.65rem 0 0.85rem 0;
            }

            .sidebar-section-title {
                color: #0F172A !important;
                font-size: 0.96rem;
                font-weight: 650;
                margin-bottom: 0.45rem;
            }

            .sidebar-fixed-note {
                margin: 0.35rem 0 0.2rem 0 !important;
                padding: 0.48rem 0.62rem !important;
                font-size: 0.78rem !important;
                background: rgba(255, 255, 255, 0.58) !important;
                box-shadow: none !important;
            }

            .calc-flow-simple {
                padding: 1rem 1.05rem;
                border-radius: 18px;
                background: #FFFFFF;
                border: 1px solid #E0F2FE;
                margin: 0.75rem 0 1rem 0;
            }

            .calc-flow-line {
                display: flex;
                align-items: center;
                gap: 0.55rem;
                flex-wrap: wrap;
                color: #475569;
                font-size: 0.95rem;
                line-height: 1.7;
            }

            .calc-chip {
                display: inline-block;
                padding: 0.34rem 0.62rem;
                border-radius: 999px;
                background: #F0F9FF;
                border: 1px solid #BAE6FD;
                color: #0369A1;
                font-weight: 600;
            }

            .calc-arrow {
                color: #94A3B8;
                font-weight: 400;
            }

            .formula-card-title,
            .calc-summary-title,
            div[data-testid="stExpander"] summary {
                font-weight: 650 !important;
            }

            .formula-line {
                font-size: 0.9rem !important;
                padding: 0.35rem 0.5rem !important;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, caption: str | None = None) -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)


def render_card_start() -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)


def render_card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# 3. 계산 함수
# =============================================================================
def solve_wave_number(T: float, h: float) -> float:
    omega = 2 * np.pi / T
    k = omega**2 / GRAVITY

    for _ in range(100):
        f = GRAVITY * k * np.tanh(k * h) - omega**2
        df = GRAVITY * np.tanh(k * h) + GRAVITY * k * h * (1 / np.cosh(k * h)) ** 2
        k -= f / df

    return k


def section_properties(D: float, t: float) -> tuple[float, float]:
    d_inner = D - 2 * t
    I = (np.pi / 64) * (D**4 - d_inner**4)
    c = D / 2
    return I, c


def wave_kinematics(z, time_value, H, T, h, k, Uc):
    a = H / 2
    omega = 2 * np.pi / T
    shape = np.cosh(k * (z + h)) / np.sinh(k * h)
    u = a * omega * shape * np.cos(omega * time_value) + Uc
    du = -a * omega**2 * shape * np.sin(omega * time_value)
    return u, du


def morison(u, du, D, rho, Cd, Cm):
    drag = 0.5 * rho * Cd * D * u * np.abs(u)
    inertia = rho * Cm * (np.pi * D**2 / 4) * du
    return drag + inertia


def sn_cycles(delta_sigma: float, A: float, m: float) -> float:
    if delta_sigma <= 0:
        return np.inf
    return A / (delta_sigma**m)


def cycles_per_year(days: float, T: float) -> float:
    return days * 24 * 3600 / T


def analyze_location(monopile: dict, fluid: dict, fatigue: dict, loc: dict):
    h = loc["h"]
    Uc = loc["Uc"]
    total_damage = 0.0
    details = []

    for sea_state in loc["sea_states"]:
        H = sea_state["H"]
        T = sea_state["T"]

        z = np.linspace(-h, 0, NUM_Z)
        time_array = np.linspace(0, T, NUM_T)
        k = solve_wave_number(T, h)

        moment_time_history = []
        for time_value in time_array:
            u, du = wave_kinematics(z, time_value, H, T, h, k, Uc)
            force = morison(u, du, monopile["D"], fluid["rho"], fluid["Cd"], fluid["Cm"])
            moment = np.trapezoid(force * (z + h), z)
            moment_time_history.append(moment)

        moment_time_history = np.array(moment_time_history)
        I, c = section_properties(monopile["D"], monopile["thickness"])
        stress_mpa = moment_time_history * c / I / 1e6

        delta_sigma = np.max(stress_mpa) - np.min(stress_mpa)
        fatigue_cycles = sn_cycles(delta_sigma, fatigue["A"], fatigue["m"])
        annual_cycles = cycles_per_year(sea_state["days_per_year"], T)
        damage = annual_cycles / fatigue_cycles

        total_damage += damage
        details.append(
            {
                "해상상태": sea_state["name"],
                "응력범위(MPa)": float(delta_sigma),
                "연간손상도": float(damage),
            }
        )

    life = np.inf if total_damage <= 0 else 1 / total_damage
    return life, total_damage, details


def validate_inputs(monopile: dict, fluid: dict) -> list[str]:
    errors = []

    if monopile["D"] <= 0:
        errors.append("직경 D는 0보다 커야 합니다.")
    if monopile["thickness"] <= 0:
        errors.append("두께 t는 0보다 커야 합니다.")
    if monopile["thickness"] * 2 >= monopile["D"]:
        errors.append("두께 t는 직경 D의 절반보다 작아야 합니다. (D > 2t)")
    if monopile["L"] <= 0:
        errors.append("파일 길이 L은 0보다 커야 합니다.")
    if fluid["rho"] <= 0:
        errors.append("해수 밀도 rho는 0보다 커야 합니다.")
    if fluid["Cd"] <= 0:
        errors.append("항력계수 Cd는 0보다 커야 합니다.")
    if fluid["Cm"] <= 0:
        errors.append("관성계수 Cm는 0보다 커야 합니다.")

    return errors


# =============================================================================
# 4. 지도 및 이미지 UI
# =============================================================================
def point_in_polygon(lon: float, lat: float, polygon: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(polygon) - 1

    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i

    return inside


def render_korea_sea_map(selected_key: str | None):
    sea_points = {
        "west": {"lon": 125.1, "lat": 36.6, "label": "서해"},
        "south": {"lon": 127.5, "lat": 34.0, "label": "남해"},
        "east": {"lon": 129.6, "lat": 36.8, "label": "동해"},
    }

    sea_click_polygons = {
        "west": [(123.4, 34.0), (126.6, 34.0), (126.7, 35.0), (126.6, 36.0), (126.4, 37.0), (126.3, 38.2), (125.8, 39.1), (123.6, 39.1), (123.4, 34.0)],
        "south": [(125.4, 32.8), (129.9, 32.8), (130.1, 33.8), (129.7, 34.5), (128.9, 34.9), (127.5, 35.0), (126.3, 34.8), (125.6, 34.2), (125.4, 32.8)],
        "east": [(128.0, 34.4), (131.8, 34.4), (131.9, 35.6), (131.8, 36.8), (131.5, 38.0), (130.9, 39.3), (129.4, 39.5), (128.5, 38.8), (128.1, 37.6), (128.0, 34.4)],
    }

    fig = go.Figure()

    for sea_key in SEA_LAYOUT:
        point = sea_points[sea_key]
        fig.add_trace(
            go.Scattermapbox(
                lon=[point["lon"]],
                lat=[point["lat"]],
                mode="text",
                text=[point["label"]],
                textposition="middle center",
                textfont=dict(
                    size=24,
                    color="#0B4F9C" if sea_key == selected_key else "#1F1F1F",
                ),
                customdata=[sea_key],
                hovertemplate="%{text} 선택<extra></extra>",
                showlegend=False,
            )
        )

    click_lons, click_lats, click_keys = [], [], []
    for sea_key in SEA_LAYOUT:
        polygon = sea_click_polygons[sea_key]
        lons = [p[0] for p in polygon]
        lats = [p[1] for p in polygon]

        lon_values = np.arange(min(lons), max(lons) + 1e-9, 0.12)
        lat_values = np.arange(min(lats), max(lats) + 1e-9, 0.12)

        for lon in lon_values:
            for lat in lat_values:
                if point_in_polygon(float(lon), float(lat), polygon):
                    click_lons.append(float(lon))
                    click_lats.append(float(lat))
                    click_keys.append(sea_key)

    fig.add_trace(
        go.Scattermapbox(
            lon=click_lons,
            lat=click_lats,
            mode="markers",
            marker=dict(size=20, color="rgba(0, 0, 0, 0.0)"),
            customdata=click_keys,
            hovertemplate="클릭해서 해역 선택<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        mapbox=dict(style="carto-positron", center=dict(lon=127.8, lat=36.0), zoom=5.35),
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        key="korea_sea_map",
        on_select="rerun",
        selection_mode="points",
        config={"displayModeBar": False},
    )

    selection = {}
    if isinstance(event, dict):
        selection = event.get("selection", {})
    elif hasattr(event, "selection"):
        selection = event.selection

    points = selection.get("points", []) if isinstance(selection, dict) else getattr(selection, "points", [])
    if not points:
        return None

    customdata = points[0].get("customdata")
    return customdata if customdata in SEA_LAYOUT else None


def render_fixed_height_image(image_path: Path, height: int = 420) -> None:
    if not image_path.exists():
        st.info("이미지 파일이 없습니다. `assets/monopile_intro.png` 경로를 확인하세요.")
        return

    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <div style="height:{height}px; overflow:hidden; border-radius:14px; background:#F8FAFC; border:1px solid #E5E7EB;">
            <img
                src="data:image/png;base64,{encoded}"
                style="width:100%; height:100%; object-fit:contain; object-position:center;"
                alt="해상풍력 모노파일"
            >
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_monopile_parameter_preview(D: float, thickness: float, L: float, height: int = 420) -> None:
    display_d = max(float(D), 0.1)
    display_t = max(float(thickness), 0.001)
    display_l = max(float(L), 1.0)

    pile_height = min(max(display_l * 5.0, 120.0), 300.0)
    pile_width = min(max(display_d * 16.0, 36.0), 130.0)
    wall_width = min(max(display_t * 420.0, 4.0), pile_width / 3.0)

    center_x = 130
    seabed_y = 335
    top_y = seabed_y - pile_height
    left_x = center_x - pile_width / 2
    right_x = center_x + pile_width / 2

    fig = go.Figure()

    fig.add_shape(type="rect", x0=left_x, x1=right_x, y0=top_y, y1=seabed_y, line=dict(color="#334155", width=2), fillcolor="#CBD5E1")
    fig.add_shape(type="rect", x0=left_x, x1=left_x + wall_width, y0=top_y, y1=seabed_y, line=dict(width=0), fillcolor="#64748B")
    fig.add_shape(type="rect", x0=right_x - wall_width, x1=right_x, y0=top_y, y1=seabed_y, line=dict(width=0), fillcolor="#64748B")
    fig.add_shape(type="line", x0=left_x, x1=right_x, y0=top_y - 22, y1=top_y - 22, line=dict(color="#0F172A", width=3))
    fig.add_shape(type="line", x0=right_x + 24, x1=right_x + 24, y0=top_y, y1=seabed_y, line=dict(color="#0F172A", width=3))
    fig.add_shape(type="line", x0=45, x1=220, y0=seabed_y, y1=seabed_y, line=dict(color="#A16207", width=8))

    fig.add_annotation(x=center_x, y=top_y - 42, text=f"직경 D = {D:.2f} m", showarrow=False, font=dict(size=13))
    fig.add_annotation(x=right_x + 62, y=(top_y + seabed_y) / 2, text=f"파일 길이 L = {L:.1f} m", showarrow=False, textangle=90, font=dict(size=13))
    fig.add_annotation(x=center_x, y=seabed_y + 30, text=f"두께 t = {thickness:.3f} m", showarrow=False, font=dict(size=13, color="#475569"))

    fig.update_xaxes(visible=False, range=[0, 260])
    fig.update_yaxes(visible=False, range=[370, 0], scaleanchor="x", scaleratio=1)
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="white", plot_bgcolor="white")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# =============================================================================
# 5. 입력 화면
# =============================================================================
def render_intro_and_map() -> str | None:
    intro_col, map_col = st.columns([1.0, 1.1], gap="large")

    with intro_col:
        section_title("계산 대상: 해상풍력 모노파일")
        monopile_image = Path(__file__).resolve().parent / "assets" / "monopile_intro.png"
        render_fixed_height_image(monopile_image)
        st.markdown(
            """
            <div class="hint-text">
                모노파일은 해상풍력 하부구조물 중 하나로, 해저 지반에 삽입되는 대형 원통형 강관입니다.
                파랑과 해류에 의해 반복 하중을 받기 때문에 해역별 환경 조건을 반영한 피로수명 검토가 필요합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with map_col:
        section_title(
            "우리나라 해역 선택",
            "지도에서 동해, 서해, 남해 중 한 지점을 선택하면 파라미터 입력창이 열립니다.",
        )
        clicked_key = render_korea_sea_map(st.session_state.selected_sea)
        if clicked_key:
            st.session_state.selected_sea = clicked_key

    return st.session_state.selected_sea


def render_parameter_inputs(selected_key: str):
    selected_name = DEFAULT_LOCATIONS[selected_key]["name"]
    base_loc = copy.deepcopy(DEFAULT_LOCATIONS[selected_key])

    st.divider()
    section_title("파라미터 입력")

    input_col, preview_col = st.columns([1.4, 0.8], gap="large")

    with input_col:
        st.markdown(f'<div class="selected-sea">선택된 해역: {selected_name}</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("#### 공통 파라미터")
            c1, c2, c3 = st.columns(3)

            D = c1.number_input("직경 D (m)", min_value=0.1, value=float(DEFAULT_MONOPILE["D"]), step=0.1)
            thickness = c2.number_input(
                "두께 t (m)",
                min_value=0.001,
                value=float(DEFAULT_MONOPILE["thickness"]),
                step=0.001,
                format="%.3f",
            )
            L = c3.number_input("파일 길이 L (m)", min_value=1.0, value=float(DEFAULT_MONOPILE["L"]), step=1.0)

            f1, f2, f3 = st.columns(3)
            rho = f1.number_input("해수 밀도 ρ (kg/m³)", min_value=1.0, value=float(DEFAULT_FLUID["rho"]), step=1.0)
            Cd = f2.number_input("항력계수 Cd", min_value=0.01, value=float(DEFAULT_FLUID["Cd"]), step=0.01)
            Cm = f3.number_input("관성계수 Cm", min_value=0.01, value=float(DEFAULT_FLUID["Cm"]), step=0.01)

        with st.container(border=True):
            st.markdown(f"#### {selected_name} 해상상태 파라미터")
            st.markdown(
                f"""
                <div class="hint-text">
                    <b>S-N 곡선:</b> A={DEFAULT_FATIGUE['A']:.2e}, m={DEFAULT_FATIGUE['m']:.1f}<br>
                    <b>{selected_name} 해역:</b> 수심 h={base_loc['h']:.1f} m, 해류속도 Uc={base_loc['Uc']:.1f} m/s<br>
                    Sea State별 H, T, 연간 발생일수는 지정값을 자동 적용합니다.
                </div>
                """,
                unsafe_allow_html=True,
            )

        submitted = st.button("예상 피로수명 계산", type="primary", use_container_width=True)

    with preview_col:
        section_title("모노파일 파라미터 미리보기")
        render_monopile_parameter_preview(D, thickness, L)

    monopile = {"D": D, "thickness": thickness, "L": L}
    fluid = {"rho": rho, "Cd": Cd, "Cm": Cm}
    fatigue = {"A": DEFAULT_FATIGUE["A"], "m": DEFAULT_FATIGUE["m"]}
    loc = {
        "name": selected_name,
        "h": base_loc["h"],
        "Uc": base_loc["Uc"],
        "sea_states": base_loc["sea_states"],
    }

    return submitted, monopile, fluid, fatigue, loc


# =============================================================================
# 6. 결과 화면
# =============================================================================
def render_result_summary(selected_name: str, life: float, total_damage: float, details: list[dict]) -> None:
    life_text = "무한대" if np.isinf(life) else f"{life:.2f} years"
    st.markdown(
        f"""
        <div class="result-badge">계산 완료 · {selected_name}</div>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">예상 피로수명</div>
                <div class="metric-value">{life_text}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">총 연간 손상도</div>
                <div class="metric-value">{total_damage:.3e}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Sea State별 계산 결과")
    st.dataframe(details, use_container_width=True, hide_index=True)


def render_result_graphs(details: list[dict], total_damage: float, life: float) -> None:
    labels = [item["해상상태"] for item in details]
    damages = [item["연간손상도"] for item in details]

    graph_col1, graph_col2 = st.columns(2, gap="large")

    with graph_col1:
        st.subheader("Sea State별 손상 기여도")
        damage_fig = go.Figure(
            data=[
                go.Bar(
                    x=labels,
                    y=damages,
                    marker_color="#38BDF8",
                    text=[f"{value:.2e}" for value in damages],
                    textposition="outside",
                    hovertemplate="Sea State: %{x}<br>연간손상도: %{y:.3e}<extra></extra>",
                )
            ]
        )
        damage_fig.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="Sea State",
            yaxis_title="연간손상도",
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        st.plotly_chart(damage_fig, use_container_width=True, config={"displayModeBar": False})

    with graph_col2:
        st.subheader("누적 손상도(D) vs 시간")
        if total_damage > 0 and np.isfinite(life):
            time_years = np.linspace(0, max(life * 1.15, 1.0), 120)
            cumulative_damage = total_damage * time_years
            x_range = [0, max(life * 1.15, 1.0)]
        else:
            time_years = np.linspace(0, 30, 120)
            cumulative_damage = np.zeros_like(time_years)
            x_range = [0, 30]

        cumulative_fig = go.Figure()
        cumulative_fig.add_trace(
            go.Scatter(
                x=time_years,
                y=cumulative_damage,
                mode="lines",
                line=dict(color="#FB7185", width=3),
                name="누적 손상도",
                hovertemplate="시간: %{x:.2f} years<br>D: %{y:.3f}<extra></extra>",
            )
        )
        cumulative_fig.add_hline(y=1, line_dash="dash", line_color="#111827", annotation_text="D=1 피로파괴", annotation_position="top left")

        if total_damage > 0 and np.isfinite(life):
            cumulative_fig.add_vline(
                x=life,
                line_dash="dot",
                line_color="#FB7185",
                annotation_text=f"{life:.2f} years",
                annotation_position="top right",
            )

        cumulative_fig.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="시간 (years)",
            yaxis_title="누적 손상도 D",
            xaxis=dict(range=x_range),
            yaxis=dict(range=[0, max(float(np.max(cumulative_damage)) * 1.05, 1.15)]),
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False,
        )
        st.plotly_chart(cumulative_fig, use_container_width=True, config={"displayModeBar": False})


def render_compact_table(rows: list[dict]) -> None:
    if not rows:
        return

    headers = list(rows[0].keys())
    header_html = "".join(
        f"<th>{html.escape(str(header))}</th>" for header in headers
    )

    body_html = ""
    for row in rows:
        body_html += "<tr>"
        body_html += "".join(
            f"<td>{html.escape(str(row[header]))}</td>" for header in headers
        )
        body_html += "</tr>"

    st.markdown(
        f"""
        <div style="display:inline-block; margin:6px 0 10px 0; overflow-x:auto; max-width:100%;">
            <table class="compact-calc-table" style="border-collapse:collapse; table-layout:auto; width:auto; font-size:15px;">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{body_html}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_calculation_tables(loc: dict, fatigue: dict, details: list[dict]):
    wave_rows, fatigue_rows, damage_rows = [], [], []

    for sea_state, result in zip(loc["sea_states"], details):
        omega = 2 * np.pi / sea_state["T"]
        k = solve_wave_number(sea_state["T"], loc["h"])
        delta_sigma = result["응력범위(MPa)"]
        damage = result["연간손상도"]
        n = cycles_per_year(sea_state["days_per_year"], sea_state["T"])
        N = np.inf if damage <= 0 else n / damage

        wave_rows.append(
            {
                "Sea State": sea_state["name"],
                "H (m)": round(sea_state["H"], 3),
                "T (s)": round(sea_state["T"], 3),
                "ω = 2π/T (rad/s)": round(omega, 4),
                "k": round(k, 5),
            }
        )

        fatigue_rows.append(
            {
                "Sea State": sea_state["name"],
                "Δσ (MPa)": f"{delta_sigma:.3f}",
                "대입식": f"N = {fatigue['A']:.2e} / ({delta_sigma:.3f}^{fatigue['m']:.1f})",
                "N": "inf" if np.isinf(N) else f"{N:.3e}",
            }
        )

        damage_rows.append(
            {
                "Sea State": sea_state["name"],
                "대입식": f"n = {sea_state['days_per_year']:.0f} × 24 × 3600 / {sea_state['T']:.2f}",
                "n": f"{n:.3e}",
                "Dᵢ = n/N": f"{damage:.3e}",
            }
        )

    return wave_rows, fatigue_rows, damage_rows


def render_calculation_process(monopile, fluid, fatigue, loc, details, total_damage, life) -> None:
    st.markdown("### 주요 계산과정")
    st.caption("계산 흐름을 먼저 간단히 보고, 필요한 식과 표는 단계별로 펼쳐서 확인할 수 있습니다.")

    wave_rows, fatigue_rows, damage_rows = build_calculation_tables(loc, fatigue, details)
    I, c = section_properties(monopile["D"], monopile["thickness"])
    d_inner = monopile["D"] - 2 * monopile["thickness"]
    life_text = "무한대" if np.isinf(life) else f"{life:.2f} years"

    st.markdown(
        f"""
        <div class="calc-flow-simple">
            <div class="calc-flow-line">
                <span class="calc-chip">해역 조건</span>
                <span class="calc-arrow">→</span>
                <span class="calc-chip">파랑하중</span>
                <span class="calc-arrow">→</span>
                <span class="calc-chip">응력범위</span>
                <span class="calc-arrow">→</span>
                <span class="calc-chip">누적손상도</span>
                <span class="calc-arrow">→</span>
                <span class="calc-chip">피로수명</span>
            </div>
        </div>
        <div class="calc-summary-card">
            <div class="calc-summary-title">계산 요약</div>
            <div class="calc-summary-text">
                총 연간 손상도는 <b>{total_damage:.3e}</b>, 예상 피로수명은 <b>{life_text}</b>입니다.
                아래 항목은 계산에 사용된 핵심식과 Sea State별 결과만 간단히 정리한 것입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("파랑하중 계산", expanded=True):
        st.markdown(
            """
            <div class="formula-card">
                <div class="formula-card-title">핵심식</div>
                <div class="formula-line">ω = 2π / T</div>
                <div class="formula-line">ω² = g k tanh(kh)</div>
                <div class="formula-line">F = 0.5ρCdD u|u| + ρCm(πD²/4)du/dt</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_compact_table(wave_rows)

    with st.expander("구조응답 및 응력 계산", expanded=False):
        st.markdown(
            f"""
            <div class="formula-card">
                <div class="formula-card-title">단면 특성과 응력범위</div>
                <div class="formula-line">내경 dᵢ = D - 2t = <b>{d_inner:.3f} m</b></div>
                <div class="formula-line">단면2차모멘트 I = π/64 × (D⁴ - dᵢ⁴) = <b>{I:.3e} m⁴</b></div>
                <div class="formula-line">외측거리 c = D/2 = <b>{c:.3f} m</b></div>
                <div class="formula-line">응력범위 Δσ = max(σ) - min(σ)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("피로수명 평가", expanded=False):
        st.markdown(
            f"""
            <div class="formula-card">
                <div class="formula-card-title">S-N 곡선</div>
                <div class="formula-line">N = A / (Δσᵐ)</div>
                <div class="formula-line">A = <b>{fatigue['A']:.2e}</b>, m = <b>{fatigue['m']:.1f}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_compact_table(fatigue_rows)

    with st.expander("누적손상도 및 최종 피로수명", expanded=False):
        st.markdown(
            f"""
            <div class="formula-card">
                <div class="formula-card-title">Miner 누적손상 법칙</div>
                <div class="formula-line">Dᵢ = n / N</div>
                <div class="formula-line">D_year = ΣDᵢ = <b>{total_damage:.3e}</b></div>
                <div class="formula-line">Life = 1 / D_year = <b>{life_text}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_compact_table(damage_rows)

def render_results(monopile, fluid, fatigue, loc) -> None:
    errors = validate_inputs(monopile, fluid)
    if errors:
        for error in errors:
            st.error(error)
        return

    with st.spinner("예상 피로수명 계산 중입니다..."):
        life, total_damage, details = analyze_location(monopile, fluid, fatigue, loc)

    st.divider()
    section_title("계산 결과")

    tab_summary, tab_graph, tab_process = st.tabs(["요약", "그래프", "계산과정"])

    with tab_summary:
        render_result_summary(loc["name"], life, total_damage, details)

    with tab_graph:
        render_result_graphs(details, total_damage, life)

    with tab_process:
        render_calculation_process(monopile, fluid, fatigue, loc, details, total_damage, life)




# =============================================================================
# 7. 사용자 친화형 화면 구성
# =============================================================================
def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-kicker">OFFSHORE WIND MONOPILE FATIGUE LIFE</div>
            <div class="hero-title">해역별 모노파일 예상 피로수명 계산</div>
            <div class="hero-caption">
                왼쪽에서 해역과 파라미터를 입력하고, 본문에서 현재 조건과 계산 결과를 확인하는 계산 대시보드입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def initialize_session_state() -> None:
    if "selected_sea" not in st.session_state or st.session_state.selected_sea is None:
        st.session_state.selected_sea = "west"
    if "calculation_result" not in st.session_state:
        st.session_state.calculation_result = None


def render_sidebar_controls():
    st.sidebar.title("계산 조건 입력")
    st.sidebar.caption("해역과 사용자가 조정할 파라미터만 입력합니다.")

    sea_labels = {"west": "서해", "south": "남해", "east": "동해"}
    current_index = SEA_LAYOUT.index(st.session_state.selected_sea)

    with st.sidebar.container(border=True):
        st.markdown('<div class="sidebar-section-title">해역 선택</div>', unsafe_allow_html=True)
        selected_label = st.radio(
            "계산 해역",
            options=[sea_labels[key] for key in SEA_LAYOUT],
            index=current_index,
            horizontal=True,
            label_visibility="collapsed",
        )
        selected_key = next(key for key, value in sea_labels.items() if value == selected_label)
        st.session_state.selected_sea = selected_key

        base_loc = copy.deepcopy(DEFAULT_LOCATIONS[selected_key])
        st.markdown(
            f"""
            <div class="sidebar-fixed-note">
                {base_loc['name']} 해역 해상상태 파라미터<br>
                수심 {base_loc['h']:.1f} m · 해류속도 {base_loc['Uc']:.1f} m/s<br>
                S-N A={DEFAULT_FATIGUE['A']:.1e}, m={DEFAULT_FATIGUE['m']:.1f}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.sidebar.container(border=True):
        st.markdown('<div class="sidebar-section-title">모노파일 제원</div>', unsafe_allow_html=True)
        col_d, col_t = st.columns(2)
        D = col_d.number_input(
            "직경 D (m)",
            min_value=0.1,
            value=float(DEFAULT_MONOPILE["D"]),
            step=0.1,
            help="모노파일 외경입니다.",
        )
        thickness = col_t.number_input(
            "두께 t (m)",
            min_value=0.001,
            value=float(DEFAULT_MONOPILE["thickness"]),
            step=0.001,
            format="%.3f",
            help="강관 벽 두께입니다. D > 2t 조건을 만족해야 합니다.",
        )
        L = st.number_input(
            "파일 길이 L (m)",
            min_value=1.0,
            value=float(DEFAULT_MONOPILE["L"]),
            step=1.0,
        )

    with st.sidebar.container(border=True):
        st.markdown('<div class="sidebar-section-title">유체/하중 계수</div>', unsafe_allow_html=True)
        rho = st.number_input("해수 밀도 ρ (kg/m³)", min_value=1.0, value=float(DEFAULT_FLUID["rho"]), step=1.0)
        col_cd, col_cm = st.columns(2)
        Cd = col_cd.number_input("Cd", min_value=0.01, value=float(DEFAULT_FLUID["Cd"]), step=0.01)
        Cm = col_cm.number_input("Cm", min_value=0.01, value=float(DEFAULT_FLUID["Cm"]), step=0.01)

    submitted = st.sidebar.button("예상 피로수명 계산", type="primary", use_container_width=True)

    if st.sidebar.button("결과 초기화", use_container_width=True):
        st.session_state.calculation_result = None

    monopile = {"D": D, "thickness": thickness, "L": L}
    fluid = {"rho": rho, "Cd": Cd, "Cm": Cm}
    fatigue = {"A": DEFAULT_FATIGUE["A"], "m": DEFAULT_FATIGUE["m"]}
    loc = {
        "name": base_loc["name"],
        "h": base_loc["h"],
        "Uc": base_loc["Uc"],
        "sea_states": base_loc["sea_states"],
    }
    return submitted, monopile, fluid, fatigue, loc

def render_intro_and_map_user_friendly() -> None:
    info_col, map_col = st.columns([0.95, 1.25], gap="large")

    with info_col:
        section_title("계산 대상", "해상풍력 모노파일의 반복하중에 따른 피로수명을 계산합니다.")
        monopile_image = Path(__file__).resolve().parent / "assets" / "monopile_intro.png"
        render_fixed_height_image(monopile_image, height=330)
        st.markdown(
            """
            <div class="guide-box" style="margin-top:0.75rem;">
                <b>모노파일이란?</b><br>
                모노파일은 해상풍력 발전기를 지지하는 대형 원통형 강관 기초입니다.
                해저 지반에 고정되어 파랑과 해류에 의한 반복하중을 직접 받기 때문에,
                해역 조건에 따른 피로수명 검토가 중요합니다.
            </div>
            <div class="guide-box" style="margin-top:0.65rem;">
                <b>사용 방법</b><br>
                지도 또는 왼쪽 사이드바에서 해역을 선택하고, 모노파일 제원을 입력한 뒤 계산 버튼을 누르면 됩니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with map_col:
        section_title("해역 선택 지도", "지도 글자 주변을 클릭하면 해역이 바뀝니다. 사이드바에서도 선택할 수 있습니다.")
        clicked_key = render_korea_sea_map(st.session_state.selected_sea)
        if clicked_key and clicked_key != st.session_state.selected_sea:
            st.session_state.selected_sea = clicked_key
            st.session_state.calculation_result = None
            st.rerun()



def render_value_table(rows: list[tuple[str, str]]) -> str:
    body = "".join(
        f"<tr><td>{html.escape(label)}</td><td>{html.escape(value)}</td></tr>"
        for label, value in rows
    )
    return f'<table class="value-table"><tbody>{body}</tbody></table>'

def render_condition_review(monopile: dict, fluid: dict, fatigue: dict, loc: dict) -> None:
    st.divider()
    section_title(
        "현재 입력 조건 확인",
        "왼쪽은 사용자 입력값, 오른쪽은 입력값이 반영된 모노파일 미리보기입니다.",
    )

    user_rows = [
        ("직경 D", f"{monopile['D']:.2f} m"),
        ("두께 t", f"{monopile['thickness']:.3f} m"),
        ("파일 길이 L", f"{monopile['L']:.1f} m"),
        ("해수 밀도 ρ", f"{fluid['rho']:.1f} kg/m³"),
        ("항력계수 Cd", f"{fluid['Cd']:.2f}"),
        ("관성계수 Cm", f"{fluid['Cm']:.2f}"),
    ]

    condition_col, preview_col = st.columns([1.05, 0.95], gap="large")

    with condition_col:
        st.markdown(
            f"""
            <div class="condition-layout">
                <div class="user-param-card">
                    <div class="review-card-title">
                        <strong>사용자 입력 파라미터</strong>
                        <span class="review-tag user">직접 수정 가능</span>
                    </div>
                    {render_value_table(user_rows)}
                    <div class="inline-fixed-note">
                        <span class="label">{loc['name']} 해역 해상상태 파라미터</span>
                        h <b>{loc['h']:.1f} m</b> · Uc <b>{loc['Uc']:.1f} m/s</b> · S-N A <b>{fatigue['A']:.2e}</b> · m <b>{fatigue['m']:.1f}</b>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with preview_col:
        section_title("모노파일 미리보기")
        render_monopile_parameter_preview(monopile["D"], monopile["thickness"], monopile["L"], height=330)

    st.markdown(f"#### {loc['name']} 해역 해상상태 파라미터")
    st.caption("Sea State별 파고, 주기, 연간 발생일수는 선택한 해역에 따라 자동 적용됩니다.")
    sea_state_rows = [
        {
            "Sea State": item["name"],
            "파고 H (m)": item["H"],
            "주기 T (s)": item["T"],
            "발생일수(days/year)": item["days_per_year"],
        }
        for item in loc["sea_states"]
    ]
    st.dataframe(sea_state_rows, use_container_width=True, hide_index=True)

def compute_and_store_result(monopile: dict, fluid: dict, fatigue: dict, loc: dict) -> None:
    errors = validate_inputs(monopile, fluid)
    if errors:
        st.session_state.calculation_result = None
        for error in errors:
            st.error(error)
        return

    with st.spinner("예상 피로수명 계산 중입니다..."):
        life, total_damage, details = analyze_location(monopile, fluid, fatigue, loc)

    st.session_state.calculation_result = {
        "monopile": monopile,
        "fluid": fluid,
        "fatigue": fatigue,
        "loc": loc,
        "life": life,
        "total_damage": total_damage,
        "details": details,
    }


def render_stored_result() -> None:
    result = st.session_state.calculation_result
    if result is None:
        st.info("왼쪽 Control Panel에서 조건을 확인한 뒤 `예상 피로수명 계산` 버튼을 눌러주세요.")
        return

    st.divider()
    section_title("계산 결과", "요약, 그래프, 계산과정을 탭으로 나누어 확인할 수 있습니다.")

    tab_summary, tab_graph, tab_process = st.tabs(["결과 요약", "그래프", "계산과정"])
    with tab_summary:
        render_result_summary(result["loc"]["name"], result["life"], result["total_damage"], result["details"])
        st.markdown(
            """
            <div class="guide-box">
                총 연간 손상도가 작을수록 예상 피로수명은 길어집니다.
                그래프 탭에서 어떤 Sea State가 손상에 가장 크게 기여하는지 확인할 수 있습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tab_graph:
        render_result_graphs(result["details"], result["total_damage"], result["life"])
    with tab_process:
        render_calculation_process(
            result["monopile"],
            result["fluid"],
            result["fatigue"],
            result["loc"],
            result["details"],
            result["total_damage"],
            result["life"],
        )

# =============================================================================
# 7. 앱 실행
# =============================================================================
def main() -> None:
    apply_page_style()
    initialize_session_state()

    submitted, monopile, fluid, fatigue, loc = render_sidebar_controls()

    render_hero()
    render_intro_and_map_user_friendly()
    render_condition_review(monopile, fluid, fatigue, loc)

    if submitted:
        compute_and_store_result(monopile, fluid, fatigue, loc)

    render_stored_result()


if __name__ == "__main__":
    main()
