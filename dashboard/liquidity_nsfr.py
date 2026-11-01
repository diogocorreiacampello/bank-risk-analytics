"""Illustrative Net Stable Funding Ratio analytics for Atlas Bank."""

import math
from pathlib import Path

import pandas as pd


DEPOSIT_FACTORS = {
    "Retail": 0.90,
    "SME": 0.50,
    "Corporate": 0.00,
}

FUNDING_FACTORS = {
    ">365 days": 1.00,
    "181-365 days": 0.50,
    "91-180 days": 0.00,
    "31-90 days": 0.00,
    "0-30 days": 0.00,
}

INVESTMENT_FACTORS = {
    "Alternative": 1.00,
    "Commodity": 1.00,
    "Corporate Bonds": 0.85,
    "Equities": 0.85,
    "European Sovereigns": 0.05,
    "FX": 1.00,
    "Short-Term Instruments": 0.15,
    "US Treasuries": 0.05,
}

SENSITIVITY_SCENARIOS = {
    "Baseline V1": {
        "corporate_asf_factor": 0.00,
        "credit_rsf_factor": 0.85,
        "include_fx": True,
    },
    "Exclude FX Proxy": {
        "corporate_asf_factor": 0.00,
        "credit_rsf_factor": 0.85,
        "include_fx": False,
    },
    "Corporate ASF 50%": {
        "corporate_asf_factor": 0.50,
        "credit_rsf_factor": 0.85,
        "include_fx": True,
    },
    "Higher Credit RSF": {
        "corporate_asf_factor": 0.00,
        "credit_rsf_factor": 1.00,
        "include_fx": True,
    },
    "Combined Alternative": {
        "corporate_asf_factor": 0.50,
        "credit_rsf_factor": 0.85,
        "include_fx": False,
    },
}


def _validate_factor(value, name):
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid factor: {name}") from exc

    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")

    return value


def _validate_table(df, category, amount, expected):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a DataFrame.")

    if not {category, amount}.issubset(df.columns):
        raise ValueError(f"Missing columns: {category}, {amount}")

    result = df.copy()

    if result[category].isna().any():
        raise ValueError(f"Missing values in {category}.")

    if result[category].duplicated().any():
        raise ValueError(f"Duplicate categories in {category}.")

    if set(result[category]) != set(expected):
        raise ValueError(f"Unexpected categories in {category}.")

    result[amount] = pd.to_numeric(
        result[amount], errors="coerce"
    )

    if not result[amount].notna().all():
        raise ValueError(f"Invalid amounts in {amount}.")

    if not result[amount].map(math.isfinite).all():
        raise ValueError(f"Non-finite amounts in {amount}.")

    if (result[amount] < 0).any():
        raise ValueError(f"Negative amounts in {amount}.")

    return result


def load_nsfr_data(project_root=None):
    """Load existing simulated datasets without modifying them."""
    if project_root is None:
        project_root = Path(__file__).resolve().parents[1]

    base = Path(project_root) / "data" / "demo"

    deposits = pd.read_csv(
        base / "liquidity" / "liquidity_deposit_segments.csv"
    )

    funding = pd.read_csv(
        base / "liquidity" / "liquidity_funding_maturity.csv"
    )

    credit = pd.read_csv(
        base / "credit" / "credit_segment_risk.csv"
    )

    investments = pd.read_csv(
        base / "portfolio" / "stress_by_asset_group.csv"
    )

    return deposits, funding, credit, investments


def calculate_nsfr(
    deposits,
    funding,
    credit,
    investments,
    corporate_asf_factor=0.00,
    credit_rsf_factor=0.85,
    include_fx=True,
):
    """Calculate illustrative NSFR and its ASF/RSF breakdowns."""

    corporate_asf_factor = _validate_factor(
        corporate_asf_factor, "corporate_asf_factor"
    )

    credit_rsf_factor = _validate_factor(
        credit_rsf_factor, "credit_rsf_factor"
    )

    if not isinstance(include_fx, bool):
        raise ValueError("include_fx must be boolean.")

    deposits = _validate_table(
        deposits,
        "customer_type",
        "total_balance",
        DEPOSIT_FACTORS,
    )

    funding = funding.copy()

    required_funding = {
        "currency", "maturity_bucket", "total_amount"
    }

    if not required_funding.issubset(funding.columns):
        raise ValueError("Missing funding columns.")

    if funding["currency"].isna().any():
        raise ValueError("Missing funding currency.")

    eur_funding = funding.loc[
        funding["currency"] == "EUR"
    ].copy()

    eur_funding = _validate_table(
        eur_funding,
        "maturity_bucket",
        "total_amount",
        set(eur_funding["maturity_bucket"]),
    )

    if not set(eur_funding["maturity_bucket"]).issubset(
        FUNDING_FACTORS
    ):
        raise ValueError("Unknown funding maturity bucket.")

    credit = credit.copy()
    credit["loan_type"] = credit["loan_type"].str.strip()

    credit = _validate_table(
        credit,
        "loan_type",
        "total_ead",
        {"Corporate", "Mortgage", "SME", "Consumer"},
    )

    investments = _validate_table(
        investments,
        "asset_group",
        "exposure",
        INVESTMENT_FACTORS,
    )

    deposit_factors = DEPOSIT_FACTORS.copy()
    deposit_factors["Corporate"] = corporate_asf_factor

    deposits["factor"] = deposits["customer_type"].map(
        deposit_factors
    )

    deposits["asf"] = (
        deposits["total_balance"] * deposits["factor"]
    )

    eur_funding["factor"] = (
        eur_funding["maturity_bucket"].map(FUNDING_FACTORS)
    )

    eur_funding["asf"] = (
        eur_funding["total_amount"] * eur_funding["factor"]
    )

    credit["factor"] = credit_rsf_factor

    credit["rsf"] = (
        credit["total_ead"] * credit["factor"]
    )

    investments["factor"] = (
        investments["asset_group"].map(INVESTMENT_FACTORS)
    )

    if not include_fx:
        investments = investments.loc[
            investments["asset_group"] != "FX"
        ].copy()

    investments["rsf"] = (
        investments["exposure"] * investments["factor"]
    )

    asf_deposits = float(deposits["asf"].sum())
    asf_funding = float(eur_funding["asf"].sum())

    rsf_credit = float(credit["rsf"].sum())
    rsf_investments = float(investments["rsf"].sum())

    total_asf = asf_deposits + asf_funding
    total_rsf = rsf_credit + rsf_investments

    if total_rsf <= 0:
        raise ValueError("RSF must be positive.")

    metrics = {
        "asf_deposits": asf_deposits,
        "asf_funding": asf_funding,
        "total_asf": total_asf,
        "rsf_credit": rsf_credit,
        "rsf_investments": rsf_investments,
        "total_rsf": total_rsf,
        "nsfr_pct": total_asf / total_rsf * 100,
        "funding_gap": total_asf - total_rsf,
    }

    breakdowns = {
        "deposits": deposits,
        "funding": eur_funding,
        "credit": credit,
        "investments": investments,
    }

    return metrics, breakdowns


def calculate_nsfr_sensitivity(
    deposits, funding, credit, investments
):
    """Calculate five illustrative NSFR sensitivity scenarios."""
    rows = []

    for name, assumptions in SENSITIVITY_SCENARIOS.items():
        metrics, _ = calculate_nsfr(
            deposits,
            funding,
            credit,
            investments,
            **assumptions,
        )

        rows.append({
            "scenario": name,
            "asf_m": metrics["total_asf"] / 1e6,
            "rsf_m": metrics["total_rsf"] / 1e6,
            "nsfr_pct": metrics["nsfr_pct"],
            "funding_gap_m": metrics["funding_gap"] / 1e6,
        })

    result = pd.DataFrame(rows)

    result["delta_pp"] = (
        result["nsfr_pct"] - result.loc[0, "nsfr_pct"]
    )

    return result


def render_nsfr():
    """Render illustrative NSFR analytics in Streamlit."""
    import plotly.express as px
    import plotly.graph_objects as go
    import streamlit as st

    st.subheader("Net Stable Funding Ratio (NSFR)")

    st.caption(
        "Illustrative structural funding model based on simulated "
        "deposits, EUR funding, credit EAD and investment exposures. "
        "Not a regulatory NSFR calculation or compliance assessment."
    )

    deposits, funding, credit, investments = load_nsfr_data()

    sensitivity = calculate_nsfr_sensitivity(
        deposits, funding, credit, investments
    )

    scenario_names = sensitivity["scenario"].tolist()

    selected_scenario = st.selectbox(
        "NSFR Sensitivity Scenario",
        options=scenario_names,
        index=0,
        key="nsfr_sensitivity_scenario",
    )

    assumptions = SENSITIVITY_SCENARIOS[selected_scenario]

    metrics, breakdowns = calculate_nsfr(
        deposits,
        funding,
        credit,
        investments,
        **assumptions,
    )

    baseline_pct = float(
        sensitivity.loc[
            sensitivity["scenario"] == "Baseline V1",
            "nsfr_pct",
        ].iloc[0]
    )

    delta_pp = metrics["nsfr_pct"] - baseline_pct

    st.markdown("#### Structural Funding Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Illustrative NSFR",
        f"{metrics['nsfr_pct']:.2f}%",
        delta=f"{delta_pp:+.2f} pp vs baseline",
    )

    c2.metric(
        "Available Stable Funding",
        f"€{metrics['total_asf'] / 1e6:,.2f}M",
    )

    c3.metric(
        "Required Stable Funding",
        f"€{metrics['total_rsf'] / 1e6:,.2f}M",
    )

    c4.metric(
        "ASF - RSF Gap",
        f"€{metrics['funding_gap'] / 1e6:,.2f}M",
    )

    st.caption(
        "The 100% reference is an analytical benchmark only. "
        "The model does not establish regulatory compliance."
    )

    st.markdown("#### ASF and RSF Composition")

    composition = pd.DataFrame({
        "Component": [
            "Deposits (ASF)",
            "EUR Funding (ASF)",
            "Credit (RSF)",
            "Investments (RSF)",
        ],
        "Amount (EUR M)": [
            metrics["asf_deposits"] / 1e6,
            metrics["asf_funding"] / 1e6,
            metrics["rsf_credit"] / 1e6,
            metrics["rsf_investments"] / 1e6,
        ],
        "Side": ["ASF", "ASF", "RSF", "RSF"],
    })

    fig_composition = px.bar(
        composition,
        x="Side",
        y="Amount (EUR M)",
        color="Component",
        barmode="stack",
        title="Stable Funding Supply vs Requirements",
    )

    fig_composition.update_layout(
        legend_title_text="Component",
        margin=dict(t=55, b=20),
    )

    st.plotly_chart(
        fig_composition,
        width="stretch",
    )

    st.markdown("#### NSFR Sensitivity Analysis")

    fig_sensitivity = go.Figure()

    fig_sensitivity.add_trace(
        go.Bar(
            x=sensitivity["scenario"],
            y=sensitivity["nsfr_pct"],
            name="Illustrative NSFR",
            text=sensitivity["nsfr_pct"].map(
                lambda x: f"{x:.2f}%"
            ),
            textposition="outside",
        )
    )

    fig_sensitivity.add_hline(
        y=100,
        line_dash="dash",
        annotation_text="100% analytical reference",
    )

    fig_sensitivity.update_layout(
        title="NSFR by Assumption Scenario",
        xaxis_title="Scenario",
        yaxis_title="NSFR (%)",
        yaxis=dict(range=[0, max(
            110, sensitivity["nsfr_pct"].max() * 1.15
        )]),
        margin=dict(t=65, b=20),
    )

    st.plotly_chart(
        fig_sensitivity,
        width="stretch",
    )

    st.dataframe(
        sensitivity.rename(columns={
            "scenario": "Scenario",
            "asf_m": "ASF (EUR M)",
            "rsf_m": "RSF (EUR M)",
            "nsfr_pct": "NSFR (%)",
            "funding_gap_m": "Funding Gap (EUR M)",
            "delta_pp": "Delta (pp)",
        }).round(2),
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### Detailed ASF and RSF Contributions")

    detail_frames = []

    for key, side, category, amount, weighted in [
        (
            "deposits", "ASF", "customer_type",
            "total_balance", "asf",
        ),
        (
            "funding", "ASF", "maturity_bucket",
            "total_amount", "asf",
        ),
        (
            "credit", "RSF", "loan_type",
            "total_ead", "rsf",
        ),
        (
            "investments", "RSF", "asset_group",
            "exposure", "rsf",
        ),
    ]:
        frame = breakdowns[key].copy()

        detail_frames.append(pd.DataFrame({
            "Side": side,
            "Source": key.title(),
            "Category": frame[category].astype(str),
            "Exposure (EUR M)": frame[amount] / 1e6,
            "Factor (%)": frame["factor"] * 100,
            "Weighted Amount (EUR M)": frame[weighted] / 1e6,
        }))

    detail = pd.concat(
        detail_frames,
        ignore_index=True,
    )

    st.dataframe(
        detail.round(2),
        width="stretch",
        hide_index=True,
    )

    with st.expander("Methodology and Model Limitations"):
        st.markdown(
            """
            **Methodology**

            - NSFR = Available Stable Funding / Required Stable Funding.
            - ASF uses simulated deposit balances and EUR funding.
            - RSF uses credit EAD and investment risk exposures as proxies.
            - Factors and scenarios are illustrative assumptions.
            - The baseline is preserved as Baseline V1.

            **Limitations**

            - Not a regulatory NSFR calculation.
            - No accounting balance-sheet reconciliation.
            - Credit EAD is not necessarily an accounting asset value.
            - GBP/USD funding is excluded without FX conversion.
            - Investment currency exposures may not be EUR-valued.
            - FX positions may represent notionals rather than assets.
            - HQLA eligibility and encumbrance are not verified.
            - Deposit stability and loan maturities are assumed.
            - No additional capital or LCR HQLA is introduced.
            - A scenario above 100% would not demonstrate compliance.
            """
        )
