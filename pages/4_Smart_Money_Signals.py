import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Smart Money Signals",
    page_icon="🚨",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    return pd.read_csv(
        "data/PREMIUM_CROSS_MARKET_SIGNALS.csv"
    )

df = load_data()

# =====================================================
# PAGE HEADER
# =====================================================

st.title("🚨 Smart Money Signals Engine")

st.caption(
    "Institutional Activity • Insider Buying • Conviction Analysis • Opportunity Detection"
)

st.divider()

# =====================================================
# DATA PREPARATION
# =====================================================

numeric_cols = [
    "conviction_score",
    "insider_score",
    "institutional_score",
    "market_value",
    "signal_score"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

if "signal_date" in df.columns:
    df["signal_date"] = pd.to_datetime(
        df["signal_date"],
        errors="coerce"
    )

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("🔍 Signal Filters")

selected_sector = "All"

if "sector" in df.columns:

    sectors = sorted(
        df["sector"]
        .dropna()
        .unique()
    )

    selected_sector = st.sidebar.selectbox(
        "Sector",
        ["All"] + list(sectors)
    )

selected_recommendation = "All"

if "recommendation" in df.columns:

    recs = sorted(
        df["recommendation"]
        .dropna()
        .unique()
    )

    selected_recommendation = st.sidebar.selectbox(
        "Recommendation",
        ["All"] + list(recs)
    )

# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = df.copy()

if (
    selected_sector != "All"
    and "sector" in filtered_df.columns
):
    filtered_df = filtered_df[
        filtered_df["sector"]
        == selected_sector
    ]

if (
    selected_recommendation != "All"
    and "recommendation" in filtered_df.columns
):
    filtered_df = filtered_df[
        filtered_df["recommendation"]
        == selected_recommendation
    ]

# =====================================================
# SIGNAL SCORE CREATION
# =====================================================

required_cols = [
    "conviction_score",
    "insider_score",
    "institutional_score"
]

if all(col in filtered_df.columns for col in required_cols):

    filtered_df["calculated_signal_score"] = (
        filtered_df["conviction_score"] * 0.50 +
        filtered_df["insider_score"] * 0.30 +
        filtered_df["institutional_score"] * 0.20
    )

else:

    filtered_df["calculated_signal_score"] = 0

# =====================================================
# KPI SECTION
# =====================================================

total_signals = len(filtered_df)

strong_buy_count = 0
buy_count = 0

if "recommendation" in filtered_df.columns:

    strong_buy_count = len(
        filtered_df[
            filtered_df["recommendation"]
            == "STRONG BUY"
        ]
    )

    buy_count = len(
        filtered_df[
            filtered_df["recommendation"]
            == "BUY"
        ]
    )

avg_score = (
    filtered_df["calculated_signal_score"]
    .mean()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Signals",
    f"{total_signals:,}"
)

col2.metric(
    "Strong Buy",
    f"{strong_buy_count:,}"
)

col3.metric(
    "Buy",
    f"{buy_count:,}"
)

col4.metric(
    "Avg Score",
    f"{avg_score:.1f}"
)

st.divider()

# =====================================================
# TOP OPPORTUNITIES
# =====================================================

st.subheader("🏆 Top Smart Money Opportunities")

top_opportunities = (
    filtered_df
    .sort_values(
        "calculated_signal_score",
        ascending=False
    )
    .head(20)
)

st.dataframe(
    top_opportunities,
    use_container_width=True
)

st.divider()

# =====================================================
# SIGNAL DISTRIBUTION
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("📊 Recommendation Distribution")

    if "recommendation" in filtered_df.columns:

        rec_df = (
            filtered_df["recommendation"]
            .value_counts()
            .reset_index()
        )

        rec_df.columns = [
            "Recommendation",
            "Count"
        ]

        fig = px.pie(
            rec_df,
            names="Recommendation",
            values="Count",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with col2:

    st.subheader("📈 Signal Score Histogram")

    fig = px.histogram(
        filtered_df,
        x="calculated_signal_score",
        nbins=20
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# SECTOR ANALYSIS
# =====================================================

st.subheader("🏢 Sector Signal Analysis")

if (
    "sector" in filtered_df.columns
    and "calculated_signal_score" in filtered_df.columns
):

    sector_df = (
        filtered_df
        .groupby("sector")[
            "calculated_signal_score"
        ]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        sector_df,
        x="sector",
        y="calculated_signal_score",
        title="Average Signal Score by Sector"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# CONVICTION VS INSIDER SCORE
# =====================================================

st.subheader("🔥 Conviction vs Insider Activity")

if all(
    col in filtered_df.columns
    for col in [
        "conviction_score",
        "insider_score"
    ]
):

    fig = px.scatter(
        filtered_df,
        x="conviction_score",
        y="insider_score",
        size="calculated_signal_score",
        color="recommendation",
        hover_data=["company_name"],
        title="Smart Money Signal Matrix"
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
# MARKET VALUE ANALYSIS
# =====================================================

st.subheader("💰 Market Value vs Signal Score")

if (
    "market_value" in filtered_df.columns
):

    fig = px.scatter(
        filtered_df,
        x="market_value",
        y="calculated_signal_score",
        color="recommendation",
        hover_data=["company_name"]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# TREEMAP
# =====================================================

st.subheader("🌳 Opportunity Treemap")

if (
    "company_name" in filtered_df.columns
    and "market_value" in filtered_df.columns
):

    treemap_df = (
        filtered_df
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(30)
    )

    fig = px.treemap(
        treemap_df,
        path=["sector", "company_name"],
        values="market_value",
        color="calculated_signal_score"
    )

    fig.update_layout(
        height=700
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# HEATMAP
# =====================================================

st.subheader("🌡 Signal Heatmap")

if (
    "sector" in filtered_df.columns
    and "recommendation" in filtered_df.columns
):

    heatmap_df = pd.crosstab(
        filtered_df["sector"],
        filtered_df["recommendation"]
    )

    fig = px.imshow(
        heatmap_df,
        text_auto=True,
        aspect="auto"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# STRONG BUY TABLE
# =====================================================

st.subheader("🚀 Strong Buy Candidates")

if "recommendation" in filtered_df.columns:

    strong_buys = filtered_df[
        filtered_df["recommendation"]
        == "STRONG BUY"
    ]

    st.dataframe(
        strong_buys.sort_values(
            "calculated_signal_score",
            ascending=False
        ),
        use_container_width=True
    )

st.divider()

# =====================================================
# RAW DATA
# =====================================================

with st.expander("📄 View Full Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )

# =====================================================
# DOWNLOAD
# =====================================================

csv = filtered_df.to_csv(
    index=False
)

st.download_button(
    "⬇ Download Signals",
    csv,
    "smart_money_signals.csv",
    "text/csv"
)

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    """
    ### 🧠 Smart Money Signal Engine

    Proprietary scoring system combining:

    - Institutional Conviction
    - Insider Transactions
    - Capital Allocation
    - Cross-Market Intelligence
    - Opportunity Ranking
    """
)
