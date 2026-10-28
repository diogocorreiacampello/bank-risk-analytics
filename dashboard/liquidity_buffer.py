"""Illustrative liquidity buffer and survival horizon analytics."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


ASSET_ASSUMPTIONS = (
    ("Cash", 100_000_000.0, 0.00),
    ("Central Bank Reserves", 150_000_000.0, 0.00),
    ("Sovereign Bonds", 200_000_000.0, 0.05),
)

RUNOFF_RATES = {
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


def calculate_liquidity_buffer():
    """Calculate haircut-adjusted liquid assets."""
    assets = pd.DataFrame(
        ASSET_ASSUMPTIONS,
        columns=["asset", "gross_value", "haircut"],
    )

    assets["available_value"] = (
        assets["gross_value"] * (1 - assets["haircut"])
    )

    return assets, float(assets["available_value"].sum())


def calculate_survival_horizon(segments):
    """Calculate illustrative 30-day deposit outflows and buffer paths."""
    required = {"customer_type", "total_balance"}

    if not required.issubset(segments.columns):
        raise ValueError("Missing deposit segment columns.")

    if segments["customer_type"].duplicated().any():
        raise ValueError("Duplicate customer segments.")

    balances = dict(
        zip(
            segments["customer_type"],
            segments["total_balance"],
        )
    )

    expected_segments = {"Retail", "SME", "Corporate"}

    if set(balances) != expected_segments:
        raise ValueError("Unexpected deposit segments.")

    if any(
        not np.isfinite(value) or value < 0
        for value in balances.values()
    ):
        raise ValueError("Invalid deposit balances.")

    assets, buffer = calculate_liquidity_buffer()

    weights = np.array(
        [0.40 / 7] * 7
        + [0.35 / 7] * 7
        + [0.25 / 16] * 16,
        dtype=float,
    )

    assert len(weights) == 30
    assert np.isclose(weights.sum(), 1.0)

    summary_rows = []
    profiles = {}

    for scenario, rates in RUNOFF_RATES.items():
        outflow = sum(
            balances[segment] * rates[segment]
            for segment in expected_segments
        )

        daily_outflow = outflow * weights
        cumulative = np.cumsum(daily_outflow)
        remaining = buffer - cumulative

        breach_indices = np.flatnonzero(remaining < -1e-6)

        breach_day = (
            int(breach_indices[0] + 1)
            if len(breach_indices)
            else None
        )

        profiles[scenario] = pd.DataFrame({
            "day": np.arange(1, 31),
            "daily_outflow": daily_outflow,
            "cumulative_outflow": cumulative,
            "remaining_buffer": remaining,
        })

        summary_rows.append({
            "scenario": scenario,
            "deposit_outflow": float(outflow),
            "available_buffer": buffer,
            "coverage_gap": float(buffer - outflow),
            "coverage_ratio": (
                float(buffer / outflow)
                if outflow > 0
                else np.nan
            ),
            "first_breach_day": breach_day,
        })

    return assets, pd.DataFrame(summary_rows), profiles


def render_liquidity_buffer(segments):
    """Render the illustrative liquidity buffer dashboard section."""
    st.subheader("Liquidity Buffer & Survival Horizon")

    st.caption(
        "Illustrative 30-day deposit runoff simulation. "
        "Liquid assets and daily runoff timing are assumed, "
        "not observed or regulatory-calibrated."
    )

    assets, summary, profiles = calculate_survival_horizon(segments)

    scenario = st.selectbox(
        "Buffer Stress Scenario",
        list(RUNOFF_RATES),
        index=1,
        key="liquidity_buffer_scenario",
    )

    selected = summary.loc[
        summary["scenario"] == scenario
    ].iloc[0]

    buffer = float(selected["available_buffer"])
    outflow = float(selected["deposit_outflow"])
    gap = float(selected["coverage_gap"])
    breach = selected["first_breach_day"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Available Buffer", f"€{buffer / 1e6:,.2f}M")
    col2.metric("30-Day Outflow", f"€{outflow / 1e6:,.2f}M")
    col3.metric("Coverage Gap", f"€{gap / 1e6:,.2f}M")

    horizon_label = (
        "No breach ≤30d"
        if pd.isna(breach)
        else f"Day {int(breach)}"
    )

    col4.metric("First Buffer Breach", horizon_label)

    profile = profiles[scenario]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[0] + profile["day"].tolist(),
        y=[buffer] + profile["remaining_buffer"].tolist(),
        mode="lines",
        name="Remaining Buffer",
    ))

    fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="Buffer exhausted",
    )

    fig.update_layout(
        title=f"Remaining Liquidity Buffer - {scenario}",
        xaxis_title="Day",
        yaxis_title="Available Buffer (EUR)",
    )

    st.plotly_chart(fig, use_container_width=True)

    comparison = go.Figure()

    comparison.add_trace(go.Bar(
        x=summary["scenario"],
        y=summary["deposit_outflow"],
        name="30-Day Deposit Outflow",
    ))

    comparison.add_hline(
        y=buffer,
        line_dash="dash",
        annotation_text="Available Liquidity Buffer",
    )

    comparison.update_layout(
        title="30-Day Outflows vs Available Liquidity Buffer",
        xaxis_title="Scenario",
        yaxis_title="EUR",
    )

    st.plotly_chart(comparison, use_container_width=True)

    st.markdown("**Simulated Liquid Asset Portfolio**")

    display_assets = assets.copy()

    display_assets["gross_value"] = display_assets[
        "gross_value"
    ].map(lambda value: f"€{value:,.2f}")

    display_assets["haircut"] = display_assets[
        "haircut"
    ].map(lambda value: f"{value:.1%}")

    display_assets["available_value"] = display_assets[
        "available_value"
    ].map(lambda value: f"€{value:,.2f}")

    st.dataframe(
        display_assets,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("**Daily Liquidity Profile**")

    daily_display = profile.copy()

    for column in [
        "daily_outflow",
        "cumulative_outflow",
        "remaining_buffer",
    ]:
        daily_display[column] = daily_display[column].map(
            lambda value: f"€{value:,.2f}"
        )

    st.dataframe(
        daily_display,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "This model assumes a static liquidity buffer and "
        "gross deposit outflows only. It excludes asset "
        "replenishment, additional funding, other cash flows, "
        "intraday liquidity, and regulatory LCR/NSFR requirements. "
        "A negative buffer represents a simulated funding gap, "
        "not a prediction of bank failure."
    )
