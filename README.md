# 📊 Unit Economics Calculator

> An interactive, professional-grade web application for modelling SaaS and D2C customer economics — built with Python, Streamlit, and Plotly.

---

## 🎯 Overview

Unit economics are the fundamental drivers of business health. This tool enables founders, operators, and analysts to model customer-level profitability by translating acquisition, revenue, and retention inputs into four canonical metrics:

| Metric | Answers |
|---|---|
| **CAC** | How much does it cost to acquire one customer? |
| **LTV** | How much gross profit does one customer generate over their lifetime? |
| **LTV:CAC** | Is the business worth scaling? |
| **Payback Period** | How quickly do you recover the acquisition cost? |

The application supports both **SaaS** (subscription, monthly churn) and **D2C** (transactional, purchase frequency) business models with real-time scenario toggling.

---

## ✨ Features

- **Dynamic Sidebar Controls** — Sliders for every variable; instant recalculation on change
- **Business Model Toggle** — Switch between SaaS and D2C; inputs adapt automatically
- **KPI Scorecards** — CAC, LTV, LTV:CAC Ratio, and Payback Period with health indicators
- **LTV vs CAC Bar Chart** — Visual comparison with 3× target reference line
- **Cumulative Cash Flow Chart** — 24-month per-customer cash flow with payback crossover marker
- **Sensitivity Analysis Table** — Colour-coded matrix (churn × CAC) showing LTV:CAC across scenarios
- **Analyst Insight Callout** — Contextual interpretation of the current scenario
- **Dark, Minimalist UI** — Professional design with JetBrains Mono and Inter typefaces

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/unit-economics-calculator.git
cd unit-economics-calculator
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501** in your default browser.

---

## 📁 Project Architecture

```
unit-economics-calculator/
│
├── app.py              # Single-file Streamlit application
│   ├── PAGE CONFIG     # Streamlit layout & metadata
│   ├── CUSTOM CSS      # Dark-mode theme, typography, component styles
│   ├── FINANCIAL ENGINE
│   │   ├── compute_cac()           # CAC formula
│   │   ├── compute_ltv()           # LTV formula
│   │   ├── compute_ltv_cac_ratio() # Ratio + health flag
│   │   ├── compute_payback()       # Payback period
│   │   ├── cumulative_cashflow()   # 24-month cohort simulation
│   │   └── sensitivity_table()    # Churn × CAC DataFrame
│   ├── CHART HELPERS
│   │   ├── chart_ltv_vs_cac()     # Plotly bar chart
│   │   ├── chart_cashflow()       # Plotly line chart
│   │   └── style_sensitivity()    # Pandas Styler colour mapping
│   ├── SIDEBAR                    # All scenario controls
│   └── MAIN DASHBOARD             # KPIs, charts, sensitivity, footer
│
├── requirements.txt    # Pinned Python dependencies
└── README.md           # This file
```

---

## 🧮 Financial Logic

All formulas follow standard SaaS / D2C unit-economics conventions.

### Customer Acquisition Cost (CAC)
```
CAC = Total Sales & Marketing Spend
      ─────────────────────────────────
         Number of New Customers
```
Measures the blended cost to acquire one new customer in a given period.

---

### Customer Lifetime Value (LTV)
```
LTV =  ARPU  ×  Gross Margin %
       ──────────────────────────
          Monthly Churn Rate
```
Derived from the perpetuity formula `(monthly contribution margin) / churn`, assuming constant churn and no expansion revenue. For D2C, `ARPU = Average Order Value × Monthly Purchase Frequency`.

> **Why this formula?** Churn is treated as a constant hazard rate, making the expected customer lifetime `1 / churn_rate`. The formula is the present value of a geometric series of monthly cash flows — a simplification that trades slight accuracy for interpretability.

---

### LTV : CAC Ratio
```
LTV:CAC = LTV / CAC
```

| Range | Signal |
|---|---|
| **< 1×** | 🔴 Destroying value — each new customer costs more than they'll ever return |
| **1× – 3×** | 🟡 Positive but below industry benchmark; growth is capital-inefficient |
| **> 3×** | 🟢 Healthy — standard benchmark used by VCs and growth-stage operators |

---

### CAC Payback Period
```
Payback (months) =         CAC
                   ────────────────────────
                   ARPU × Gross Margin %
```
The number of months required to fully recover the acquisition cost through contribution margin, assuming zero churn. Industry benchmark: **< 12 months** for SaaS, **< 6 months** for D2C.

> **Payback vs LTV horizon:** Payback ignores churn (best-case floor). The cash-flow chart accounts for monthly cohort decay, giving a more conservative and realistic view of actual capital recovery.

---

### Cumulative Cash Flow Model
```
CF(0) = -CAC
CF(m) = CF(m-1) + surviving_fraction(m) × (ARPU × Gross Margin %)

where: surviving_fraction(m) = (1 - churn_rate)^m
```
Models a single acquired cohort as it decays over 24 months. The crossover point (CF = 0) is the realised payback month under churn-adjusted conditions.

---

### Sensitivity Analysis
A 2D matrix iterating over:
- **Rows:** Churn Rate (%) — from configurable lower to upper bound
- **Columns:** CAC ($) — from 0.5× to N× of the base CAC

Each cell displays the resulting LTV:CAC ratio, colour-coded by health threshold.

---

## 📊 Benchmark Reference

| Metric | Early Stage | Growth Stage | Best-in-Class |
|---|---|---|---|
| LTV:CAC | > 1× | > 3× | > 5× |
| Payback Period | < 24 mo | < 12 mo | < 6 mo |
| Gross Margin (SaaS) | > 50% | > 65% | > 75% |
| Monthly Churn | < 5% | < 3% | < 1% |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| UI Framework | Streamlit 1.35+ |
| Data / Math | Pandas 2.2, NumPy 1.26 |
| Visualisation | Plotly 5.22 |

---

## 📄 License

MIT — free to use, modify, and distribute with attribution.

---

*Built to demonstrate financial fluency and engineering maturity in Python.*
