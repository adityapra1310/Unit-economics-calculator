"""
Unit Economics Calculator
=========================
A professional, interactive web application for modeling SaaS and D2C
customer economics with dynamic scenario analysis.

Author  : Aditya Prakash
Version : 1.0.0
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Unit Economics Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  –  professional, minimalist theme
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
      /* ── Global ───────────────────────────── */
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

      html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

      /* ── Background ───────────────────────── */
      .stApp { background-color: #0f1117; color: #e8eaf0; }

      /* ── Sidebar ──────────────────────────── */
      [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #161b27 0%, #0f1117 100%);
        border-right: 1px solid #1e2535;
      }
      [data-testid="stSidebar"] .stMarkdown h2 {
        color: #5b8dee;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
      }

      /* ── Metric cards ─────────────────────── */
      [data-testid="metric-container"] {
        background: #161b27;
        border: 1px solid #1e2535;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        transition: transform 0.2s;
      }
      [data-testid="metric-container"]:hover { transform: translateY(-2px); }
      [data-testid="stMetricLabel"]  { color: #8892a4 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
      [data-testid="stMetricValue"]  { color: #e8eaf0 !important; font-family: 'JetBrains Mono', monospace !important; }
      [data-testid="stMetricDelta"]  { font-size: 0.75rem !important; }

      /* ── Section headers ──────────────────── */
      .section-header {
        color: #8892a4;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        border-bottom: 1px solid #1e2535;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem;
      }

      /* ── Status badge ─────────────────────── */
      .badge {
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .badge-red    { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
      .badge-yellow { background: rgba(234,179,8,0.15);  color: #eab308; border: 1px solid rgba(234,179,8,0.3); }
      .badge-green  { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }

      /* ── Insight callout ──────────────────── */
      .insight-box {
        background: rgba(91,141,238,0.07);
        border-left: 3px solid #5b8dee;
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.1rem;
        margin: 1rem 0;
        font-size: 0.875rem;
        color: #b8c4d8;
      }
      .insight-box strong { color: #5b8dee; }

      /* ── Plotly charts ────────────────────── */
      .js-plotly-plot .plotly { border-radius: 12px; }

      /* ── Divider ──────────────────────────── */
      hr { border-color: #1e2535 !important; }

      /* ── DataFrame ────────────────────────── */
      .dataframe { font-family: 'JetBrains Mono', monospace !important; font-size: 0.78rem !important; }

      /* ── Toggle group ─────────────────────── */
      [data-testid="stRadio"] > div {
        background: #161b27;
        border-radius: 8px;
        padding: 0.4rem;
        gap: 0.3rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  FINANCIAL ENGINE
# ─────────────────────────────────────────────

def compute_cac(sm_spend: float, new_customers: int) -> float:
    """CAC = Total S&M Spend / Number of New Customers."""
    if new_customers <= 0:
        return 0.0
    return sm_spend / new_customers


def compute_ltv(arpu: float, gross_margin: float, churn_rate: float) -> float:
    """
    LTV = (ARPU × Gross Margin%) / Monthly Churn Rate
    For D2C the ARPU passed in is already annualised to a monthly equivalent.
    """
    if churn_rate <= 0:
        return float("inf")
    return (arpu * (gross_margin / 100)) / (churn_rate / 100)


def compute_ltv_cac_ratio(ltv: float, cac: float) -> float:
    """LTV:CAC — the primary unit-economics health indicator."""
    if cac <= 0:
        return 0.0
    return ltv / cac


def compute_payback(cac: float, arpu: float, gross_margin: float) -> float:
    """
    Payback Period (months) = CAC / (ARPU × Gross Margin%)
    Number of months to recover the cost of acquiring one customer.
    """
    margin_revenue = arpu * (gross_margin / 100)
    if margin_revenue <= 0:
        return float("inf")
    return cac / margin_revenue


def cumulative_cashflow(
    cac: float,
    arpu: float,
    gross_margin: float,
    churn_rate: float,
    months: int = 24,
) -> tuple[list[int], list[float]]:
    """
    Simulate cumulative cash flow per acquired customer over `months`.
    Each month: contribution margin earned by surviving cohort − upfront CAC.
    Churn is applied as a monthly decay to the remaining customer fraction.
    """
    m_list: list[int] = list(range(0, months + 1))
    cum_cf: list[float] = [0.0] * (months + 1)
    cum_cf[0] = -cac  # initial acquisition cost

    surviving_fraction = 1.0
    margin_per_month = arpu * (gross_margin / 100)

    for m in range(1, months + 1):
        surviving_fraction *= 1 - (churn_rate / 100)
        cum_cf[m] = cum_cf[m - 1] + surviving_fraction * margin_per_month

    return m_list, cum_cf


def sensitivity_table(
    arpu: float,
    gross_margin: float,
    churn_rates: list[float],
    cac_values: list[float],
) -> pd.DataFrame:
    """
    Build a sensitivity matrix:
      rows    → Churn Rate (%)
      columns → CAC ($)
      cells   → LTV:CAC ratio
    """
    data: dict[str, list[float]] = {}
    for cac in cac_values:
        col: list[float] = []
        for churn in churn_rates:
            ltv = compute_ltv(arpu, gross_margin, churn)
            ratio = compute_ltv_cac_ratio(ltv, cac)
            col.append(round(ratio, 2))
        data[f"CAC ${int(cac):,}"] = col

    df = pd.DataFrame(data, index=[f"{c:.1f}%" for c in churn_rates])
    df.index.name = "Churn Rate"
    return df


# ─────────────────────────────────────────────
#  CHART HELPERS
# ─────────────────────────────────────────────

CHART_LAYOUT = dict(
    paper_bgcolor="#161b27",
    plot_bgcolor="#161b27",
    font=dict(family="Inter, sans-serif", color="#8892a4", size=12),
    margin=dict(l=10, r=10, t=50, b=10),
    xaxis=dict(gridcolor="#1e2535", zerolinecolor="#1e2535"),
    yaxis=dict(gridcolor="#1e2535", zerolinecolor="#1e2535"),
)


def chart_ltv_vs_cac(ltv: float, cac: float) -> go.Figure:
    """Grouped bar chart: LTV vs CAC with threshold annotations."""
    ratio = compute_ltv_cac_ratio(ltv, cac)

    bar_color_ltv = "#5b8dee"
    bar_color_cac = "#ef4444" if ratio < 1 else ("#eab308" if ratio < 3 else "#22c55e")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="LTV",
            x=["Customer Economics"],
            y=[round(ltv, 2)],
            marker_color=bar_color_ltv,
            marker_line_width=0,
            text=[f"${ltv:,.0f}"],
            textposition="outside",
            textfont=dict(color="#e8eaf0", size=13, family="JetBrains Mono"),
        )
    )
    fig.add_trace(
        go.Bar(
            name="CAC",
            x=["Customer Economics"],
            y=[round(cac, 2)],
            marker_color=bar_color_cac,
            marker_line_width=0,
            text=[f"${cac:,.0f}"],
            textposition="outside",
            textfont=dict(color="#e8eaf0", size=13, family="JetBrains Mono"),
        )
    )

    fig.add_hline(
        y=cac * 3,
        line_dash="dot",
        line_color="#22c55e",
        annotation_text="3× CAC  (target LTV)",
        annotation_position="top right",
        annotation_font=dict(color="#22c55e", size=11),
    )

    fig.update_layout(
        title=dict(text="LTV vs CAC", font=dict(color="#e8eaf0", size=15), x=0.02),
        barmode="group",
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8892a4")),
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        **CHART_LAYOUT,
    )
    return fig


def chart_cashflow(
    cac: float,
    arpu: float,
    gross_margin: float,
    churn_rate: float,
) -> go.Figure:
    """Line chart of cumulative cash flow per customer over 24 months."""
    months, cum_cf = cumulative_cashflow(cac, arpu, gross_margin, churn_rate)

    # Find payback month (first month ≥ 0)
    payback_month: int | None = next(
        (m for m, v in zip(months, cum_cf) if v >= 0), None
    )

    fig = go.Figure()

    # Fill areas above/below zero separately
    fig.add_trace(
        go.Scatter(
            x=months,
            y=cum_cf,
            mode="lines",
            name="Cumulative Cash Flow",
            line=dict(color="#5b8dee", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(91,141,238,0.08)",
        )
    )

    # Zero reference line
    fig.add_hline(y=0, line_color="#1e2535", line_width=1.5)

    # Payback marker
    if payback_month is not None:
        pb_val = cum_cf[payback_month]
        fig.add_trace(
            go.Scatter(
                x=[payback_month],
                y=[pb_val],
                mode="markers+text",
                name=f"Payback: Month {payback_month}",
                marker=dict(color="#22c55e", size=10, symbol="circle"),
                text=[f"  Payback\n  Month {payback_month}"],
                textposition="middle right",
                textfont=dict(color="#22c55e", size=11),
            )
        )

    fig.update_layout(
        title=dict(
            text="Cumulative Cash Flow Per Customer (24 Months)",
            font=dict(color="#e8eaf0", size=15),
            x=0.02,
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8892a4")),
        **CHART_LAYOUT,
    )
    fig.update_xaxes(title_text="Month", dtick=3, gridcolor="#1e2535", zerolinecolor="#1e2535")
    fig.update_yaxes(title_text="Cumulative Cash Flow ($)", tickprefix="$",
                     tickformat=",.0f", gridcolor="#1e2535", zerolinecolor="#1e2535")
    return fig


def style_sensitivity(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Colour-code the sensitivity table cells by LTV:CAC health threshold."""

    def cell_color(val: float) -> str:
        if val < 1:
            return "background-color:#3b1212; color:#ef4444;"
        elif val < 3:
            return "background-color:#2d2509; color:#eab308;"
        else:
            return "background-color:#0d2b1a; color:#22c55e;"

    return df.style.applymap(cell_color).format("{:.2f}×")


# ─────────────────────────────────────────────
#  SIDEBAR  –  Scenario Controls
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙ SCENARIO BUILDER")

    # ── Business Model ───────────────────────
    st.markdown('<p class="section-header">Business Model</p>', unsafe_allow_html=True)
    model: str = st.radio(
        label="Select model",
        options=["SaaS", "D2C"],
        horizontal=True,
        label_visibility="collapsed",
    )

    # ── Acquisition Metrics ──────────────────
    st.markdown('<p class="section-header">Acquisition</p>', unsafe_allow_html=True)
    sm_spend: float = st.slider(
        "Monthly S&M Spend ($)",
        min_value=1_000,
        max_value=500_000,
        value=50_000,
        step=1_000,
        format="$%d",
    )
    new_customers: int = st.slider(
        "New Customers Acquired",
        min_value=1,
        max_value=5_000,
        value=200,
        step=10,
    )

    # ── Revenue Metrics ──────────────────────
    st.markdown('<p class="section-header">Revenue</p>', unsafe_allow_html=True)

    if model == "SaaS":
        arpu_label = "Monthly ARPU ($)"
        arpu_default = 120
        arpu_max = 2_000
    else:
        arpu_label = "Avg Order Value ($)"
        arpu_default = 85
        arpu_max = 1_000

    arpu: float = st.slider(
        arpu_label,
        min_value=5,
        max_value=arpu_max,
        value=arpu_default,
        step=5,
        format="$%d",
    )

    if model == "D2C":
        purchase_freq: float = st.slider(
            "Purchase Frequency (orders/month)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
        )
        # Normalise D2C to monthly ARPU equivalent
        arpu = arpu * purchase_freq

    gross_margin: float = st.slider(
        "Gross Margin (%)",
        min_value=1.0,
        max_value=99.0,
        value=70.0,
        step=0.5,
        format="%.1f%%",
    )
    churn_rate: float = st.slider(
        "Monthly Churn Rate (%)",
        min_value=0.1,
        max_value=30.0,
        value=3.0,
        step=0.1,
        format="%.1f%%",
    )

    # ── Sensitivity Ranges ───────────────────
    st.markdown('<p class="section-header">Sensitivity Range</p>', unsafe_allow_html=True)
    churn_range: tuple[float, float] = st.slider(
        "Churn Range (%)",
        min_value=0.5,
        max_value=30.0,
        value=(1.0, 10.0),
        step=0.5,
    )
    cac_multiplier: float = st.slider(
        "CAC Range (× base CAC)",
        min_value=0.5,
        max_value=4.0,
        value=2.0,
        step=0.25,
    )

    st.markdown("---")
    st.caption("📐 Formulas follow standard SaaS & D2C unit-economics conventions.")


# ─────────────────────────────────────────────
#  COMPUTE METRICS
# ─────────────────────────────────────────────

cac: float = compute_cac(sm_spend, new_customers)
ltv: float = compute_ltv(arpu, gross_margin, churn_rate)
ratio: float = compute_ltv_cac_ratio(ltv, cac)
payback: float = compute_payback(cac, arpu, gross_margin)


def ratio_health(r: float) -> tuple[str, str]:
    """Return (badge_class, label) based on the LTV:CAC ratio."""
    if r < 1:
        return "badge-red", "⚠ UNSUSTAINABLE"
    elif r < 3:
        return "badge-yellow", "⚡ NEEDS IMPROVEMENT"
    else:
        return "badge-green", "✓ HEALTHY"


badge_cls, badge_label = ratio_health(ratio)


# ─────────────────────────────────────────────
#  MAIN DASHBOARD
# ─────────────────────────────────────────────

# ── Header ──────────────────────────────────
st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                border-bottom:1px solid #1e2535; padding-bottom:1rem; margin-bottom:1.5rem;">
        <div>
            <h1 style="margin:0; color:#e8eaf0; font-size:1.6rem; font-weight:700;
                       letter-spacing:-0.02em;">
                📊 Unit Economics Calculator
            </h1>
            <p style="margin:0.25rem 0 0; color:#8892a4; font-size:0.85rem;">
                {model} Model  ·  Interactive scenario modelling
            </p>
        </div>
        <span class="badge {badge_cls}">{badge_label}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI Scorecards ───────────────────────────
st.markdown('<p class="section-header">Key Performance Indicators</p>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Customer Acquisition Cost",
        value=f"${cac:,.0f}",
        delta=f"${sm_spend:,.0f} S&M / {new_customers:,} customers",
        delta_color="off",
    )

with kpi2:
    ltv_display = f"${ltv:,.0f}" if ltv != float("inf") else "∞"
    avg_life = (100 / churn_rate) if churn_rate > 0 else float("inf")
    st.metric(
        label="Customer Lifetime Value",
        value=ltv_display,
        delta=f"~{avg_life:.1f} mo avg lifetime",
        delta_color="off",
    )

with kpi3:
    ratio_display = f"{ratio:.2f}×"
    if ratio >= 3:
        delta_txt, delta_col = "▲ Above 3× target", "normal"
    elif ratio >= 1:
        delta_txt, delta_col = "▼ Below 3× target", "inverse"
    else:
        delta_txt, delta_col = "⚠ Below breakeven", "inverse"

    st.metric(
        label="LTV : CAC Ratio",
        value=ratio_display,
        delta=delta_txt,
        delta_color=delta_col,
    )

with kpi4:
    pb_display = f"{payback:.1f} mo" if payback != float("inf") else "Never"
    pb_bench = "▲ Under 12 mo" if payback < 12 else "▼ Over 12 mo"
    pb_col = "normal" if payback < 12 else "inverse"
    st.metric(
        label="CAC Payback Period",
        value=pb_display,
        delta=pb_bench,
        delta_color=pb_col,
    )

# ── Insight callout ──────────────────────────
insight_lines: list[str] = []
if ratio < 1:
    insight_lines.append(
        f"Your LTV (<strong>${ltv:,.0f}</strong>) is below CAC (<strong>${cac:,.0f}</strong>). "
        "Every new customer acquired is destroying value. Reduce S&M spend, improve retention, "
        "or increase ARPU immediately."
    )
elif ratio < 3:
    insight_lines.append(
        f"LTV:CAC of <strong>{ratio:.2f}×</strong> is positive but below the 3× industry benchmark. "
        f"Cutting churn by 1 pp or raising ARPU by 10 % would materially improve unit economics."
    )
else:
    insight_lines.append(
        f"Strong LTV:CAC of <strong>{ratio:.2f}×</strong>. "
        f"Payback in <strong>{payback:.1f} months</strong> — "
        f"{'well within the 12-month best-practice window.' if payback < 12 else 'consider optimising CAC to shorten payback.'}"
    )

st.markdown(
    f'<div class="insight-box">💡 <strong>Analyst Insight:</strong> {insight_lines[0]}</div>',
    unsafe_allow_html=True,
)

# ── Charts row ───────────────────────────────
st.markdown('<p class="section-header">Visualisations</p>', unsafe_allow_html=True)
col_bar, col_cf = st.columns(2)

with col_bar:
    st.plotly_chart(
        chart_ltv_vs_cac(ltv, cac),
        use_container_width=True,
        config={"displayModeBar": False},
    )

with col_cf:
    st.plotly_chart(
        chart_cashflow(cac, arpu, gross_margin, churn_rate),
        use_container_width=True,
        config={"displayModeBar": False},
    )

# ── Sensitivity Analysis ─────────────────────
st.markdown('<p class="section-header">Sensitivity Analysis — LTV:CAC Ratio</p>', unsafe_allow_html=True)

churn_steps = np.round(
    np.linspace(churn_range[0], churn_range[1], 8), 1
).tolist()
cac_base = max(cac, 1)
cac_steps = [
    round(cac_base * m, 0)
    for m in np.linspace(0.5, cac_multiplier, 6)
]

sens_df = sensitivity_table(arpu, gross_margin, churn_steps, cac_steps)

st.markdown(
    """<p style="color:#8892a4; font-size:0.8rem; margin-bottom:0.5rem;">
    🟢 ≥ 3×  |  🟡 1–3×  |  🔴 &lt; 1×  — cells reflect LTV:CAC at each churn/CAC intersection
    </p>""",
    unsafe_allow_html=True,
)
st.dataframe(style_sensitivity(sens_df), use_container_width=True)

# ── Detailed Assumptions ─────────────────────
with st.expander("📋 Calculation Assumptions & Raw Inputs"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Acquisition**")
        st.code(
            f"S&M Spend    :  ${sm_spend:>10,.0f}\n"
            f"New Customers:  {new_customers:>10,}\n"
            f"CAC          :  ${cac:>10,.2f}",
            language="text",
        )
    with c2:
        st.markdown("**Revenue**")
        st.code(
            f"ARPU (monthly):  ${arpu:>9,.2f}\n"
            f"Gross Margin  :  {gross_margin:>9.1f}%\n"
            f"Monthly Churn :  {churn_rate:>9.1f}%",
            language="text",
        )
    with c3:
        st.markdown("**Derived Metrics**")
        st.code(
            f"LTV           :  ${ltv:>9,.2f}\n"
            f"LTV:CAC       :  {ratio:>10.2f}×\n"
            f"Payback       :  {payback:>8.1f} mo",
            language="text",
        )

# ── Footer ───────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; color:#3d4557; font-size:0.72rem;
                border-top:1px solid #1e2535; margin-top:2rem; padding-top:1rem;">
        Unit Economics Calculator · Built with Streamlit & Plotly ·
        Formulas: standard SaaS / D2C conventions
    </div>
    """,
    unsafe_allow_html=True,
)
