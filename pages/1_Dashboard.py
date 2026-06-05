import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------
# PAGE CONFIG
# -----------------------------------------
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------------------
# LOAD DATA
# -----------------------------------------
@st.cache_data
def load_data():

    master = pd.read_csv("MASTER_DATA_ENRICHED.csv")

    try:
        signals = pd.read_csv(
            "PREMIUM_CROSS_MARKET_SIGNALS.csv"
        )
    except:
        signals = pd.DataFrame()

    return master, signals

master_df, signals_df = load_data()

# -----------------------------------------
# HEADER
# -----------------------------------------
st.title("📈 Smart Money Dashboard")

st.markdown(
    """
    Institutional Holdings • Insider Trading
    • Cross Market Signals
    """
)

st.divider()

# -----------------------------------------
# KPI CARDS
# -----------------------------------------
total_companies = (
    master_df["issuer_name"].nunique()
    if "issuer_name" in master_df.columns
    else 0
)

total_records = len(master_df)

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
    "Companies",
    f"{total_companies:,}"
)

col2.metric(
    "Records",
    f"{total_records:,}"
)

col3.metric(
    "Market Value",
    f"${total_market_value:,.0f}"
)

col4.metric(
    "Avg Conviction",
    f"{avg_conviction:.1f}"
)

st.divider()

# -----------------------------------------
# TOP HOLDINGS
# -----------------------------------------
if (
    "issuer_name" in master_df.columns
    and "market_value" in master_df.columns
):

    st.subheader("🏆 Top Holdings")

    holdings = (
        master_df.groupby("issuer_name")
        ["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        holdings,
        x="issuer_name",
        y="market_value",
        color="market_value",
        title="Top Institutional Holdings"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------------
# TREEMAP
# -----------------------------------------
if (
    "issuer_name" in master_df.columns
    and "market_value" in master_df.columns
):

    st.subheader("🌳 Holdings Treemap")

    tree = (
        master_df.groupby("issuer_name")
        ["market_value"]
        .sum()
        .reset_index()
    )

    fig = px.treemap(
        tree,
        path=["issuer_name"],
        values="market_value",
        title="Market Value Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------------
# CONVICTION ANALYSIS
# -----------------------------------------
if "conviction_score" in master_df.columns:

    st.subheader("🎯 Conviction Distribution")

    fig = px.histogram(
        master_df,
        x="conviction_score",
        nbins=20,
        title="Conviction Score Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------------
# SCATTER ANALYSIS
# -----------------------------------------
if (
    "conviction_score" in master_df.columns
    and "market_value" in master_df.columns
):

    st.subheader(
        "📍 Market Value vs Conviction"
    )

    fig = px.scatter(
        master_df,
        x="conviction_score",
        y="market_value",
        color="conviction_score",
        size="market_value",
        hover_name="issuer_name"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------------
# SIGNAL STRENGTH
# -----------------------------------------
if (
    not signals_df.empty
    and "issuer_name" in signals_df.columns
    and "signal_strength"
    in signals_df.columns
):

    st.subheader(
        "🚀 Signal Strength Ranking"
    )

    top_signals = (
        signals_df.sort_values(
            "signal_strength",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        top_signals,
        x="issuer_name",
        y="signal_strength",
        color="signal_strength",
        title="Top Smart Money Signals"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------------
# RECOMMENDATIONS
# -----------------------------------------
if (
    not signals_df.empty
    and "recommendation"
    in signals_df.columns
):

    st.subheader(
        "📋 Recommendation Breakdown"
    )

    fig = px.pie(
        signals_df,
        names="recommendation",
        title="Buy / Hold / Sell"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------------
# HEATMAP
# -----------------------------------------
st.subheader("🔥 Correlation Heatmap")

numeric_df = master_df.select_dtypes(
    include=np.number
)

if len(numeric_df.columns) > 1:

    corr = numeric_df.corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------------
# TOP SMART MONEY PICKS
# -----------------------------------------
if (
    "issuer_name" in master_df.columns
    and "conviction_score"
    in master_df.columns
):

    st.subheader(
        "⭐ Top Conviction Picks"
    )

    ranking = (
        master_df.groupby(
            "issuer_name"
        )["conviction_score"]
        .mean()
        .reset_index()
        .sort_values(
            "conviction_score",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

# -----------------------------------------
# INSIGHTS
# -----------------------------------------
st.subheader("🤖 AI Style Insights")

insights = []

if (
    "issuer_name" in master_df.columns
    and "market_value"
    in master_df.columns
):

    top_company = (
        master_df.groupby(
            "issuer_name"
        )["market_value"]
        .sum()
        .idxmax()
    )

    top_value = (
        master_df.groupby(
            "issuer_name"
        )["market_value"]
        .sum()
        .max()
    )

    insights.append(
        f"🏆 Largest Holding: {top_company} (${top_value:,.0f})"
    )

if "conviction_score" in master_df.columns:

    insights.append(
        f"🎯 Average Conviction Score: "
        f"{master_df['conviction_score'].mean():.2f}"
    )

if (
    not signals_df.empty
    and "signal_strength"
    in signals_df.columns
):

    strongest = signals_df.loc[
        signals_df["signal_strength"]
        .idxmax()
    ]

    insights.append(
        f"🚀 Strongest Signal: "
        f"{strongest['issuer_name']} "
        f"({strongest['signal_strength']})"
    )

for insight in insights:
    st.success(insight)

# -----------------------------------------
# DATA DOWNLOAD
# -----------------------------------------
st.subheader("⬇ Export Data")

csv = master_df.to_csv(index=False)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="smart_money_data.csv",
    mime="text/csv"
)

# -----------------------------------------
# FOOTER
# -----------------------------------------
st.markdown("---")

st.caption(
    "Smart Money Dashboard | Streamlit + Plotly"
)
