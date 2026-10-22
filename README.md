# Atlas Bank - Bank Risk Analytics Platform

An interactive banking risk analytics project built with **Python, SQL, Pandas, NumPy, Plotly and Streamlit**.

Atlas Bank simulates a multi-asset investment portfolio and a banking loan book, providing quantitative tools for market risk, interest-rate sensitivity, stress testing, sovereign risk, portfolio optimization and credit risk analytics.

> **Status:** Market Risk and Credit Risk Analytics are implemented and available in the public Streamlit dashboard. Liquidity Risk is planned.

## 1. Project Overview

The current platform includes:

- Portfolio risk monitoring and historical P&L analysis
- Historical Value at Risk (VaR) and Expected Shortfall (ES)
- Fixed-income duration, convexity and DV01
- Interest-rate and yield-curve scenario analysis
- Portfolio stress testing
- Sovereign bond and spread risk analysis
- Risk concentration and contribution analysis
- Sovereign portfolio optimization
- Credit risk monitoring using PD, LGD, EAD and Expected Loss
- Credit concentration analysis by segment, rating and customer

## 2. Technology Stack

| Component | Technology |
|---|---|
| Programming | Python |
| Data processing | Pandas, NumPy |
| Financial analytics | Quantitative Python models |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Database integration | PostgreSQL, SQLAlchemy |
| SQL analysis | PostgreSQL SQL |
| Version control | Git and GitHub |

The public dashboard runs on local demonstration datasets without requiring a PostgreSQL connection.

## 3. Market Risk Dashboard

### Portfolio Overview
Portfolio exposures, risk indicators, historical P&L and executive risk monitoring.

### Market Risk Analytics
Instrument-level risk, concentration and risk contribution.

### Stress Testing & Interest Rates
Interest-rate shocks, duration and convexity sensitivity, interactive stress tests and yield-curve scenarios.

### Sovereign Risk Analytics
Sovereign bond risk, instrument-level analysis and portfolio what-if simulations.

### Portfolio Optimization
Sovereign allocation scenarios and historical tail-risk comparisons.

### Credit Risk Analytics
Analysis of a simulated loan portfolio containing 13,000 loans across four credit segments: Corporate, SME, Mortgage and Consumer.

The credit portfolio has approximately EUR 3.0 billion in Exposure at Default (EAD) and EUR 11.78 million in Expected Loss.

The dashboard includes portfolio credit KPIs, segment-level exposure and expected-loss analysis, credit-rating risk profiles and aggregated customer concentration metrics.

## 4. Risk Methodologies

### Historical Value at Risk
Historical VaR estimates a loss threshold using the empirical distribution of historical portfolio P&L.

### Expected Shortfall
Expected Shortfall measures average losses in the selected tail of the historical loss distribution.

### Fixed-Income Sensitivity
Duration, convexity and DV01 are used to approximate bond price sensitivity to changes in yields.

Second-order approximation:

Delta P / P = -Modified Duration x Delta Yield + 0.5 x Convexity x (Delta Yield)^2

### Stress Testing
Scenario analysis estimates the effect of changes in interest rates and other market risk factors.

### Sovereign Portfolio Optimization
Alternative sovereign allocations are evaluated using historical tail-risk measures and model assumptions.

### Credit Expected Loss
Expected Loss (EL) is estimated at loan level using:

`EL = PD x LGD x EAD`

Where:
- **PD** is Probability of Default.
- **LGD** is Loss Given Default.
- **EAD** is Exposure at Default.

Portfolio Expected Loss is the sum of individual loan expected losses. The dashboard also reports EAD-weighted PD and aggregated concentration indicators.

These are illustrative credit-risk calculations based on simulated data, not regulatory capital estimates.

## 5. Repository Structure

```text
bank-risk-analytics/
|-- dashboard/
|   |-- app.py
|   `-- credit_risk.py
|-- data/
|   `-- demo/
|       |-- portfolio/
|       |-- sovereign/
|       `-- credit/
|-- database/
|   `-- 03_credit_risk_analysis.sql
|-- src/
|   `-- atlas_bank/
|       `-- database.py
|-- requirements.txt
|-- requirements-database.txt
|-- .gitignore
`-- README.md
```

## 6. Installation

The project was developed and tested with Python 3.13.15.

Clone the repository:

```bash
git clone https://github.com/diogocorreiacampello/bank-risk-analytics.git
cd bank-risk-analytics
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

For local execution, Streamlit normally opens at http://localhost:8501.

**Live dashboard:** [Open Atlas Bank](https://bank-risk-analytics-glwtzxzs8qkycsestguv4a.streamlit.app/)

## 7. Optional Database Integration

The project also includes a PostgreSQL connection helper and an example SQL credit-risk analysis.

Database integration is optional for the dashboard.

```bash
pip install -r requirements-database.txt
```

Database credentials must never be committed to Git.

## 8. Validation

The dashboard was tested across six functional areas using Streamlit AppTest.

- Original Market Risk reconciliation: 51 displayed financial metrics, 14 tables and 23 chart specifications
- Combined dashboard component inventory: 58 metrics, 15 tables and 27 Plotly charts
- Six dashboard areas executed without exceptions
- Credit Risk Analytics validated with seven metrics, one table and four charts
- Credit demo datasets reconciled against aggregated PostgreSQL results

These checks confirm consistency between application versions, not independent validation of financial models.

## 9. Limitations

- Demonstration datasets are simulated or research-derived.
- Results are not live banking or market data.
- Historical risk estimates depend on the observation window.
- Stress scenarios use simplified assumptions.
- Duration and convexity are approximations.
- Optimization is based on historical assumptions.
- Transaction costs may be excluded from optimization results.
- Credit risk calculations use simulated loan data and simplified assumptions.
- The application is not a regulatory reporting system.

## 10. Roadmap

### Credit Risk
Implemented: interactive PD, LGD, EAD, Expected Loss and concentration analytics.

Potential extensions include credit migration analysis, scenario-based credit stress testing and more advanced portfolio credit-risk modelling.

### Liquidity Risk
Develop LCR, NSFR, funding structure and liquidity stress analytics.

### Engineering
Improve automated tests, reproducibility, documentation and deployment readiness.

## Disclaimer

Atlas Bank is an independent educational and portfolio project. It is not affiliated with a financial institution and does not provide investment advice or regulatory risk reporting.
