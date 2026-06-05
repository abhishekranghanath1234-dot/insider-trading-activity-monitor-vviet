import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Institutional Holdings",
    page_icon="🏦",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("MASTER_DATA_ENRICHED.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🏦 Institutional Holdings Analysis")

st.markdown("""
Analyze institutional ownership, position sizes,
conviction scores and portfolio concentration.
""")

st.divider()

# --------------------------------------------------
# REQUIRED COLUMNS CHECK
# --------------------------------------------------
required_cols = ["issuer_name", "market_value"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Required column '{col}' not found.")
        st.stop()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Filters")

companies = sorted(
    df["issuer_name"]
    .dropna()
    .unique()
)

selected_company = st.sidebar.selectbox(
    "Select Company",
    ["All"] + list(companies)
)

if selected_company != "All":
    df = df[
        df["issuer_name"] ==
        selected_company
    ]

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
total_holdings = len(df)

total_market_value = (
    df["market_value"].sum()
)

avg_position = (
    df["market_value"].mean()
)

largest_position = (
    df["market_value"].max()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Holdings",
    f"{total_holdings:,}"
)

col2.metric(
    "Market Value",
    f"${total_market_value:,.0f}"
)

col3.metric(
    "Avg Position",
    f"${avg_position:,.0f}"
)

col4.metric(
    "Largest Position",
    f"${largest_position:,.0f}"
)

st.divider()

# --------------------------------------------------
# TOP HOLDINGS
# --------------------------------------------------
st.subheader("🏆 Top Holdings")

top_holdings = (
    df.groupby("issuer_name")
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
    top_holdings,
    x="issuer_name",
    y="market_value",
    color="market_value",
    text_auto=".2s",
    title="Top Institutional Holdings"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# TREEMAP
# --------------------------------------------------
st.subheader("🌳 Holdings Treemap")

fig = px.treemap(
    top_holdings,
    path=["issuer_name"],
    values="market_value",
    title="Portfolio Allocation"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# MARKET VALUE DISTRIBUTION
# --------------------------------------------------
st.subheader("📈 Market Value Distribution")

fig = px.histogram(
    df,
    x="market_value",
    nbins=25,
    title="Distribution of Holdings"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# CONVICTION SCORE
# --------------------------------------------------
if "conviction_score" in df.columns:

    st.subheader("🎯 Conviction Scores")

    conviction_df = (
        df.groupby("issuer_name")
        ["conviction_score"]
        .mean()
        .reset_index()
        .sort_values(
            "conviction_score",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        conviction_df,
        x="issuer_name",
        y="conviction_score",
        color="conviction_score",
        title="Highest Conviction Holdings"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# BUBBLE CHART
# --------------------------------------------------
if (
    "conviction_score" in df.columns
    and "market_value" in df.columns
):

    st.subheader("🔵 Holdings Bubble Analysis")

    fig = px.scatter(
        df,
        x="conviction_score",
        y="market_value",
        size="market_value",
        color="conviction_score",
        hover_name="issuer_name",
        title="Conviction vs Position Size"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# VOTING SHARES
# --------------------------------------------------
if "voting_shares" in df.columns:

    st.subheader("🗳 Voting Shares")

    voting_df = (
        df.groupby("issuer_name")
        ["voting_shares"]
        .sum()
        .reset_index()
        .sort_values(
            "voting_shares",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        voting_df,
        x="issuer_name",
        y="voting_shares",
        color="voting_shares",
        title="Voting Shares Held"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------
st.subheader("🔥 Correlation Heatmap")

numeric_df = df.select_dtypes(
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

# --------------------------------------------------
# TOP INSTITUTIONAL PICKS
# --------------------------------------------------
st.subheader("⭐ Institutional Favorites")

favorites = (
    df.groupby("issuer_name")
    ["market_value"]
    .sum()
    .reset_index()
    .sort_values(
        "market_value",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    favorites,
    use_container_width=True
)

# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------
st.subheader("🤖 Portfolio Insights")

largest_company = (
    df.groupby("issuer_name")
    ["market_value"]
    .sum()
    .idxmax()
)

largest_value = (
    df.groupby("issuer_name")
    ["market_value"]
    .sum()
    .max()
)

st.success(
    f"🏆 Largest Institutional Position: "
    f"{largest_company} (${largest_value:,.0f})"
)

if "conviction_score" in df.columns:

    best_conviction = (
        df.groupby("issuer_name")
        ["conviction_score"]
        .mean()
        .idxmax()
    )

    score = (
        df.groupby("issuer_name")
        ["conviction_score"]
        .mean()
        .max()
    )

    st.success(
        f"🎯 Highest Conviction Holding: "
        f"{best_conviction} ({score:.2f})"
    )

# --------------------------------------------------
# RAW DATA
# --------------------------------------------------
st.subheader("📄 Holdings Data")

st.dataframe(
    df,
    use_container_width=True
)

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------
csv = df.to_csv(index=False)

st.download_button(
    "⬇ Download Holdings Data",
    csv,
    "institutional_holdings.csv",
    "text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")

st.caption(
    "Smart Money Dashboard | Institutional Holdings Module"
)
