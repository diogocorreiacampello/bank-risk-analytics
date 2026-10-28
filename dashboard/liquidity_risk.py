from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "demo"
    / "liquidity"
)


@st.cache_data
def load_liquidity_data():
    names = [
        "liquidity_deposit_overview",
        "liquidity_deposit_segments",
        "liquidity_deposit_types",
        "liquidity_deposit_geography",
        "liquidity_deposit_concentration",
        "liquidity_segment_concentration",
        "liquidity_funding_structure",
        "liquidity_funding_maturity",
        "liquidity_funding_counterparties",
    ]

    return {
        name: pd.read_csv(DATA_DIR / f"{name}.csv")
        for name in names
    }


def format_amount(value, currency="EUR"):
    symbols = {"EUR": "€", "GBP": "£", "USD": "$"}
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{value / 1_000_000:,.2f}M"


def render_liquidity_risk():
    st.title("Liquidity Risk Analytics")
    st.caption(
        "Deposit and funding analytics based on simulated "
        "banking data. Not regulatory liquidity reporting."
    )

    data = load_liquidity_data()

    overview = data["liquidity_deposit_overview"].iloc[0]
    concentration = data["liquidity_deposit_concentration"].iloc[0]

    st.subheader("Deposit Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Deposits",
        format_amount(overview["total_balance"])
    )
    col2.metric(
        "Deposit Accounts",
        f"{int(overview['accounts']):,}"
    )
    col3.metric(
        "Largest Depositor",
        f"{concentration['top1_share']:.2%}"
    )
    col4.metric(
        "Top 10 Depositors",
        f"{concentration['top10_share']:.2%}"
    )

    st.subheader("Deposit Composition")

    segments = data["liquidity_deposit_segments"]
    deposit_types = data["liquidity_deposit_types"]

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            segments,
            x="customer_type",
            y="total_balance",
            title="Deposits by Customer Segment",
            labels={
                "customer_type": "Customer Segment",
                "total_balance": "Balance (EUR)"
            }
        )
        st.plotly_chart(fig, width="stretch")

    with right:
        fig = px.pie(
            deposit_types,
            names="deposit_type",
            values="total_balance",
            title="Deposits by Account Type"
        )
        st.plotly_chart(fig, width="stretch")

    st.subheader("Geographic Distribution")

    geography = data["liquidity_deposit_geography"]

    fig = px.bar(
        geography,
        x="country",
        y="total_balance",
        title="Deposits by Country",
        labels={
            "country": "Country",
            "total_balance": "Balance (EUR)"
        }
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader("Deposit Concentration")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Customer HHI",
        f"{concentration['customer_hhi']:.6f}"
    )
    c2.metric(
        "Top 5 Depositors",
        f"{concentration['top5_share']:.2%}"
    )
    c3.metric(
        "Effective Depositors",
        f"{1 / concentration['customer_hhi']:,.0f}"
    )

    segment_concentration = data[
        "liquidity_segment_concentration"
    ]

    st.dataframe(
        segment_concentration,
        width="stretch",
        hide_index=True
    )

    st.subheader("Funding Analytics")

    funding = data["liquidity_funding_structure"]
    currencies = sorted(funding["currency"].unique())

    selected_currency = st.selectbox(
        "Funding Currency",
        currencies,
        index=currencies.index("EUR")
        if "EUR" in currencies else 0
    )

    selected_funding = funding[
        funding["currency"] == selected_currency
    ]

    total_funding = selected_funding["total_amount"].sum()

    st.metric(
        f"Total Funding ({selected_currency})",
        format_amount(total_funding, selected_currency)
    )

    fig = px.bar(
        selected_funding,
        x="funding_type",
        y="total_amount",
        title=f"Funding Structure - {selected_currency}",
        labels={
            "funding_type": "Funding Type",
            "total_amount": f"Amount ({selected_currency})"
        }
    )
    st.plotly_chart(fig, width="stretch")

    maturity = data["liquidity_funding_maturity"]
    selected_maturity = maturity[
        maturity["currency"] == selected_currency
    ]

    reference_date = maturity["reference_date"].iloc[0]

    st.caption(f"Funding maturity reference date: {reference_date}")

    fig = px.bar(
        selected_maturity,
        x="maturity_bucket",
        y="total_amount",
        title=f"Funding Maturity Profile - {selected_currency}",
        labels={
            "maturity_bucket": "Maturity Bucket",
            "total_amount": f"Amount ({selected_currency})"
        }
    )
    st.plotly_chart(fig, width="stretch")

    counterparties = data["liquidity_funding_counterparties"]
    selected_counterparties = counterparties[
        counterparties["currency"] == selected_currency
    ]

    fig = px.bar(
        selected_counterparties,
        x="counterparty",
        y="total_amount",
        title=f"Funding Counterparties - {selected_currency}",
        labels={
            "counterparty": "Counterparty",
            "total_amount": f"Amount ({selected_currency})"
        }
    )
    st.plotly_chart(fig, width="stretch")

    st.info(
        "Liquidity metrics are illustrative and based on "
        "simulated data. LCR and NSFR are not calculated "
        "in this dashboard version."
    )

    from liquidity_stress import render_liquidity_stress

    st.divider()
    render_liquidity_stress(segments)

    from liquidity_buffer import render_liquidity_buffer

    st.divider()
    render_liquidity_buffer(segments)
