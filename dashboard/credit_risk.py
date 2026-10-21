from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data" / "demo" / "credit"
)


def load_credit_data():
    """Load aggregated, simulated credit risk datasets."""

    files = {
        "overview": "credit_portfolio_overview.csv",
        "segments": "credit_segment_risk.csv",
        "ratings": "credit_rating_risk.csv",
        "concentration": "credit_customer_concentration.csv",
    }

    return {
        key: pd.read_csv(DATA_DIR / filename)
        for key, filename in files.items()
    }


def render_credit_risk():
    """Render the Atlas Bank Credit Risk Analytics page."""

    data = load_credit_data()

    overview = data["overview"].iloc[0]
    segments = data["segments"].copy()
    ratings = data["ratings"].copy()
    concentration = data["concentration"].iloc[0]

    st.header("Credit Risk Analytics")

    st.caption(
        "Simulated loan portfolio | "
        "Probability of Default | "
        "Loss Given Default | "
        "Exposure at Default | "
        "Expected Loss"
    )

    # Portfolio KPIs

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total EAD",
        f"€{overview['total_ead'] / 1e9:,.2f}B"
    )

    c2.metric(
        "Expected Loss",
        f"€{overview['total_expected_loss'] / 1e6:,.2f}M"
    )

    c3.metric(
        "Expected Loss Rate",
        f"{overview['expected_loss_rate'] * 100:.4f}%"
    )

    c4.metric(
        "EAD-Weighted PD",
        f"{overview['ead_weighted_pd'] * 100:.4f}%"
    )

    st.caption(
        f"{int(overview['total_loans']):,} simulated loans | "
        f"{int(overview['unique_customers']):,} customers | "
        f"{int(overview['segments'])} credit segments"
    )

    st.divider()

    # Segment risk

    st.subheader("Credit Risk by Segment")

    segments["EAD (€M)"] = segments["total_ead"] / 1e6
    segments["Expected Loss (€M)"] = (
        segments["expected_loss"] / 1e6
    )

    fig_ead = px.bar(
        segments,
        x="loan_type",
        y="EAD (€M)",
        title="Exposure at Default by Segment",
        labels={"loan_type": "Segment"}
    )

    st.plotly_chart(fig_ead, width="stretch")

    fig_el = px.bar(
        segments,
        x="loan_type",
        y="Expected Loss (€M)",
        title="Expected Loss by Segment",
        labels={"loan_type": "Segment"}
    )

    st.plotly_chart(fig_el, width="stretch")

    # Risk contribution

    st.subheader("Exposure vs Expected Loss Contribution")

    contribution = segments.melt(
        id_vars="loan_type",
        value_vars=["ead_share_pct", "el_share_pct"],
        var_name="Metric",
        value_name="Share (%)"
    )

    contribution["Metric"] = contribution["Metric"].map({
        "ead_share_pct": "EAD Share",
        "el_share_pct": "Expected Loss Share"
    })

    fig_contribution = px.bar(
        contribution,
        x="loan_type",
        y="Share (%)",
        color="Metric",
        barmode="group",
        title="Portfolio Risk Contribution by Segment",
        labels={"loan_type": "Segment"}
    )

    st.plotly_chart(
        fig_contribution,
        width="stretch"
    )

    st.divider()

    # Rating quality

    st.subheader("Credit Quality by Rating")

    rating_order = [
        "AAA", "AA", "A", "BBB", "BB", "B", "CCC"
    ]

    ratings["Expected Loss Rate (%)"] = (
        ratings["expected_loss_rate"] * 100
    )

    fig_rating = px.bar(
        ratings,
        x="rating",
        y="Expected Loss Rate (%)",
        category_orders={"rating": rating_order},
        title="Expected Loss Rate by Credit Rating",
        labels={"rating": "Credit Rating"}
    )

    st.plotly_chart(
        fig_rating,
        width="stretch"
    )

    st.dataframe(
        ratings[
            [
                "rating",
                "loans",
                "total_ead",
                "expected_loss",
                "weighted_pd",
                "expected_loss_rate"
            ]
        ],
        width="stretch",
        hide_index=True
    )

    st.divider()

    # Customer concentration

    st.subheader("Customer Concentration Risk")

    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Top 10 Customer Concentration",
        f"{concentration['top_10_concentration'] * 100:.2f}%"
    )

    k2.metric(
        "Largest Customer EAD",
        f"€{concentration['largest_customer_ead'] / 1e6:.2f}M"
    )

    k3.metric(
        "Customer HHI",
        f"{concentration['customer_hhi']:.6f}"
    )

    st.caption(
        "Customer concentration is calculated from "
        "aggregated exposures. No individual customer "
        "identifiers are included in the demo datasets."
    )

    st.divider()

    st.caption(
        "Research environment using simulated data. "
        "Expected Loss is calculated as PD × LGD × EAD. "
        "Results are illustrative and do not constitute "
        "regulatory capital estimates."
    )
