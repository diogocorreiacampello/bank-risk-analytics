"""Illustrative EUR liquidity coverage model for Atlas Bank.

This module is not a regulatory LCR reporting implementation.
All deposit classifications, HQLA eligibility assumptions and
cash inflows are simulated for research and education.
"""

import math

import pandas as pd


DEFAULT_ASSUMPTIONS = {
    "retail_stable_share": 0.70,
    "retail_stable_runoff": 0.05,
    "retail_less_stable_runoff": 0.10,
    "sme_runoff": 0.10,
    "corporate_runoff": 0.40,
    "gross_inflows": 50_000_000.0,
}

HQLA_ASSUMPTIONS = (
    ("Cash", 100_000_000.0, 0.00, "Level 1 (assumed)"),
    ("Central Bank Reserves", 150_000_000.0, 0.00, "Level 1 (assumed)"),
    ("Sovereign Bonds", 200_000_000.0, 0.00, "Level 1 (assumed)"),
)

SENSITIVITY_SCENARIOS = {
    "Base": {},
    "Lower Retail Stability": {"retail_stable_share": 0.50},
    "Higher Corporate Runoff": {"corporate_runoff": 0.50},
    "Reduced HQLA": {"hqla_multiplier": 400 / 450},
    "Combined Stress": {
        "retail_stable_share": 0.50,
        "corporate_runoff": 0.50,
        "hqla_multiplier": 400 / 450,
    },
}


def _validate_fraction(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a numeric fraction.")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")


def _validate_nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric.")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative.")


def calculate_lcr(segments, assumptions=None):
    """Calculate an illustrative EUR LCR and its supporting tables."""
    required = {"customer_type", "total_balance"}

    if not isinstance(segments, pd.DataFrame):
        raise ValueError("segments must be a pandas DataFrame.")
    if not required.issubset(segments.columns):
        raise ValueError("Missing required deposit columns.")
    if segments["customer_type"].duplicated().any():
        raise ValueError("Duplicate deposit segments.")

    balances = pd.to_numeric(
        segments["total_balance"], errors="coerce"
    )

    if not balances.notna().all():
        raise ValueError("Invalid deposit balances.")
    if not balances.map(math.isfinite).all():
        raise ValueError("Deposit balances must be finite.")
    if (balances < 0).any():
        raise ValueError("Deposit balances cannot be negative.")

    expected_segments = {"Retail", "SME", "Corporate"}

    if set(segments["customer_type"]) != expected_segments:
        raise ValueError("Expected Retail, SME and Corporate segments.")

    balance = dict(zip(segments["customer_type"], balances))

    params = DEFAULT_ASSUMPTIONS.copy()

    if assumptions is not None:
        if not isinstance(assumptions, dict):
            raise ValueError("assumptions must be a dictionary.")

        unknown = set(assumptions) - (
            set(DEFAULT_ASSUMPTIONS) | {"hqla_multiplier"}
        )

        if unknown:
            raise ValueError(f"Unknown assumptions: {sorted(unknown)}")

        params.update(assumptions)

    for name in (
        "retail_stable_share",
        "retail_stable_runoff",
        "retail_less_stable_runoff",
        "sme_runoff",
        "corporate_runoff",
    ):
        _validate_fraction(params[name], name)

    _validate_nonnegative(params["gross_inflows"], "gross_inflows")

    multiplier = params.get("hqla_multiplier", 1.0)
    _validate_fraction(multiplier, "hqla_multiplier")

    outflows = pd.DataFrame([
        {
            "category": "Retail - Stable (assumed)",
            "balance": balance["Retail"] * params["retail_stable_share"],
            "runoff_rate": params["retail_stable_runoff"],
        },
        {
            "category": "Retail - Less Stable (assumed)",
            "balance": balance["Retail"] * (
                1 - params["retail_stable_share"]
            ),
            "runoff_rate": params["retail_less_stable_runoff"],
        },
        {
            "category": "SME - Simplified",
            "balance": balance["SME"],
            "runoff_rate": params["sme_runoff"],
        },
        {
            "category": "Corporate - Simplified",
            "balance": balance["Corporate"],
            "runoff_rate": params["corporate_runoff"],
        },
    ])

    outflows["cash_outflow"] = (
        outflows["balance"] * outflows["runoff_rate"]
    )

    hqlas = pd.DataFrame(
        HQLA_ASSUMPTIONS,
        columns=["asset", "gross_value", "haircut", "assumed_level"],
    )

    hqlas["eligible_value"] = (
        hqlas["gross_value"]
        * (1 - hqlas["haircut"])
        * multiplier
    )

    gross_outflows = float(outflows["cash_outflow"].sum())
    gross_inflows = float(params["gross_inflows"])
    inflow_cap = 0.75 * gross_outflows
    eligible_inflows = min(gross_inflows, inflow_cap)
    net_outflows = gross_outflows - eligible_inflows
    hqla_total = float(hqlas["eligible_value"].sum())

    if net_outflows <= 0:
        raise ValueError(
            "Net cash outflows must be positive for an LCR calculation."
        )

    metrics = {
        "total_deposits": float(sum(balance.values())),
        "gross_outflows": gross_outflows,
        "gross_inflows": gross_inflows,
        "inflow_cap": inflow_cap,
        "eligible_inflows": eligible_inflows,
        "net_outflows": net_outflows,
        "hqla": hqla_total,
        "lcr_pct": 100 * hqla_total / net_outflows,
        "hqla_gap": hqla_total - net_outflows,
    }

    return metrics, outflows, hqlas


def calculate_lcr_sensitivity(segments):
    """Calculate the five illustrative LCR sensitivity scenarios."""
    rows = []

    for scenario, assumptions in SENSITIVITY_SCENARIOS.items():
        metrics, _, _ = calculate_lcr(segments, assumptions)

        rows.append({
            "scenario": scenario,
            "gross_outflows_m": metrics["gross_outflows"] / 1e6,
            "net_outflows_m": metrics["net_outflows"] / 1e6,
            "hqla_m": metrics["hqla"] / 1e6,
            "lcr_pct": metrics["lcr_pct"],
            "hqla_gap_m": metrics["hqla_gap"] / 1e6,
        })

    return pd.DataFrame(rows)


def render_lcr(segments):
    """Render illustrative EUR LCR analytics in Streamlit."""
    import plotly.express as px
    import plotly.graph_objects as go
    import streamlit as st

    st.subheader("Liquidity Coverage Ratio (LCR)")
    st.caption(
        "Illustrative EUR 30-day liquidity coverage model. "
        "Not a regulatory LCR calculation or compliance assessment."
    )

    metrics, outflows, hqlas = calculate_lcr(segments)
    sensitivity = calculate_lcr_sensitivity(segments)

    scenario_names = sensitivity["scenario"].tolist()

    selected_scenario = st.selectbox(
        "LCR Sensitivity Scenario",
        options=scenario_names,
        index=0,
        key="lcr_sensitivity_scenario",
    )

    scenario_assumptions = SENSITIVITY_SCENARIOS[selected_scenario]

    selected_metrics, selected_outflows, selected_hqlas = calculate_lcr(
        segments,
        scenario_assumptions,
    )

    st.markdown("#### 30-Day Liquidity Coverage")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Illustrative LCR",
        f"{selected_metrics['lcr_pct']:.2f}%",
        delta=f"{selected_metrics['lcr_pct'] - 100:+.2f} pp vs 100%",
    )

    col2.metric(
        "Assumed HQLA",
        f"€{selected_metrics['hqla'] / 1e6:,.2f}M",
    )

    col3.metric(
        "Net Cash Outflows",
        f"€{selected_metrics['net_outflows'] / 1e6:,.2f}M",
    )

    col4.metric(
        "HQLA Surplus / Shortfall",
        f"€{selected_metrics['hqla_gap'] / 1e6:+,.2f}M",
    )

    st.caption(
        "The 100% reference is shown for analytical comparison only. "
        "Actual regulatory compliance cannot be determined from "
        "the available simulated data."
    )

    st.markdown("#### Cash Outflow Composition")

    outflow_chart = selected_outflows.copy()
    outflow_chart["cash_outflow_m"] = (
        outflow_chart["cash_outflow"] / 1e6
    )

    fig_outflows = px.bar(
        outflow_chart,
        x="category",
        y="cash_outflow_m",
        color="category",
        title="30-Day Deposit Outflows by Category",
        labels={
            "category": "Deposit Category",
            "cash_outflow_m": "Cash Outflows (€M)",
        },
    )

    fig_outflows.update_layout(
        showlegend=False,
        xaxis_tickangle=-20,
    )

    st.plotly_chart(
        fig_outflows,
        width="stretch",
    )

    st.dataframe(
        selected_outflows,
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### Assumed HQLA Composition")

    hqlas_chart = selected_hqlas.copy()
    hqlas_chart["eligible_value_m"] = (
        hqlas_chart["eligible_value"] / 1e6
    )

    fig_hqla = px.pie(
        hqlas_chart,
        names="asset",
        values="eligible_value_m",
        title="Assumed HQLA by Asset Type",
        hole=0.45,
    )

    st.plotly_chart(
        fig_hqla,
        width="stretch",
    )

    st.dataframe(
        selected_hqlas,
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### LCR Sensitivity Analysis")

    fig_sensitivity = go.Figure()

    fig_sensitivity.add_trace(
        go.Bar(
            x=sensitivity["scenario"],
            y=sensitivity["lcr_pct"],
            name="Illustrative LCR",
            text=[
                f"{value:.2f}%"
                for value in sensitivity["lcr_pct"]
            ],
            textposition="outside",
        )
    )

    fig_sensitivity.add_hline(
        y=100,
        line_dash="dash",
        annotation_text="100% analytical reference",
    )

    fig_sensitivity.update_layout(
        title="Illustrative LCR Across Sensitivity Scenarios",
        xaxis_title="Scenario",
        yaxis_title="LCR (%)",
        yaxis_range=[
            0,
            max(120, sensitivity["lcr_pct"].max() * 1.15),
        ],
    )

    st.plotly_chart(
        fig_sensitivity,
        width="stretch",
    )

    st.dataframe(
        sensitivity,
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### Model Assumptions and Limitations")

    st.info(
        "Retail stability shares, deposit runoff rates, "
        "HQLA eligibility and inflows are illustrative assumptions. "
        "The model applies a simplified 75% inflow cap. "
        "It excludes GBP/USD funding, contractual cash-flow detail, "
        "asset encumbrance, HQLA operational requirements and "
        "regulatory classification tests."
    )

    return {
        "selected_scenario": selected_scenario,
        "metrics": selected_metrics,
        "outflows": selected_outflows,
        "hqlas": selected_hqlas,
        "sensitivity": sensitivity,
    }
