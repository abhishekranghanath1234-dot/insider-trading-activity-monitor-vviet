import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    master = pd.read_csv(
        "data/MASTER_DATA_ENRICHED.csv"
    )

    signals = pd.read_csv(
        "data/PREMIUM_CROSS_MARKET_SIGNALS.csv"
    )

    return master, signals


master_df, signals_df = load_data()

# =====================================================
# PAGE TITLE
# =====================================================

st.title("📊 Smart Money Dashboard")

st.caption(
    "Institutional Holdings • Insider Activity • Cross Market Intelligence"
)

st.divider()

# =====================================================
# DATA CLEANING
# =====================================================

if "market_value" in master_df.columns:

    master_df["market_value"] = pd.to_numeric(
        master_df["market_value"],
        errors="coerce"
    )

if "conviction_score" in master_df.columns:

    master_df["conviction_score"] = pd.to_numeric(
        master_df["conviction_score"],
        errors="coerce"
    )

# =====================================================
# KPI SECTION
# =====================================================

total_filings = len(master_df)

total_companies = (
    master_df["company_name"].nunique()
    if "company_name" in master_df.columns
    else 0
)

total_market_value = (
    master_df["market_value"].sum()
    if "market_value" in master_df.columns
    else 0
)

avg_conviction = (
    master_df["conviction_score"].mean()
    if "conviction_score" in master_df.columns
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Filings",
    f"{total_filings:,}"
)

col2.metric(
    "Companies",
    f"{total_companies:,}"
)

col3.metric(
    "Portfolio Value",
    f"${total_market_value/1e9:.2f}B"
)

col4.metric(
    "Avg Conviction",
    f"{avg_conviction:.1f}"
)

st.divider()

# =====================================================
# FILTERS
# =====================================================

st.subheader("🎯 Dashboard Filters")

col1, col2 = st.columns(2)

with col1:

    if "company_name" in master_df.columns:

        companies = sorted(
            master_df["company_name"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_company = st.selectbox(
            "Select Company",
            ["All"] + companies
        )

with col2:

    if "form_type" in master_df.columns:

        forms = sorted(
            master_df["form_type"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_form = st.selectbox(
            "Form Type",
            ["All"] + forms
        )

filtered_df = master_df.copy()

if (
    "company_name" in filtered_df.columns
    and selected_company != "All"
):
    filtered_df = filtered_df[
        filtered_df["company_name"]
        == selected_company
    ]

if (
    "form_type" in filtered_df.columns
    and selected_form != "All"
):
    filtered_df = filtered_df[
        filtered_df["form_type"]
        == selected_form
    ]

# =====================================================
# TOP HOLDINGS
# =====================================================

left, right = st.columns(2)

with left:

    st.subheader("🏆 Top Holdings")

    if (
        "company_name" in filtered_df.columns
        and "market_value" in filtered_df.columns
    ):

        top_holdings = (
            filtered_df
            .groupby("company_name")["market_value"]
            .sum()
            .reset_index()
            .sort_values(
                "market_value",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            top_holdings,
            x="market_value",
            y="company_name",
            orientation="h",
            title="Largest Holdings"
        )

        fig.update_layout(
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with right:

    st.subheader("📈 Conviction Distribution")

    if "conviction_score" in filtered_df.columns:

        fig = px.histogram(
            filtered_df,
            x="conviction_score",
            nbins=30,
            title="Conviction Score Histogram"
        )

        fig.update_layout(
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

st.divider()

# =====================================================
# TREEMAP
# =====================================================

st.subheader("🌳 Market Value Treemap")

if (
    "company_name" in filtered_df.columns
    and "market_value" in filtered_df.columns
):

    tree_df = (
        filtered_df
        .groupby("company_name")["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(30)
    )

    fig = px.treemap(
        tree_df,
        path=["company_name"],
        values="market_value",
        title="Portfolio Allocation"
    )

    fig.update_layout(
        height=650
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# CONVICTION VS MARKET VALUE
# =====================================================

st.subheader("🔥 Conviction vs Market Value")

if (
    "market_value" in filtered_df.columns
    and "conviction_score" in filtered_df.columns
):

    scatter_df = (
        filtered_df
        .dropna(
            subset=[
                "market_value",
                "conviction_score"
            ]
        )
        .head(5000)
    )

    fig = px.scatter(
        scatter_df,
        x="conviction_score",
        y="market_value",
        hover_data=["company_name"],
        title="Conviction vs Capital Allocation"
    )

    fig.update_layout(
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# SIGNAL LEADERBOARD
# =====================================================

st.subheader("🚨 Smart Money Signals")

if not signals_df.empty:

    score_col = None

    possible_cols = [
        "signal_score",
        "score",
        "strength",
        "conviction_score"
    ]

    for col in possible_cols:

        if col in signals_df.columns:

            score_col = col
            break

    if score_col:

        leaderboard = (
            signals_df
            .sort_values(
                score_col,
                ascending=False
            )
            .head(25)
        )

    else:

        leaderboard = signals_df.head(25)

    st.dataframe(
        leaderboard,
        use_container_width=True
    )

st.divider()

# =====================================================
# WHALE DETECTION
# =====================================================

st.subheader("🐋 Whale Positions")

if "market_value" in filtered_df.columns:

    whales = filtered_df[
        filtered_df["market_value"]
        > 100000000
    ]

    if len(whales) > 0:

        whale_table = (
            whales[
                [
                    "company_name",
                    "market_value"
                ]
            ]
            .sort_values(
                "market_value",
                ascending=False
            )
            .head(20)
        )

        st.dataframe(
            whale_table,
            use_container_width=True
        )

    else:

        st.info(
            "No whale positions detected."
        )

st.divider()

# =====================================================
# RAW DATA
# =====================================================

with st.expander("📄 View Raw Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    ### 🧠 Smart Money Intelligence

    Institutional Holdings • Insider Tracking • AI Analytics
    """
)
