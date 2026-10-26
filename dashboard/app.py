
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Atlas Bank | Market Risk",
    page_icon="📊",
    layout="wide"
)

DATA_DIR = (
    Path(__file__).resolve().parent.parent / "data" / "demo" / "portfolio"
)

@st.cache_data
def load_data():
    pnl = pd.read_csv(
        DATA_DIR / "portfolio_historical_pnl.csv",
        index_col=0,
        parse_dates=True
    ).sort_index()

    risk = pd.read_csv(
        DATA_DIR / "portfolio_risk_metrics.csv"
    )

    stress = pd.read_csv(
        DATA_DIR / "stress_by_asset_group.csv"
    )

    return pnl, risk, stress


pnl, risk, stress = load_data()

var95 = float(risk.loc[0, "VaR 95%"])
var99 = float(risk.loc[0, "VaR 99%"])
es99 = float(risk.loc[0, "ES 99%"])
worst_pnl = float(risk.loc[0, "Worst P&L"])

def eur_millions(value):
    return f"€{value / 1_000_000:,.2f}M"


st.title("Atlas Bank")
st.subheader("Market Risk Analytics Dashboard")
st.caption(
    "Historical Value at Risk | Expected Shortfall | Stress Testing"
)

st.divider()






# ATLAS BANK - SELECTIVE NAVIGATION TEST

st.sidebar.title("ATLAS BANK")
st.sidebar.caption("Financial Risk Analytics Platform")

selected_page = st.sidebar.radio(
    "Analytics Area",
    [
        "Portfolio Overview",
        "Market Risk Analytics",
        "Stress Testing & Interest Rates",
        "Sovereign Risk Analytics",
        "Portfolio Optimization",
        "Credit Risk Analytics",
        "Liquidity Risk Analytics"
    ],
    key="atlas_selected_page"
)

st.sidebar.divider()
st.sidebar.caption("Atlas Bank | Research Environment")

st.title(selected_page)


if selected_page == 'Portfolio Overview':
    st.header("Portfolio Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Portfolio Exposure", "€1.20B")
    c2.metric("Historical Scenarios", f"{len(pnl):,}")
    c3.metric("Worst Historical P&L", eur_millions(worst_pnl))

    st.divider()



if selected_page == 'Portfolio Overview':
    st.header("Risk Metrics")

    c1, c2, c3 = st.columns(3)
    c1.metric("1-Day VaR 95%", eur_millions(var95))
    c2.metric("1-Day VaR 99%", eur_millions(var99))
    c3.metric("1-Day Expected Shortfall 99%", eur_millions(es99))

    st.caption(
        "Historical simulation based on 379 aligned daily scenarios. "
        "Risk metrics are estimates, not guaranteed maximum losses."
    )

    st.divider()



if selected_page == 'Portfolio Overview':
    st.header("Historical Portfolio P&L")

    pnl_chart = pnl[["total_pnl"]].reset_index()
    pnl_chart.columns = ["Date", "P&L"]

    fig_line = px.line(
        pnl_chart,
        x="Date",
        y="P&L",
        title="Daily Portfolio P&L"
    )

    fig_line.update_layout(
        xaxis_title="Date",
        yaxis_title="P&L (€)"
    )

    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Distribution of Daily P&L")

    fig_hist = px.histogram(
        pnl,
        x="total_pnl",
        nbins=50,
        title="Historical P&L Distribution"
    )

    fig_hist.add_vline(
        x=-var95,
        line_dash="dash",
        line_color="orange",
        annotation_text="VaR 95%"
    )

    fig_hist.add_vline(
        x=-var99,
        line_dash="dash",
        line_color="red",
        annotation_text="VaR 99%"
    )

    fig_hist.update_layout(
        xaxis_title="Daily P&L (€)",
        yaxis_title="Number of Scenarios"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()



if selected_page == 'Stress Testing & Interest Rates':
    st.header("Stress Testing")

    # Handle CSV exports with different index-column conventions.
    if "asset_group" not in stress.columns:
        possible_columns = [
            col for col in stress.columns
            if col.startswith("Unnamed:")
        ]
        if possible_columns:
            stress = stress.rename(
                columns={possible_columns[0]: "asset_group"}
            )

    if "asset_group" in stress.columns and "stress_pnl" in stress.columns:
        stress_chart = stress.copy()
        stress_chart["stress_pnl_millions"] = (
            pd.to_numeric(stress_chart["stress_pnl"]) / 1_000_000
        )

        fig_stress = px.bar(
            stress_chart.sort_values("stress_pnl_millions"),
            x="stress_pnl_millions",
            y="asset_group",
            orientation="h",
            title="Stress Loss by Asset Group",
            labels={
                "stress_pnl_millions": "Stress P&L (€ millions)",
                "asset_group": "Asset Group"
            }
        )

        st.plotly_chart(fig_stress, use_container_width=True)
    else:
        st.warning("Stress CSV columns need to be checked.")
        st.write(stress.columns.tolist())

    with st.expander("View underlying stress data"):
        st.dataframe(stress, use_container_width=True)

    st.divider()
    st.caption("Atlas Bank | Financial Risk Analytics Project")


    # ============================================================
    # INSTRUMENT RISK EXPLORER
    # ============================================================

    st.divider()


if selected_page == 'Market Risk Analytics':
    st.header("Instrument Risk Explorer")

    st.write(
        "Explore portfolio exposures and stress losses "
        "at individual instrument level."
    )

    instrument_data = pd.read_csv(
        DATA_DIR / "stress_by_instrument.csv"
    )

    asset_classes = sorted(
        instrument_data["asset_group"].unique().tolist()
    )

    selected_classes = st.multiselect(
        "Select asset classes",
        options=asset_classes,
        default=asset_classes
    )

    filtered_instruments = instrument_data[
        instrument_data["asset_group"].isin(selected_classes)
    ].copy()

    filtered_instruments = filtered_instruments.sort_values(
        "stress_pnl_eur",
        ascending=True
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Selected Instruments",
        len(filtered_instruments)
    )

    col2.metric(
        "Selected Exposure",
        f"€{filtered_instruments['market_value'].sum()/1e6:,.2f}M"
    )

    col3.metric(
        "Stress P&L",
        f"€{filtered_instruments['stress_pnl_eur'].sum()/1e6:,.2f}M"
    )

    st.subheader("Instrument-Level Stress Results")

    st.dataframe(
        filtered_instruments,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Stress Loss by Instrument")

    fig_instruments = px.bar(
        filtered_instruments,
        x="stress_pnl_eur",
        y="instrument_name",
        orientation="h",
        color="asset_group",
        labels={
            "stress_pnl_eur": "Stress P&L (€)",
            "instrument_name": "Instrument",
            "asset_group": "Asset Group"
        },
        title="Stress P&L by Instrument"
    )

    fig_instruments.update_layout(
        height=850,
        yaxis={"categoryorder": "total descending"}
    )

    st.plotly_chart(
        fig_instruments,
        use_container_width=True
    )


    # ============================================================
    # RISK CONCENTRATION ANALYSIS
    # ============================================================

    st.divider()


if selected_page == 'Market Risk Analytics':
    st.header("Risk Concentration Analysis")

    st.write(
        "Identify the instruments contributing most "
        "to portfolio losses under the stress scenario."
    )

    concentration_data = pd.read_csv(
        DATA_DIR / "stress_by_instrument.csv"
    )

    # Consider only instruments with losses
    loss_data = concentration_data[
        concentration_data["stress_pnl_eur"] < 0
    ].copy()

    total_losses = -loss_data["stress_pnl_eur"].sum()

    loss_data["loss_contribution_pct"] = (
        -loss_data["stress_pnl_eur"] / total_losses * 100
    )

    loss_data = loss_data.sort_values(
        "loss_contribution_pct",
        ascending=False
    )

    top_10 = loss_data.head(10)

    st.subheader("Top 10 Loss Contributors")

    fig_concentration = px.bar(
        top_10,
        x="loss_contribution_pct",
        y="instrument_name",
        orientation="h",
        color="asset_group",
        labels={
            "loss_contribution_pct": "Contribution to Gross Losses (%)",
            "instrument_name": "Instrument",
            "asset_group": "Asset Group"
        },
        title="Top 10 Instruments by Stress Loss Contribution"
    )

    fig_concentration.update_layout(
        height=600,
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        fig_concentration,
        use_container_width=True
    )

    top_5_concentration = (
        loss_data.head(5)["loss_contribution_pct"].sum()
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Top 5 Loss Concentration",
        f"{top_5_concentration:.2f}%"
    )

    col2.metric(
        "Largest Loss Contributor",
        loss_data.iloc[0]["instrument_name"]
    )

    with st.expander("View risk concentration data"):
        st.dataframe(
            loss_data[
                [
                    "instrument_name",
                    "asset_group",
                    "market_value",
                    "stress_pnl_eur",
                    "loss_contribution_pct"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


    # ============================================================
    # INTERACTIVE STRESS TESTING
    # ============================================================

    st.divider()


if selected_page == 'Stress Testing & Interest Rates':
    st.header("Interactive Stress Testing")

    st.write(
        "Adjust market shocks and analyse their impact "
        "on the equity portfolio."
    )

    equity_shock = st.slider(
        "Equity Market Shock (%)",
        min_value=-50,
        max_value=20,
        value=-20,
        step=5
    )

    usd_shock = st.slider(
        "USD vs EUR Shock (%)",
        min_value=-30,
        max_value=20,
        value=-10,
        step=5
    )

    interactive_data = pd.read_csv(
        DATA_DIR / "stress_by_instrument.csv"
    )

    interactive_equities = interactive_data[
        interactive_data["asset_group"] == "Equities"
    ].copy()

    interactive_equities["market_return"] = equity_shock / 100

    interactive_equities["fx_return"] = (
        interactive_equities["currency"]
        .apply(lambda x: usd_shock / 100 if x == "USD" else 0)
    )

    interactive_equities["total_return"] = (
        (1 + interactive_equities["market_return"])
        * (1 + interactive_equities["fx_return"])
        - 1
    )

    interactive_equities["interactive_pnl"] = (
        interactive_equities["market_value"]
        * interactive_equities["total_return"]
    )

    total_interactive_pnl = interactive_equities[
        "interactive_pnl"
    ].sum()

    equity_exposure = interactive_equities[
        "market_value"
    ].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Equity Exposure",
        f"€{equity_exposure / 1e6:,.2f}M"
    )

    col2.metric(
        "Interactive Stress P&L",
        f"€{total_interactive_pnl / 1e6:,.2f}M"
    )

    col3.metric(
        "Portfolio Impact",
        f"{total_interactive_pnl / 1.2e9:.2%}"
    )

    fig_interactive = px.bar(
        interactive_equities.sort_values("interactive_pnl"),
        x="interactive_pnl",
        y="instrument_name",
        orientation="h",
        title="Equity Stress P&L by Instrument",
        labels={
            "interactive_pnl": "Stress P&L (€)",
            "instrument_name": "Instrument"
        }
    )

    st.plotly_chart(
        fig_interactive,
        use_container_width=True
    )

    with st.expander("View interactive stress calculations"):
        st.dataframe(
            interactive_equities[
                [
                    "instrument_name",
                    "currency",
                    "market_value",
                    "market_return",
                    "fx_return",
                    "total_return",
                    "interactive_pnl"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


    # ATLAS BANK - INTERACTIVE FIXED INCOME STRESS

    st.divider()


if selected_page == 'Stress Testing & Interest Rates':
    st.header("Interactive Fixed Income Stress Simulator")

    st.write(
        "Adjust interest rate and sovereign spread shocks "
        "to evaluate the impact on the fixed income portfolio."
    )

    bond_data = pd.read_csv(
        DATA_DIR / "bond_risk_parameters.csv"
    )

    col1, col2 = st.columns(2)

    with col1:
        rate_shock = st.slider(
            "Interest Rate Shock (bps)",
            min_value=-200,
            max_value=300,
            value=100,
            step=25
        )

        france_spread = st.slider(
            "French Sovereign Spread Shock (bps)",
            min_value=0,
            max_value=300,
            value=75,
            step=25
        )

    with col2:
        italy_spread = st.slider(
            "Italian Sovereign Spread Shock (bps)",
            min_value=0,
            max_value=400,
            value=150,
            step=25
        )

        portugal_spread = st.slider(
            "Portuguese Sovereign Spread Shock (bps)",
            min_value=0,
            max_value=400,
            value=125,
            step=25
        )

    spread_shocks = {
        11: france_spread,
        12: italy_spread,
        13: portugal_spread
    }

    bond_data["spread_shock_bps"] = (
        bond_data["instrument_id"]
        .map(spread_shocks)
        .fillna(0)
    )

    bond_data["total_shock_bps"] = (
        rate_shock + bond_data["spread_shock_bps"]
    )

    bond_data["delta_yield"] = (
        bond_data["total_shock_bps"] / 10000
    )

    bond_data["stress_return"] = (
        -bond_data["modified_duration"] * bond_data["delta_yield"]
        + 0.5 * bond_data["convexity"] * bond_data["delta_yield"] ** 2
    )

    bond_data["stress_pnl"] = (
        bond_data["market_value"] * bond_data["stress_return"]
    )

    total_bond_pnl = bond_data["stress_pnl"].sum()

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Fixed Income Exposure",
        f"€{bond_data['market_value'].sum() / 1e6:,.2f}M"
    )

    metric2.metric(
        "Stress P&L",
        f"€{total_bond_pnl / 1e6:,.2f}M"
    )

    metric3.metric(
        "Portfolio Impact",
        f"{total_bond_pnl / 1_200_000_000:.2%}"
    )

    st.subheader("Stress P&L by Asset Group")

    bond_group_stress = (
        bond_data.groupby("asset_group", as_index=False)["stress_pnl"]
        .sum()
    )

    fig_bond = px.bar(
        bond_group_stress,
        x="stress_pnl",
        y="asset_group",
        orientation="h",
        title="Fixed Income Stress by Asset Group",
        labels={
            "stress_pnl": "Stress P&L (€)",
            "asset_group": "Asset Group"
        }
    )

    st.plotly_chart(fig_bond, use_container_width=True)

    with st.expander("View instrument-level stress results"):
        st.dataframe(
            bond_data[
                [
                    "instrument_name",
                    "asset_group",
                    "market_value",
                    "modified_duration",
                    "convexity",
                    "total_shock_bps",
                    "stress_pnl"
                ]
            ],
            use_container_width=True
        )

    st.caption(
        "Scenario analysis based on modified duration and convexity. "
        "Interest rate shocks are applied uniformly across the fixed "
        "income portfolio, with additional sovereign spread shocks. "
        "Currency effects are excluded."
    )


    # ATLAS BANK - INTEREST RATE SENSITIVITY ANALYSIS

    st.divider()


if selected_page == 'Stress Testing & Interest Rates':
    st.header("Interest Rate Sensitivity Analysis")

    st.write(
        "Analyse the impact of parallel interest rate shifts "
        "on the fixed income portfolio using modified duration "
        "and convexity."
    )

    sensitivity_bonds = pd.read_csv(
        DATA_DIR / "bond_risk_parameters.csv"
    )

    import numpy as np

    rate_scenarios = np.arange(-200, 201, 25)

    sensitivity_results = []

    for shock_bps in rate_scenarios:

        delta_y = shock_bps / 10000

        linear_pnl = (
            -sensitivity_bonds["market_value"]
            * sensitivity_bonds["modified_duration"]
            * delta_y
        ).sum()

        convexity_pnl = (
            sensitivity_bonds["market_value"]
            * (
                -sensitivity_bonds["modified_duration"] * delta_y
                + 0.5 * sensitivity_bonds["convexity"] * delta_y**2
            )
        ).sum()

        sensitivity_results.append({
            "Rate Shock (bps)": shock_bps,
            "Duration Only (€)": linear_pnl,
            "Duration + Convexity (€)": convexity_pnl
        })

    sensitivity_df = pd.DataFrame(sensitivity_results)

    # Display results in millions
    sensitivity_chart = sensitivity_df.copy()

    sensitivity_chart["Duration Only (€M)"] = (
        sensitivity_chart["Duration Only (€)"] / 1e6
    )

    sensitivity_chart["Duration + Convexity (€M)"] = (
        sensitivity_chart["Duration + Convexity (€)"] / 1e6
    )

    fig_sensitivity = px.line(
        sensitivity_chart,
        x="Rate Shock (bps)",
        y=[
            "Duration Only (€M)",
            "Duration + Convexity (€M)"
        ],
        markers=True,
        title="Portfolio P&L Sensitivity to Interest Rate Shocks",
        labels={
            "value": "Estimated P&L (€ millions)",
            "variable": "Valuation Method"
        }
    )

    fig_sensitivity.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    fig_sensitivity.update_layout(
        hovermode="x unified",
        legend_title_text="Valuation Method"
    )

    st.plotly_chart(
        fig_sensitivity,
        use_container_width=True
    )

    st.subheader("Sensitivity Results")

    display_sensitivity = sensitivity_df[
        sensitivity_df["Rate Shock (bps)"].isin(
            [-200, -100, -50, 0, 50, 100, 200]
        )
    ].copy()

    st.dataframe(
        display_sensitivity.style.format({
            "Duration Only (€)": "€{:,.2f}",
            "Duration + Convexity (€)": "€{:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Parallel yield curve shifts applied to all 14 fixed "
        "income instruments. Sovereign spread shocks and FX "
        "effects are excluded. Results are second-order "
        "approximations rather than full bond repricing."
    )


    # ATLAS BANK - DV01 RISK CONTRIBUTION

    st.divider()


if selected_page == 'Stress Testing & Interest Rates':
    st.header("Interest Rate Risk Contribution")

    st.write(
        "Identify which fixed income asset groups contribute "
        "most to the portfolio's interest rate sensitivity."
    )

    dv01_data = pd.read_csv(
        DATA_DIR / "bond_risk_parameters.csv"
    )

    dv01_by_group = (
        dv01_data
        .groupby("asset_group", as_index=False)
        .agg(
            exposure_eur=("market_value", "sum"),
            dv01_eur=("dv01", "sum")
        )
    )

    total_dv01 = dv01_by_group["dv01_eur"].sum()

    dv01_by_group["risk_contribution_pct"] = (
        dv01_by_group["dv01_eur"] / total_dv01 * 100
    )

    dv01_by_group["exposure_pct"] = (
        dv01_by_group["exposure_eur"]
        / dv01_by_group["exposure_eur"].sum()
        * 100
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Fixed Income DV01",
            f"€{total_dv01:,.2f}"
        )

    with col2:
        largest_group = dv01_by_group.loc[
            dv01_by_group["dv01_eur"].idxmax(),
            "asset_group"
        ]

        st.metric(
            "Largest Interest Rate Risk Contributor",
            largest_group
        )

    fig_dv01 = px.bar(
        dv01_by_group.sort_values(
            "risk_contribution_pct",
            ascending=True
        ),
        x="risk_contribution_pct",
        y="asset_group",
        orientation="h",
        text="risk_contribution_pct",
        title="DV01 Contribution by Asset Group",
        labels={
            "risk_contribution_pct": "Contribution to Total DV01 (%)",
            "asset_group": "Asset Group"
        }
    )

    fig_dv01.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    st.plotly_chart(
        fig_dv01,
        use_container_width=True
    )

    st.subheader("Exposure vs Risk Contribution")

    fig_comparison = px.bar(
        dv01_by_group,
        x="asset_group",
        y=["exposure_pct", "risk_contribution_pct"],
        barmode="group",
        title="Portfolio Exposure vs Interest Rate Risk",
        labels={
            "value": "Percentage (%)",
            "asset_group": "Asset Group",
            "variable": "Metric"
        }
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )

    st.dataframe(
        dv01_by_group.style.format({
            "exposure_eur": "€{:,.0f}",
            "dv01_eur": "€{:,.2f}",
            "risk_contribution_pct": "{:.2f}%",
            "exposure_pct": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "DV01 measures the approximate change in portfolio "
        "value for a parallel 1 basis point increase in yields. "
        "Contributions are based on absolute positive DV01 "
        "for the long-only fixed income portfolio."
    )


    # ATLAS BANK - YIELD CURVE SCENARIO SIMULATOR

    st.divider()


if selected_page == 'Stress Testing & Interest Rates':
    st.header("Yield Curve Scenario Simulator")

    st.write(
        "Apply different interest rate shocks across maturities "
        "to analyse non-parallel yield curve movements."
    )

    curve_data = pd.read_csv(
        DATA_DIR / "bond_risk_parameters.csv"
    )

    curve_data["maturity"] = curve_data["maturity"].astype(int)

    # Yield curve scenario presets
    curve_presets = {
        "Custom": None,
        "Parallel Shift": {1: 100, 2: 100, 5: 100, 10: 100},
        "Bear Flattening": {1: 150, 2: 125, 5: 75, 10: 25},
        "Bear Steepening": {1: 25, 2: 50, 5: 100, 10: 150},
        "Bull Steepening": {1: -150, 2: -100, 5: -50, 10: -25}
    }

    scenario = st.selectbox(
        "Select Yield Curve Scenario",
        list(curve_presets.keys()),
        key="curve_scenario"
    )

    # Update slider values only when scenario changes
    if "previous_curve_scenario" not in st.session_state:
        st.session_state.previous_curve_scenario = "Custom"

    if scenario != st.session_state.previous_curve_scenario:
        selected = curve_presets[scenario]

        if selected is not None:
            for maturity, shock in selected.items():
                st.session_state[f"curve_{maturity}y"] = shock

        st.session_state.previous_curve_scenario = scenario

    col1, col2 = st.columns(2)

    with col1:
        shock_1y = st.slider(
            "1-Year Rate Shock (bps)",
            min_value=-200, max_value=300, step=25,
            key="curve_1y"
        )

        shock_2y = st.slider(
            "2-Year Rate Shock (bps)",
            min_value=-200, max_value=300, step=25,
            key="curve_2y"
        )

    with col2:
        shock_5y = st.slider(
            "5-Year Rate Shock (bps)",
            min_value=-200, max_value=300, step=25,
            key="curve_5y"
        )

        shock_10y = st.slider(
            "10-Year Rate Shock (bps)",
            min_value=-200, max_value=300, step=25,
            key="curve_10y"
        )

    curve_shocks = {
        1: shock_1y,
        2: shock_2y,
        5: shock_5y,
        10: shock_10y
    }

    curve_data["shock_bps"] = (
        curve_data["maturity"].map(curve_shocks)
    )

    curve_data["delta_y"] = (
        curve_data["shock_bps"] / 10000
    )

    curve_data["stress_return"] = (
        -curve_data["modified_duration"] * curve_data["delta_y"]
        + 0.5 * curve_data["convexity"] * curve_data["delta_y"]**2
    )

    curve_data["stress_pnl"] = (
        curve_data["market_value"]
        * curve_data["stress_return"]
    )

    curve_total_pnl = curve_data["stress_pnl"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Fixed Income Exposure",
            f"€{curve_data['market_value'].sum()/1e6:,.2f}M"
        )

    with col2:
        st.metric(
            "Curve Stress P&L",
            f"€{curve_total_pnl/1e6:,.2f}M"
        )

    with col3:
        st.metric(
            "Portfolio Impact",
            f"{curve_total_pnl/1_200_000_000:.2%}"
        )

    curve_results = (
        curve_data.groupby("maturity", as_index=False)
        .agg(
            exposure_eur=("market_value", "sum"),
            stress_pnl=("stress_pnl", "sum")
        )
    )

    curve_results["stress_pnl_m"] = (
        curve_results["stress_pnl"] / 1e6
    )

    curve_results["maturity_label"] = (
        curve_results["maturity"].astype(str) + "Y"
    )

    fig_curve = px.bar(
        curve_results,
        x="maturity_label",
        y="stress_pnl_m",
        title="Stress P&L by Maturity",
        labels={
            "maturity_label": "Maturity",
            "stress_pnl_m": "Stress P&L (€ millions)"
        }
    )

    fig_curve.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    st.plotly_chart(
        fig_curve,
        use_container_width=True
    )

    st.subheader("Scenario Results")

    st.dataframe(
        curve_data[
            [
                "instrument_name",
                "maturity",
                "market_value",
                "shock_bps",
                "modified_duration",
                "stress_pnl"
            ]
        ].style.format({
            "market_value": "€{:,.0f}",
            "modified_duration": "{:.2f}",
            "stress_pnl": "€{:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Scenario shocks are assigned according to contractual "
        "maturity. Duration and convexity approximations are used. "
        "This is a maturity-bucket scenario analysis, not a "
        "cash-flow-based Key Rate Duration model. "
        "FX and credit spread effects are excluded."
    )



    # ATLAS BANK - SCENARIO COMPARISON

    st.divider()


if selected_page == 'Stress Testing & Interest Rates':
    st.header("Yield Curve Scenario Comparison")

    st.write(
        "Compare the impact of different yield curve scenarios "
        "on the fixed income portfolio."
    )

    comparison_presets = {
        "Parallel Shift (+100 bps)": {
            1: 100, 2: 100, 5: 100, 10: 100
        },
        "Bear Flattening": {
            1: 150, 2: 125, 5: 75, 10: 25
        },
        "Bear Steepening": {
            1: 25, 2: 50, 5: 100, 10: 150
        },
        "Bull Steepening": {
            1: -150, 2: -125, 5: -75, 10: -25
        }
    }

    comparison_data = pd.read_csv(
        DATA_DIR / "bond_risk_parameters.csv"
    )

    comparison_data["maturity"] = (
        comparison_data["maturity"].astype(int)
    )

    comparison_results = []

    for scenario_name, shocks in comparison_presets.items():

        scenario_data = comparison_data.copy()

        scenario_data["shock_bps"] = (
            scenario_data["maturity"].map(shocks)
        )

        scenario_data["delta_y"] = (
            scenario_data["shock_bps"] / 10000
        )

        scenario_data["stress_pnl"] = (
            scenario_data["market_value"]
            * (
                -scenario_data["modified_duration"]
                * scenario_data["delta_y"]
                + 0.5
                * scenario_data["convexity"]
                * scenario_data["delta_y"]**2
            )
        )

        total_pnl = scenario_data["stress_pnl"].sum()

        comparison_results.append({
            "Scenario": scenario_name,
            "Stress P&L (€M)": total_pnl / 1e6,
            "Portfolio Impact (%)": total_pnl / 1_200_000_000 * 100
        })

    comparison_df = pd.DataFrame(comparison_results)

    fig_comparison = px.bar(
        comparison_df,
        x="Scenario",
        y="Stress P&L (€M)",
        color="Stress P&L (€M)",
        color_continuous_scale="RdYlGn",
        title="Portfolio Stress P&L by Yield Curve Scenario"
    )

    fig_comparison.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    fig_comparison.update_layout(
        coloraxis_showscale=False
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True
    )

    st.subheader("Scenario Comparison Results")

    st.dataframe(
        comparison_df.style.format({
            "Stress P&L (€M)": "€{:,.2f}M",
            "Portfolio Impact (%)": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Scenarios use contractual maturity buckets and "
        "duration-convexity approximations. "
        "FX and credit spread effects are excluded."
    )



    # ATLAS BANK - INSTRUMENT LEVEL SCENARIO RISK

    st.divider()


if selected_page == 'Stress Testing & Interest Rates':
    st.header("Instrument-Level Scenario Risk Contribution")

    st.write(
        "Identify which fixed income instruments are most "
        "vulnerable under different yield curve scenarios."
    )

    selected_risk_scenario = st.selectbox(
        "Select Scenario for Instrument Analysis",
        list(comparison_presets.keys()),
        index=2,
        key="instrument_risk_scenario"
    )

    selected_shocks = comparison_presets[selected_risk_scenario]

    instrument_risk = comparison_data.copy()

    instrument_risk["shock_bps"] = (
        instrument_risk["maturity"].map(selected_shocks)
    )

    instrument_risk["delta_y"] = (
        instrument_risk["shock_bps"] / 10000
    )

    instrument_risk["stress_pnl"] = (
        instrument_risk["market_value"]
        * (
            -instrument_risk["modified_duration"]
            * instrument_risk["delta_y"]
            + 0.5
            * instrument_risk["convexity"]
            * instrument_risk["delta_y"]**2
        )
    )

    total_scenario_pnl = instrument_risk["stress_pnl"].sum()

    total_losses = -instrument_risk.loc[
        instrument_risk["stress_pnl"] < 0,
        "stress_pnl"
    ].sum()

    instrument_risk["loss_contribution_pct"] = 0.0

    if total_losses > 0:
        instrument_risk["loss_contribution_pct"] = (
            -instrument_risk["stress_pnl"].clip(upper=0)
            / total_losses * 100
        )

    instrument_risk["stress_pnl_m"] = (
        instrument_risk["stress_pnl"] / 1e6
    )

    instrument_risk = instrument_risk.sort_values(
        "stress_pnl"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Selected Scenario P&L",
            f"€{total_scenario_pnl/1e6:,.2f}M"
        )

    with col2:
        st.metric(
            "Largest Loss Contributor",
            (
                instrument_risk.iloc[0]["instrument_name"]
                if total_losses > 0
                else "No losses"
            )
        )

    fig_instrument_risk = px.bar(
        instrument_risk,
        x="stress_pnl_m",
        y="instrument_name",
        orientation="h",
        color="stress_pnl_m",
        color_continuous_scale="RdYlGn",
        title="Stress P&L by Instrument (€M)"
    )

    fig_instrument_risk.update_layout(
        yaxis={"categoryorder": "total descending"},
        coloraxis_showscale=False,
        xaxis_title="Stress P&L (€ millions)",
        yaxis_title="Instrument"
    )

    fig_instrument_risk.add_vline(
        x=0,
        line_dash="dash",
        line_color="gray"
    )

    st.plotly_chart(
        fig_instrument_risk,
        use_container_width=True
    )

    st.subheader("Instrument Risk Breakdown")

    st.dataframe(
        instrument_risk[
            [
                "instrument_name",
                "asset_group",
                "market_value",
                "maturity",
                "shock_bps",
                "stress_pnl",
                "loss_contribution_pct"
            ]
        ].style.format({
            "market_value": "€{:,.0f}",
            "stress_pnl": "€{:,.2f}",
            "loss_contribution_pct": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Loss contribution is measured relative to total "
        "gross losses across instruments. Instruments with "
        "positive P&L have zero loss contribution. "
        "Duration-convexity approximation; FX and credit "
        "spread effects excluded."
    )



    # ATLAS BANK - RISK CONCENTRATION DASHBOARD

    st.divider()



# ATLAS BANK - SHARED RISK DEPENDENCY FIX V1

import json

if selected_page == "Market Risk Analytics":

    comparison_presets = {
            "Parallel Shift (+100 bps)": {
                1: 100, 2: 100, 5: 100, 10: 100
            },
            "Bear Flattening": {
                1: 150, 2: 125, 5: 75, 10: 25
            },
            "Bear Steepening": {
                1: 25, 2: 50, 5: 100, 10: 150
            },
            "Bull Steepening": {
                1: -150, 2: -125, 5: -75, 10: -25
            }
        }

    comparison_data = pd.read_csv(
        DATA_DIR / "bond_risk_parameters.csv"
    )

    comparison_data["maturity"] = (
        comparison_data["maturity"].astype(int)
    )

    st.write(
            "Identify which fixed income instruments are most "
            "vulnerable under different yield curve scenarios."
        )
    selected_risk_scenario = st.selectbox(
            "Select Scenario for Instrument Analysis",
            list(comparison_presets.keys()),
            index=2,
            key="instrument_risk_scenario"
        )
    selected_shocks = comparison_presets[selected_risk_scenario]
    instrument_risk = comparison_data.copy()
    instrument_risk["shock_bps"] = (
            instrument_risk["maturity"].map(selected_shocks)
        )
    instrument_risk["delta_y"] = (
            instrument_risk["shock_bps"] / 10000
        )
    instrument_risk["stress_pnl"] = (
            instrument_risk["market_value"]
            * (
                -instrument_risk["modified_duration"]
                * instrument_risk["delta_y"]
                + 0.5
                * instrument_risk["convexity"]
                * instrument_risk["delta_y"]**2
            )
        )
    total_scenario_pnl = instrument_risk["stress_pnl"].sum()
    total_losses = -instrument_risk.loc[
            instrument_risk["stress_pnl"] < 0,
            "stress_pnl"
        ].sum()
    instrument_risk["loss_contribution_pct"] = 0.0
    if total_losses > 0:
            instrument_risk["loss_contribution_pct"] = (
                -instrument_risk["stress_pnl"].clip(upper=0)
                / total_losses * 100
            )
    instrument_risk["stress_pnl_m"] = (
            instrument_risk["stress_pnl"] / 1e6
        )
    instrument_risk = instrument_risk.sort_values(
            "stress_pnl"
        )

if selected_page == 'Market Risk Analytics':
    st.header("Risk Concentration Dashboard")

    st.write(
        "Analyse the concentration of potential losses "
        "across instruments and asset groups under "
        "the selected yield curve scenario."
    )

    # Reuse the scenario selected in the previous section
    concentration_data = instrument_risk.copy()

    # Calculate gross losses
    concentration_data["gross_loss"] = (
        -concentration_data["stress_pnl"].clip(upper=0)
    )

    total_gross_loss = concentration_data["gross_loss"].sum()

    # Rank instruments by gross loss
    concentration_data = concentration_data.sort_values(
        "gross_loss",
        ascending=False
    )

    # Calculate concentration metrics
    if total_gross_loss > 0:
        top_3_concentration = (
            concentration_data["gross_loss"].head(3).sum()
            / total_gross_loss * 100
        )

        top_5_concentration = (
            concentration_data["gross_loss"].head(5).sum()
            / total_gross_loss * 100
        )
    else:
        top_3_concentration = 0.0
        top_5_concentration = 0.0

    st.subheader("Portfolio Loss Concentration")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Top 3 Loss Concentration",
            f"{top_3_concentration:.2f}%"
        )

    with col2:
        st.metric(
            "Top 5 Loss Concentration",
            f"{top_5_concentration:.2f}%"
        )

    with col3:
        st.metric(
            "Total Gross Losses",
            f"€{total_gross_loss/1e6:,.2f}M"
        )

    # ==========================================
    # ASSET GROUP ANALYSIS
    # ==========================================

    group_concentration = (
        concentration_data
        .groupby("asset_group", as_index=False)
        .agg(
            exposure_eur=("market_value", "sum"),
            gross_loss_eur=("gross_loss", "sum"),
            net_stress_pnl_eur=("stress_pnl", "sum")
        )
    )

    total_exposure = group_concentration["exposure_eur"].sum()

    group_concentration["exposure_pct"] = (
        group_concentration["exposure_eur"]
        / total_exposure * 100
    )

    if total_gross_loss > 0:
        group_concentration["loss_contribution_pct"] = (
            group_concentration["gross_loss_eur"]
            / total_gross_loss * 100
        )
    else:
        group_concentration["loss_contribution_pct"] = 0.0

    st.subheader("Loss Concentration by Asset Group")

    fig_group_concentration = px.bar(
        group_concentration.sort_values(
            "loss_contribution_pct",
            ascending=True
        ),
        x="loss_contribution_pct",
        y="asset_group",
        orientation="h",
        text="loss_contribution_pct",
        title="Contribution to Total Gross Losses (%)"
    )

    fig_group_concentration.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_group_concentration.update_layout(
        xaxis_title="Share of Gross Losses (%)",
        yaxis_title="Asset Group"
    )

    st.plotly_chart(
        fig_group_concentration,
        use_container_width=True
    )

    # ==========================================
    # EXPOSURE VS LOSS CONTRIBUTION
    # ==========================================

    st.subheader("Exposure vs Loss Contribution")

    comparison_long = group_concentration.melt(
        id_vars="asset_group",
        value_vars=[
            "exposure_pct",
            "loss_contribution_pct"
        ],
        var_name="Metric",
        value_name="Percentage"
    )

    comparison_long["Metric"] = (
        comparison_long["Metric"].replace({
            "exposure_pct": "Portfolio Exposure",
            "loss_contribution_pct": "Gross Loss Contribution"
        })
    )

    fig_exposure_loss = px.bar(
        comparison_long,
        x="asset_group",
        y="Percentage",
        color="Metric",
        barmode="group",
        title="Exposure Share vs Gross Loss Share"
    )

    fig_exposure_loss.update_layout(
        xaxis_title="Asset Group",
        yaxis_title="Percentage (%)"
    )

    st.plotly_chart(
        fig_exposure_loss,
        use_container_width=True
    )

    # ==========================================
    # CONCENTRATION ALERTS
    # ==========================================

    st.subheader("Risk Concentration Alerts")

    # Illustrative monitoring thresholds
    top_3_limit = 50.0
    top_5_limit = 75.0

    if total_gross_loss == 0:
        st.info(
            "No stressed losses under this scenario. "
            "Loss concentration metrics are not applicable."
        )
    else:
        if top_3_concentration > top_3_limit:
            st.warning(
                f"Top 3 concentration exceeds "
                f"the illustrative {top_3_limit:.0f}% threshold."
            )
        else:
            st.success(
                "Top 3 concentration is within "
                "the illustrative monitoring threshold."
            )

        if top_5_concentration > top_5_limit:
            st.warning(
                f"Top 5 concentration exceeds "
                f"the illustrative {top_5_limit:.0f}% threshold."
            )
        else:
            st.success(
                "Top 5 concentration is within "
                "the illustrative monitoring threshold."
            )

    # ==========================================
    # RESULTS TABLE
    # ==========================================

    st.subheader("Asset Group Concentration Results")

    st.dataframe(
        group_concentration[
            [
                "asset_group",
                "exposure_eur",
                "gross_loss_eur",
                "net_stress_pnl_eur",
                "exposure_pct",
                "loss_contribution_pct"
            ]
        ].style.format({
            "exposure_eur": "€{:,.0f}",
            "gross_loss_eur": "€{:,.2f}",
            "net_stress_pnl_eur": "€{:,.2f}",
            "exposure_pct": "{:.2f}%",
            "loss_contribution_pct": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Loss concentration is calculated using gross "
        "negative stressed P&L, before offsetting gains. "
        "Monitoring thresholds are illustrative, not "
        "regulatory or institution-approved limits. "
        "Results update with the selected scenario."
    )


    # ATLAS BANK - EXECUTIVE RISK OVERVIEW

    st.divider()


if selected_page == 'Portfolio Overview':
    st.header("Executive Risk Overview")

    st.write(
        "Consolidated portfolio exposure, market risk "
        "and historical performance indicators."
    )

    exec_risk = pd.read_csv(
        DATA_DIR / "portfolio_risk_metrics.csv"
    )

    exec_pnl = pd.read_csv(
        DATA_DIR / "portfolio_historical_pnl.csv",
        parse_dates=["date"]
    ).sort_values("date")

    exec_instruments = pd.read_csv(
        DATA_DIR / "stress_by_instrument.csv"
    )

    exec_bonds = pd.read_csv(
        DATA_DIR / "bond_risk_parameters.csv"
    )

    exec_groups = pd.read_csv(
        DATA_DIR / "stress_by_asset_group.csv"
    )

    exec_exposure = exec_instruments["market_value"].sum()
    exec_dv01 = exec_bonds["dv01"].sum()

    exec_var99 = float(exec_risk.iloc[0]["VaR 99%"])
    exec_es99 = float(exec_risk.iloc[0]["ES 99%"])
    exec_worst = float(exec_risk.iloc[0]["Worst P&L"])

    st.subheader("Portfolio Risk Indicators")

    ec1, ec2, ec3 = st.columns(3)

    ec1.metric(
        "Total Portfolio Exposure",
        f"€{exec_exposure / 1e6:,.2f}M"
    )

    ec2.metric(
        "Historical VaR 99% (1-Day)",
        f"€{exec_var99 / 1e6:,.2f}M"
    )

    ec3.metric(
        "Expected Shortfall 99% (1-Day)",
        f"€{exec_es99 / 1e6:,.2f}M"
    )

    ec4, ec5, ec6 = st.columns(3)

    ec4.metric(
        "Fixed Income DV01",
        f"€{exec_dv01:,.2f}"
    )

    ec5.metric(
        "Worst Historical P&L",
        f"€{exec_worst / 1e6:,.2f}M"
    )

    ec6.metric(
        "VaR 99% / Portfolio",
        f"{exec_var99 / exec_exposure:.2%}"
    )

    st.subheader("Portfolio Composition")

    import plotly.express as px

    exec_groups = exec_groups.copy()

    exec_groups["exposure_pct"] = (
        exec_groups["exposure"]
        / exec_exposure
        * 100
    )

    fig_exec_exposure = px.bar(
        exec_groups.sort_values("exposure_pct"),
        x="exposure_pct",
        y="asset_group",
        orientation="h",
        text="exposure_pct",
        labels={
            "exposure_pct": "Portfolio Exposure (%)",
            "asset_group": "Asset Group"
        },
        title="Portfolio Exposure by Asset Group"
    )

    fig_exec_exposure.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_exec_exposure.update_layout(
        xaxis_range=[0, max(exec_groups["exposure_pct"]) * 1.2]
    )

    st.plotly_chart(
        fig_exec_exposure,
        use_container_width=True
    )

    st.subheader("Historical Portfolio P&L")

    exec_pnl["cumulative_pnl"] = (
        exec_pnl["total_pnl"].cumsum()
    )

    fig_exec_pnl = px.line(
        exec_pnl,
        x="date",
        y="cumulative_pnl",
        title="Cumulative Historical Scenario P&L",
        labels={
            "date": "Date",
            "cumulative_pnl": "Cumulative P&L (€)"
        }
    )

    fig_exec_pnl.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray"
    )

    st.plotly_chart(
        fig_exec_pnl,
        use_container_width=True
    )

    st.caption(
        "Cumulative sum of historical daily P&L scenarios "
        "at current portfolio exposures. This is not "
        "a realised investment performance series."
    )

    st.subheader("Data Quality & Model Scope")

    ed1, ed2, ed3 = st.columns(3)

    ed1.metric(
        "Historical Observations",
        f"{len(exec_pnl):,}"
    )

    ed2.metric(
        "First Observation",
        exec_pnl["date"].min().strftime("%Y-%m-%d")
    )

    ed3.metric(
        "Last Observation",
        exec_pnl["date"].max().strftime("%Y-%m-%d")
    )

    st.caption(
        "Historical simulation uses current portfolio "
        "exposures and a one-day risk horizon. "
        "VaR and Expected Shortfall are estimates, "
        "not guaranteed maximum losses. "
        "Results reflect the exported historical sample."
    )


    # ATLAS_SOVEREIGN_RISK_MODULE_V1

    # ============================================================
    # SOVEREIGN RISK ANALYTICS
    # Research module - independent from production risk metrics
    # ============================================================

    import json

    st.divider()


if selected_page == 'Sovereign Risk Analytics':
    st.header("Sovereign Risk Analytics")

    st.caption(
        "Historical simulation of European sovereign bond risk. "
        "Research model covering EUR 225 million of exposures."
    )

    SOVEREIGN_DIR = (
        Path(__file__).resolve().parent.parent / "data" / "demo" / "sovereign"
    )

    @st.cache_data
    def load_sovereign_risk_data():
        comparison = pd.read_csv(
            SOVEREIGN_DIR / "sovereign_risk_model_comparison.csv",
            index_col=0
        )

        instrument_pnl = pd.read_csv(
            SOVEREIGN_DIR / "sovereign_instrument_pnl_convexity.csv",
            index_col="date",
            parse_dates=["date"]
        ).sort_index()

        es_contribution = pd.read_csv(
            SOVEREIGN_DIR / "sovereign_es_contribution.csv",
            index_col=0
        )

        with open(
            SOVEREIGN_DIR / "sovereign_risk_metadata.json",
            encoding="utf-8"
        ) as f:
            metadata = json.load(f)

        return comparison, instrument_pnl, es_contribution, metadata


    try:
        (
            sov_comparison,
            sov_instrument_pnl,
            sov_es_contribution,
            sov_metadata
        ) = load_sovereign_risk_data()

    except (FileNotFoundError, ValueError, KeyError, OSError) as exc:
        st.warning(
            "Sovereign risk research data could not be loaded: "
            f"{exc}"
        )

    else:
        # Historical P&L with convexity
        sov_pnl = sov_instrument_pnl.sum(axis=1)

        sov_var95 = float(
            sov_comparison.loc["VaR_95", "DV01_PLUS_CONVEXITY"]
        )
        sov_var99 = float(
            sov_comparison.loc["VaR_99", "DV01_PLUS_CONVEXITY"]
        )
        sov_es99 = float(
            sov_comparison.loc["ES_99", "DV01_PLUS_CONVEXITY"]
        )

        st.subheader("Sovereign Risk Metrics")

        sm1, sm2, sm3 = st.columns(3)

        sm1.metric("Historical VaR 95%", eur_millions(sov_var95))
        sm2.metric("Historical VaR 99%", eur_millions(sov_var99))
        sm3.metric("Expected Shortfall 99%", eur_millions(sov_es99))

        st.caption(
            f"{sov_metadata['scenarios']} historical scenarios | "
            f"{sov_metadata['holding_period_days']}-day horizon | "
            "DV01 + convexity"
        )

        st.subheader("Historical Sovereign P&L")

        sov_pnl_df = sov_pnl.rename(
            "pnl_eur"
        ).reset_index()

        fig_sov_pnl = px.line(
            sov_pnl_df,
            x="date",
            y="pnl_eur",
            title="Historical Sovereign P&L Scenarios",
            labels={
                "date": "Historical Date",
                "pnl_eur": "Scenario P&L (€)"
            }
        )

        fig_sov_pnl.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray"
        )

        st.plotly_chart(
            fig_sov_pnl,
            use_container_width=True
        )

        st.caption(
            "Historical scenario P&L at constant current exposures; "
            "not realised investment performance."
        )

        st.subheader("Risk Model Comparison")

        sov_comparison_display = sov_comparison.copy()
        sov_comparison_display.index.name = "Metric"

        st.dataframe(
            sov_comparison_display.style.format("{:,.2f}"),
            use_container_width=True
        )

        st.subheader("Expected Shortfall Risk Contribution")

        st.caption(
            "Instrument contributions shown below use the "
            "DV01-only model, not the convexity-adjusted model."
        )

        sov_es_chart = (
            sov_es_contribution.reset_index()
            .rename(columns={
                sov_es_contribution.index.name or "index": "instrument"
            })
        )

        fig_sov_es = px.bar(
            sov_es_chart.sort_values("es_contribution_eur"),
            x="es_contribution_eur",
            y="instrument",
            orientation="h",
            title="ES 99% Contribution by Instrument (DV01 Only)",
            labels={
                "es_contribution_eur": "ES Contribution (€)",
                "instrument": "Instrument"
            }
        )

        st.plotly_chart(
            fig_sov_es,
            use_container_width=True
        )

        st.subheader("Data Quality & Model Scope")

        sq1, sq2, sq3 = st.columns(3)

        sq1.metric(
            "Historical Scenarios",
            f"{len(sov_pnl):,}"
        )

        sq2.metric(
            "First Scenario",
            sov_pnl.index.min().strftime("%Y-%m-%d")
        )

        sq3.metric(
            "Last Scenario",
            sov_pnl.index.max().strftime("%Y-%m-%d")
        )

        st.caption(
            "Model limitations: German 10Y yield is used as a "
            "proxy for German 5Y; positions and sensitivities "
            "are held constant; no FX effects; historical "
            "sample ends in June 2025. "
            "Research model, not production risk reporting."
        )



    # ATLAS_SOVEREIGN_INSTRUMENT_EXPLORER_V1
    # Interactive analysis of sovereign P&L with convexity

    st.divider()


if selected_page == 'Sovereign Risk Analytics':
    st.header("Sovereign Instrument Risk Explorer")

    st.caption(
        "Explore historical risk for individual sovereign bonds "
        "or the complete European sovereign portfolio."
    )

    explorer_file = (
        Path(__file__).resolve().parent.parent / "data" / "demo" / "sovereign"
        / "sovereign_instrument_pnl_convexity.csv"
    )

    if not explorer_file.exists():
        st.warning("Sovereign instrument P&L data not available.")

    else:
        @st.cache_data
        def load_sovereign_explorer_data(path):
            return pd.read_csv(
                path,
                index_col="date",
                parse_dates=["date"]
            ).sort_index()

        explorer_pnl = load_sovereign_explorer_data(
            explorer_file
        )

        explorer_options = [
            "Total Sovereign Portfolio"
        ] + list(explorer_pnl.columns)

        selected_instrument = st.selectbox(
            "Select sovereign instrument",
            explorer_options,
            key="sovereign_instrument_explorer"
        )

        if selected_instrument == "Total Sovereign Portfolio":
            selected_pnl = explorer_pnl.sum(axis=1)
        else:
            selected_pnl = explorer_pnl[selected_instrument]

        selected_losses = -selected_pnl

        explorer_var95 = selected_losses.quantile(0.95)
        explorer_var99 = selected_losses.quantile(0.99)

        explorer_es99 = selected_losses[
            selected_losses >= explorer_var99
        ].mean()

        ex1, ex2, ex3, ex4 = st.columns(4)

        ex1.metric(
            "VaR 95%",
            eur_millions(explorer_var95)
        )

        ex2.metric(
            "VaR 99%",
            eur_millions(explorer_var99)
        )

        ex3.metric(
            "ES 99%",
            eur_millions(explorer_es99)
        )

        ex4.metric(
            "Worst P&L",
            eur_millions(selected_pnl.min())
        )

        explorer_df = selected_pnl.rename(
            "pnl_eur"
        ).reset_index()

        fig_explorer = px.line(
            explorer_df,
            x="date",
            y="pnl_eur",
            title=f"Historical P&L - {selected_instrument}",
            labels={
                "date": "Historical Date",
                "pnl_eur": "Scenario P&L (€)"
            }
        )

        fig_explorer.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray"
        )

        st.plotly_chart(
            fig_explorer,
            use_container_width=True
        )

        st.caption(
            "Historical simulation with constant exposures and "
            "DV01 + convexity. One-day horizon. "
            "German 10Y shocks proxy the German Bund 5Y. "
            "Individual instrument VaR and ES are not additive."
        )



    # ATLAS_SOVEREIGN_WHAT_IF_V1

    st.divider()


if selected_page == 'Sovereign Risk Analytics':
    st.header("Sovereign Portfolio What-If Simulator")

    st.caption(
        "Change sovereign bond exposures and recalculate historical "
        "risk using the same 412 scenarios and DV01 + convexity model. "
        "No changes are made to the actual portfolio."
    )

    whatif_root = Path(__file__).resolve().parent.parent / "data" / "demo"

    whatif_pnl_file = (
        whatif_root / "sovereign"
        / "sovereign_instrument_pnl_convexity.csv"
    )

    whatif_bonds_file = (
        whatif_root / "portfolio"
        / "bond_risk_parameters.csv"
    )

    if not whatif_pnl_file.exists() or not whatif_bonds_file.exists():
        st.error("Required sovereign research files are missing.")

    else:
        @st.cache_data
        def load_whatif_data(pnl_path, bonds_path):
            pnl_data = pd.read_csv(
                pnl_path, index_col="date", parse_dates=["date"]
            ).sort_index()

            bonds_data = pd.read_csv(bonds_path)

            return pnl_data, bonds_data

        whatif_pnl, whatif_bonds = load_whatif_data(
            whatif_pnl_file, whatif_bonds_file
        )

        whatif_bonds = (
            whatif_bonds
            .set_index("instrument_name")
            .loc[whatif_pnl.columns]
        )

        st.subheader("Portfolio Exposure Assumptions")

        st.caption(
            "Adjust each position between 0% and 200% "
            "of its original market value."
        )

        whatif_exposures = {}

        for instrument in whatif_pnl.columns:

            original_value = float(
                whatif_bonds.loc[instrument, "market_value"]
            )

            new_value_m = st.slider(
                instrument + " (€M)",
                min_value=0.0,
                max_value=original_value * 2 / 1_000_000,
                value=original_value / 1_000_000,
                step=1.0,
                key="whatif_" + instrument
            )

            whatif_exposures[instrument] = new_value_m * 1_000_000

        original_exposure = whatif_bonds["market_value"].astype(float)

        simulated_exposure = pd.Series(whatif_exposures)

        exposure_ratio = simulated_exposure / original_exposure

        simulated_pnl = whatif_pnl.mul(
            exposure_ratio, axis=1
        ).sum(axis=1)

        original_pnl = whatif_pnl.sum(axis=1)

        def calculate_whatif_risk(pnl_series):
            losses = -pnl_series

            var95 = losses.quantile(0.95)
            var99 = losses.quantile(0.99)

            es99 = losses[
                losses >= var99
            ].mean()

            return {
                "VaR95": var95,
                "VaR99": var99,
                "ES99": es99,
                "WorstPnL": pnl_series.min()
            }

        original_risk = calculate_whatif_risk(original_pnl)
        simulated_risk = calculate_whatif_risk(simulated_pnl)

        st.subheader("Simulated Portfolio Risk")

        w1, w2, w3 = st.columns(3)

        w1.metric(
            "Simulated VaR 95%",
            eur_millions(simulated_risk["VaR95"]),
            delta=f"{simulated_risk['VaR95'] - original_risk['VaR95']:+,.0f} €",
            delta_color="inverse"
        )

        w2.metric(
            "Simulated VaR 99%",
            eur_millions(simulated_risk["VaR99"]),
            delta=f"{simulated_risk['VaR99'] - original_risk['VaR99']:+,.0f} €",
            delta_color="inverse"
        )

        w3.metric(
            "Simulated ES 99%",
            eur_millions(simulated_risk["ES99"]),
            delta=f"{simulated_risk['ES99'] - original_risk['ES99']:+,.0f} €",
            delta_color="inverse"
        )

        st.caption(
            "Deltas compare the simulated risk against "
            "the original sovereign portfolio. "
            "Negative risk deltas indicate lower risk."
        )

        whatif_comparison = pd.DataFrame({
            "Original Portfolio": original_risk,
            "Simulated Portfolio": simulated_risk
        })

        whatif_comparison["Difference"] = (
            whatif_comparison["Simulated Portfolio"]
            - whatif_comparison["Original Portfolio"]
        )

        st.dataframe(
            whatif_comparison.style.format("€{:,.2f}"),
            use_container_width=True
        )

        st.subheader("Historical Scenario Comparison")

        whatif_chart = pd.DataFrame({
            "date": original_pnl.index,
            "Original Portfolio": original_pnl.values,
            "Simulated Portfolio": simulated_pnl.values
        })

        whatif_chart = whatif_chart.melt(
            id_vars="date",
            var_name="Portfolio",
            value_name="P&L (€)"
        )

        fig_whatif = px.line(
            whatif_chart,
            x="date",
            y="P&L (€)",
            color="Portfolio",
            title="Original vs Simulated Sovereign P&L"
        )

        fig_whatif.add_hline(
            y=0, line_dash="dash", line_color="gray"
        )

        st.plotly_chart(
            fig_whatif,
            use_container_width=True
        )

        st.caption(
            "Research simulation only. P&L is scaled proportionally "
            "with exposure; duration, convexity and risk-factor "
            "sensitivities per euro are held constant. "
            "No trading costs, funding effects or market impact."
        )

    # ATLAS BANK - SOVEREIGN PORTFOLIO OPTIMIZATION



if selected_page == 'Portfolio Optimization':
    st.header("Sovereign Portfolio Optimization")

    st.caption(
        "Comparison of original, unconstrained and diversified "
        "European sovereign bond portfolios. "
        "All portfolios maintain €225M total exposure and constant DV01."
    )

    optimization_dir = (
        Path(__file__).resolve().parent.parent / "data" / "demo" / "sovereign"
    )

    @st.cache_data
    def load_sovereign_optimization():
        risk_data = pd.read_csv(
            optimization_dir / "sovereign_optimization_risk_comparison.csv"
        )

        allocation_data = pd.read_csv(
            optimization_dir / "sovereign_optimization_allocations.csv"
        )

        return risk_data, allocation_data


    opt_risk, opt_alloc = load_sovereign_optimization()

    portfolio_order = [
        "Original",
        "Unconstrained",
        "Diversified"
    ]

    st.subheader("Portfolio Allocation Comparison")

    allocation_chart = px.bar(
        opt_alloc,
        x="portfolio",
        y="exposure_million_eur",
        color="instrument",
        category_orders={"portfolio": portfolio_order},
        barmode="stack",
        labels={
            "portfolio": "Portfolio",
            "exposure_million_eur": "Exposure (€M)",
            "instrument": "Sovereign Instrument"
        },
        title="Sovereign Bond Allocation by Portfolio"
    )

    allocation_chart.update_layout(
        yaxis_title="Exposure (€M)",
        legend_title="Instrument"
    )

    st.plotly_chart(
        allocation_chart,
        use_container_width=True
    )

    st.subheader("Portfolio Risk Comparison")

    risk_columns = [
        "VaR 95% (€)",
        "VaR 99% (€)",
        "ES 99% (€)",
        "Worst Loss (€)"
    ]

    selected_metric = st.selectbox(
        "Select risk metric",
        risk_columns,
        index=2,
        key="sovereign_optimization_metric"
    )

    risk_chart = px.bar(
        opt_risk,
        x="portfolio",
        y=selected_metric,
        color="portfolio",
        category_orders={"portfolio": portfolio_order},
        labels={
            "portfolio": "Portfolio",
            selected_metric: selected_metric
        },
        title=f"{selected_metric} by Portfolio"
    )

    risk_chart.update_layout(showlegend=False)

    st.plotly_chart(
        risk_chart,
        use_container_width=True
    )

    st.subheader("Optimization Results")

    risk_table = opt_risk.set_index("portfolio").reindex(
        portfolio_order
    )

    st.dataframe(
        risk_table.style.format({
            "VaR 95% (€)": "€{:,.2f}",
            "VaR 99% (€)": "€{:,.2f}",
            "ES 99% (€)": "€{:,.2f}",
            "Worst Loss (€)": "€{:,.2f}",
            "Exposure (€M)": "{:,.2f}"
        }),
        use_container_width=True
    )

    original_es = float(
        risk_table.loc["Original", "ES 99% (€)"]
    )

    unconstrained_es = float(
        risk_table.loc["Unconstrained", "ES 99% (€)"]
    )

    diversified_es = float(
        risk_table.loc["Diversified", "ES 99% (€)"]
    )

    es1, es2 = st.columns(2)

    es1.metric(
        "ES Reduction - Unconstrained",
        f"€{original_es - unconstrained_es:,.0f}",
        f"{(original_es - unconstrained_es) / original_es * 100:.2f}%"
    )

    es2.metric(
        "ES Reduction - Diversified",
        f"€{original_es - diversified_es:,.0f}",
        f"{(original_es - diversified_es) / original_es * 100:.2f}%"
    )

    st.caption(
        "Historical simulation based on 412 one-day scenarios. "
        "ES 99% uses the Rockafellar-Uryasev formulation. "
        "Optimization results are research estimates, "
        "not investment recommendations."
    )


# ============================================================
# CREDIT RISK ANALYTICS
# ============================================================

if selected_page == "Credit Risk Analytics":

    from credit_risk import render_credit_risk

    render_credit_risk()


if selected_page == "Liquidity Risk Analytics":
    from liquidity_risk import render_liquidity_risk

    render_liquidity_risk()
