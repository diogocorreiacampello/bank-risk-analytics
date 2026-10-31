# Atlas Bank - Bank Risk Analytics Platform

An interactive banking risk analytics project built with **Python, SQL, Pandas, NumPy, Plotly and Streamlit**.

Atlas Bank simulates a multi-asset investment portfolio and a banking loan book, providing quantitative tools for market risk, interest-rate sensitivity, stress testing, sovereign risk, portfolio optimization, credit risk and liquidity risk analytics.

> **Status:** Seven analytics areas are available in the public dashboard, including Deposit Runoff Stress Testing and Liquidity Buffer & Survival Horizon. An illustrative Liquidity Coverage Ratio (LCR) module has been implemented and validated locally, pending deployment.

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
- Deposit composition, customer concentration and geographic analysis
- Funding structure, maturity profiles and counterparty concentration
- Scenario-based deposit runoff stress testing and segment contributions

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

### Liquidity Risk Analytics
Analysis of a simulated deposit base containing 50,000 accounts and EUR 3.5 billion in deposits, together with 22 funding contracts denominated in EUR, GBP and USD.

The dashboard includes deposit KPIs, customer segmentation, geographic distribution, concentration indicators, funding structure, maturity buckets and counterparty exposures.

An interactive Deposit Runoff Stress Testing section evaluates Base, Moderate Stress and Severe Stress scenarios, including estimated deposit outflows and segment-level contributions.

A Liquidity Buffer & Survival Horizon section models a simulated portfolio of liquid assets, haircut-adjusted available liquidity, 30-day cumulative deposit outflows and the first day of a simulated funding gap.

An illustrative Liquidity Coverage Ratio (LCR) section estimates 30-day net cash outflows, assumed HQLA, liquidity coverage and sensitivity across five scenarios. This is a simplified research model, not regulatory LCR reporting.

Funding amounts are reported separately by currency, without implicit FX conversion. Maturity buckets use a fixed reference date of **2026-10-26**.

The deposit and funding analytics, Deposit Runoff Stress Testing and Liquidity Buffer & Survival Horizon are publicly deployed. The illustrative LCR extension is implemented and tested locally, pending deployment.

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

### Liquidity Concentration and Funding Analysis
Deposit concentration is measured using Top 1, Top 5 and Top 10 depositor shares and the Herfindahl-Hirschman Index (HHI).

`HHI = sum((Customer Deposit Balance / Total Deposit Balance)^2)`

The effective number of depositors is approximated as `1 / HHI`.

Funding analytics include amount-weighted interest rates, maturity buckets and counterparty concentration, calculated separately for each currency.

These are descriptive liquidity and funding indicators. A separate illustrative LCR model is documented below; regulatory LCR and NSFR calculations are not provided.

### Deposit Runoff Stress Testing

The deposit runoff model applies illustrative withdrawal assumptions to the simulated EUR 3.5 billion deposit base, segmented into Retail, SME and Corporate customers.

| Customer segment | Base | Moderate Stress | Severe Stress |
|---|---:|---:|---:|
| Retail | 3% | 5% | 10% |
| SME | 5% | 10% | 20% |
| Corporate | 8% | 15% | 30% |

For each segment and scenario:

`Deposit Outflow = Segment Deposit Balance * Runoff Rate`

Total scenario outflow is the sum of the three segment outflows.

| Scenario | Estimated outflow | Share of total deposits |
|---|---:|---:|
| Base | EUR 150.61 million | 4.30% |
| Moderate Stress | EUR 272.69 million | 7.79% |
| Severe Stress | EUR 545.38 million | 15.58% |

Segment contribution is calculated as the segment's outflow divided by total scenario outflow. Stress amplification is defined as the segment's outflow contribution divided by its share of total deposits.

Under Severe Stress, Retail contributes approximately 40.34% of total outflows, Corporate 35.96% and SME 23.70%.

These assumptions are illustrative rather than empirically calibrated or regulatory runoff rates. The standalone deposit runoff model estimates withdrawals only. The separate Liquidity Buffer & Survival Horizon extension compares these withdrawals with an illustrative liquidity reserve and estimates the first funding-gap day. Neither model independently calculates regulatory net cash outflows, LCR or NSFR. The separate illustrative LCR module uses different assumptions and should not be interpreted as the coverage ratio of the liquidity-buffer simulation.

### Liquidity Buffer & Survival Horizon

This extension uses the same simulated EUR 3.5 billion deposit base and the three runoff scenarios defined above. The liquid asset portfolio is illustrative and is not derived from observed bank holdings.

| Liquid asset | Gross value | Haircut | Available value |
|---|---:|---:|---:|
| Cash | EUR 100 million | 0% | EUR 100 million |
| Central bank reserves | EUR 150 million | 0% | EUR 150 million |
| Sovereign bonds | EUR 200 million | 5% | EUR 190 million |
| **Total** | **EUR 450 million** | | **EUR 440 million** |

`Available Asset Value = Gross Asset Value * (1 - Haircut)`

The model assumes that 40% of each scenario's total deposit withdrawals occur during days 1-7, 35% during days 8-14 and 25% during days 15-30. Withdrawals are allocated uniformly within each interval.

`Remaining Buffer (Day t) = Initial Available Buffer - Cumulative Deposit Outflows (Day t)`

`30-Day Coverage Gap = Initial Available Buffer - Total 30-Day Deposit Outflows`

`Coverage Ratio = Initial Available Buffer / Total 30-Day Deposit Outflows`

The first buffer breach is the first simulated day when the remaining buffer becomes negative. If no breach occurs, the dashboard reports no breach within the 30-day modelling horizon.

| Scenario | 30-day outflows | Coverage gap | Coverage ratio | First breach |
|---|---:|---:|---:|---|
| Base | EUR 150.61 million | +EUR 289.39 million | 292.14% | None within 30 days |
| Moderate Stress | EUR 272.69 million | +EUR 167.31 million | 161.36% | None within 30 days |
| Severe Stress | EUR 545.38 million | -EUR 105.38 million | 80.68% | Day 18 |

Under Severe Stress, the remaining buffer is approximately EUR 5.40 million on day 17 and becomes approximately negative EUR 3.12 million on day 18.

The model assumes a static, immediately available liquidity reserve and gross deposit outflows only. It excludes other cash inflows and outflows, additional funding, asset replenishment, intraday liquidity, and regulatory eligibility or operational constraints. The resulting coverage ratio is a simulation metric, not the regulatory Liquidity Coverage Ratio (LCR). A negative buffer indicates a simulated funding gap, not a prediction of bank failure.

### Illustrative Liquidity Coverage Ratio (LCR)

The LCR extension estimates a simplified 30-day liquidity coverage ratio using simulated EUR deposits, assumed High Quality Liquid Assets (HQLA) and illustrative cash inflows. It is designed for financial risk analytics and scenario analysis, not regulatory reporting.

`Illustrative LCR = Assumed HQLA / Illustrative 30-Day Net Cash Outflows * 100`

`Illustrative Net Cash Outflows = Gross Cash Outflows - Eligible Cash Inflows`

The base model applies the following assumptions:

| Component | Illustrative assumption |
|---|---|
| Retail deposits | 70% stable at 5% runoff; 30% less stable at 10% runoff |
| SME deposits | 10% runoff |
| Corporate deposits | 40% runoff |
| Assumed HQLA | EUR 100 million cash, EUR 150 million central bank reserves and EUR 200 million sovereign bonds |
| HQLA haircuts | 0% in this illustrative LCR model |
| Gross cash inflows | EUR 50 million |
| Eligible inflows | Capped at 75% of gross outflows |

The HQLA assumptions in this model are separate from the haircut-adjusted EUR 440 million liquidity buffer used in the survival-horizon analysis. They are not interchangeable regulatory classifications.

**Base scenario results:**

| Metric | Illustrative result |
|---|---:|
| Gross 30-day outflows | EUR 469.13 million |
| Eligible 30-day inflows | EUR 50.00 million |
| Net 30-day outflows | EUR 419.13 million |
| Assumed HQLA | EUR 450.00 million |
| Illustrative LCR | 107.37% |
| HQLA surplus / deficit | EUR +30.87 million |

**Sensitivity analysis:**

| Scenario | Illustrative LCR | HQLA surplus / deficit |
|---|---:|---:|
| Base | 107.37% | EUR +30.87 million |
| Lower Retail Stability | 102.01% | EUR +8.87 million |
| Higher Corporate Runoff | 92.88% | EUR -34.50 million |
| Reduced HQLA | 95.44% | EUR -19.13 million |
| Combined Stress | 78.97% | EUR -106.50 million |

The five scenarios assess the sensitivity of the simplified liquidity coverage estimate to retail deposit stability, corporate withdrawals and available HQLA.

The model does not establish regulatory HQLA eligibility, encumbrance, operational requirements, deposit stability classifications or the complete contractual cash-flow profile. It excludes a comprehensive treatment of secured funding, additional inflows and outflows, foreign-currency liquidity and regulatory reporting adjustments. A result above or below 100% must not be interpreted as a verified regulatory compliance outcome.

## 5. Repository Structure

```text
bank-risk-analytics/
|-- dashboard/
|   |-- app.py
|   |-- credit_risk.py
|   |-- liquidity_risk.py
|   |-- liquidity_stress.py
|   |-- liquidity_buffer.py
|   `-- liquidity_lcr.py
|-- data/
|   `-- demo/
|       |-- portfolio/
|       |-- sovereign/
|       |-- credit/
|       `-- liquidity/  # Nine aggregated CSV datasets
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

The dashboard was tested across seven functional areas using Streamlit AppTest.

- Original Market Risk reconciliation: 51 displayed financial metrics, 14 tables and 23 chart specifications
- Combined dashboard component inventory: 78 metrics, 22 tables and 40 Plotly charts
- Seven dashboard areas executed without exceptions
- Credit Risk Analytics validated with seven metrics, one table and four charts
- Credit demo datasets reconciled against aggregated PostgreSQL results
- Liquidity Risk Analytics, including deposit runoff, liquidity buffer and illustrative LCR analytics, validated with 20 metrics, seven tables and 13 Plotly charts
- Nine liquidity CSV datasets validated and financially reconciled
- Deposit runoff calculations reconciled across three scenarios
- Nine funding-currency and stress-scenario combinations passed Streamlit AppTest
- Liquidity buffer calculations reconciled across all three runoff scenarios, including the Severe Stress breach on day 18
- Full liquidity page tested with independent funding-currency, runoff-scenario, buffer-scenario and LCR-sensitivity selectors
- Illustrative LCR reconciled across five sensitivity scenarios, including Base 107.37% and Combined Stress 78.97%
- All seven dashboard pages passed Streamlit AppTest with 78 metrics, 22 tables and 40 Plotly charts

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
- Liquidity analytics use simulated data and simplified assumptions.
- Deposit runoff rates are illustrative and are not empirically calibrated.
- Deposit runoff outflows are compared with a separately simulated, haircut-adjusted liquidity buffer; the buffer is not based on observed bank assets.
- Daily runoff timing, liquidity availability and asset haircuts are illustrative rather than empirically calibrated.
- The survival horizon is limited to a 30-day simulation and does not incorporate other funding sources or cash flows.
- An illustrative LCR is calculated, but it is not a regulatory LCR assessment. Regulatory LCR and NSFR are not calculated.
- Funding balances in different currencies are not aggregated without FX conversion.
- The application is not a regulatory reporting system.

## 10. Roadmap

### Credit Risk
Implemented: interactive PD, LGD, EAD, Expected Loss and concentration analytics.

Potential extensions include credit migration analysis, scenario-based credit stress testing and more advanced portfolio credit-risk modelling.

### Liquidity Risk
Implemented: deposit composition, concentration, funding structure, maturity analysis and counterparty exposures.

Implemented and publicly deployed: three deposit runoff stress scenarios with segment-level outflow and contribution analysis.

Implemented and publicly deployed: haircut-adjusted liquidity buffer, 30-day cash outflow profiles, coverage gaps and simulated survival horizons.

Implemented locally, pending deployment: illustrative LCR with assumed HQLA, 30-day net outflows and five sensitivity scenarios.

Planned extensions: more comprehensive regulatory LCR and NSFR modelling, advanced funding stress testing, empirically calibrated liquidity buffers, dynamic cash-flow modelling and extended survival horizon analysis.

### Engineering
Improve automated tests, reproducibility, documentation and deployment readiness.

## Disclaimer

Atlas Bank is an independent educational and portfolio project. It is not affiliated with a financial institution and does not provide investment advice or regulatory risk reporting.
