import pandas as pd
import plotly.express as px
import streamlit as st


SCENARIOS = {
    "Base": {
        "Retail": 0.03,
        "SME": 0.05,
        "Corporate": 0.08,
    },
    "Moderate Stress": {
        "Retail": 0.05,
        "SME": 0.10,
        "Corporate": 0.15,
    },
    "Severe Stress": {
        "Retail": 0.10,
        "SME": 0.20,
        "Corporate": 0.30,
    },
}


def calculate_deposit_runoff(segments):
    """Calculate illustrative 30-day deposit runoff scenarios."""

    required = {"customer_type", "total_balance"}

    if not required.issubset(segments.columns):
        raise ValueError("Missing required deposit segment columns.")

    if segments[list(required)].isna().any().any():
        raise ValueError("Deposit segment data contains missing values.")

    if segments["customer_type"].duplicated().any():
        raise ValueError("Duplicate customer segments detected.")

    if set(segments["customer_type"]) != {
        "Retail", "SME", "Corporate"
    }:
        raise ValueError("Unexpected customer segments.")

    if not pd.api.types.is_numeric_dtype(
        segments["total_balance"]
    ):
        raise ValueError("Deposit balances must be numeric.")

    if not (
        segments["total_balance"].map(
            lambda x: pd.notna(x) and float("-inf") < x < float("inf")
        )
    ).all():
        raise ValueError("Non-finite deposit balances detected.")

    if (segments["total_balance"] <= 0).any():
        raise ValueError("Deposit balances must be positive.")

    total_deposits = float(segments["total_balance"].sum())

    records = []

    for scenario, rates in SCENARIOS.items():
        for _, row in segments.iterrows():

            segment = row["customer_type"]
            balance = float(row["total_balance"])
            rate = rates[segment]
            outflow = balance * rate

            records.append({
                "scenario": scenario,
                "customer_type": segment,
                "deposit_balance": balance,
                "runoff_rate": rate,
                "outflow_eur": outflow,
                "remaining_deposits_eur": balance - outflow,
            })

    results = pd.DataFrame(records)

    results["deposit_weight"] = (
        results["deposit_balance"] / total_deposits
    )

    results["outflow_contribution"] = (
        results["outflow_eur"]
        / results.groupby("scenario")["outflow_eur"].transform("sum")
    )

    results["stress_amplification"] = (
        results["outflow_contribution"]
        / results["deposit_weight"]
    )

    summary = (
        results.groupby("scenario", as_index=False)
        .agg(
            total_outflow_eur=("outflow_eur", "sum"),
            remaining_deposits_eur=(
                "remaining_deposits_eur", "sum"
            ),
        )
    )

    summary["outflow_rate"] = (
        summary["total_outflow_eur"] / total_deposits
    )

    return results, summary


def render_liquidity_stress(segments):
    """Render illustrative deposit runoff stress analytics."""

    st.subheader("Deposit Runoff Stress Testing")

    st.caption(
        "Illustrative 30-day deposit withdrawal scenarios. "
        "Runoff rates are hypothetical, not regulatory LCR assumptions."
    )

    results, summary = calculate_deposit_runoff(segments)

    scenario = st.selectbox(
        "Stress Scenario",
        list(SCENARIOS),
        key="liquidity_stress_scenario",
    )

    selected = results[results["scenario"] == scenario].copy()

    selected_summary = summary[
        summary["scenario"] == scenario
    ].iloc[0]

    largest = selected.loc[
        selected["outflow_eur"].idxmax(),
        "customer_type",
    ]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Deposit Outflow",
        f"€{selected_summary['total_outflow_eur']/1e6:,.2f}M",
    )

    c2.metric(
        "Outflow Rate",
        f"{selected_summary['outflow_rate']:.2%}",
    )

    c3.metric(
        "Remaining Deposits",
        f"€{selected_summary['remaining_deposits_eur']/1e6:,.2f}M",
    )

    c4.metric("Largest Contributor", largest)

    comparison = summary.copy()

    comparison["scenario"] = pd.Categorical(
        comparison["scenario"],
        categories=list(SCENARIOS),
        ordered=True,
    )

    comparison = comparison.sort_values("scenario")

    fig = px.bar(
        comparison,
        x="scenario",
        y="total_outflow_eur",
        title="Deposit Outflows by Stress Scenario",
        labels={
            "scenario": "Scenario",
            "total_outflow_eur": "Outflow (EUR)",
        },
    )

    st.plotly_chart(fig, width="stretch")

    fig = px.bar(
        selected.sort_values("outflow_eur", ascending=False),
        x="customer_type",
        y="outflow_eur",
        title=f"Deposit Outflow by Segment - {scenario}",
        labels={
            "customer_type": "Customer Segment",
            "outflow_eur": "Outflow (EUR)",
        },
    )

    st.plotly_chart(fig, width="stretch")

    detail = selected[
        [
            "customer_type",
            "deposit_balance",
            "runoff_rate",
            "outflow_eur",
            "outflow_contribution",
            "stress_amplification",
        ]
    ].copy()

    detail = detail.rename(
        columns={
            "customer_type": "Customer Segment",
            "deposit_balance": "Deposits (EUR)",
            "runoff_rate": "Runoff Rate",
            "outflow_eur": "Outflow (EUR)",
            "outflow_contribution": "Outflow Contribution",
            "stress_amplification": "Stress Amplification",
        }
    )

    # Convert decimal fractions to percentage points for display only.
    detail["Runoff Rate"] = detail["Runoff Rate"] * 100
    detail["Outflow Contribution"] = (
        detail["Outflow Contribution"] * 100
    )

    st.dataframe(
        detail,
        width="stretch",
        hide_index=True,
        column_config={
            "Runoff Rate": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Outflow Contribution": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Stress Amplification": st.column_config.NumberColumn(
                format="%.2fx"
            ),
        },
    )

    st.info(
        "These figures represent gross simulated deposit outflows, "
        "not a liquidity shortfall. Liquid assets, other cash flows "
        "and regulatory LCR/NSFR requirements are not modelled."
    )
