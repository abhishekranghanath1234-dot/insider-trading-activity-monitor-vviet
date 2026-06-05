import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Money Dashboard",
    page_icon="📈",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.kpi-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 12px;
    color: white;
    text-align: center;
}

h1,h2,h3 {
    color:#2563EB;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("MASTER_DATA_ENRICHED.csv")

try:
    df = load_data()
except:
    st.error("MASTER_DATA_ENRICHED.csv not found.")
    st.stop()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("📈 Smart Money Surveillance Dashboard")
st.markdown("Track Institutional Holdings, Insider Activity and Smart Money Signals")

# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------
with st.expander("View Raw Data"):
    st.dataframe(df.head(100))

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Records",
        len(df)
    )

with col2:
    company_count = (
        df["issuer_name"].nunique()
        if "issuer_name" in df.columns
        else 0
    )

    st.metric(
        "Companies",
        company_count
    )

with col3:

    if "market_value" in df.columns:
        total_value = df["market_value"].sum()

        st.metric(
            "Market Value",
            f"${total_value:,.0f}"
        )

with col4:

    if "conviction_score" in df.columns:

        avg_conviction = (
            df["conviction_score"].mean()
        )

        st.metric(
            "Avg Conviction",
            round(avg_conviction, 2)
        )

st.divider()

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.sidebar.header("Filters")

if "issuer_name" in df.columns:

    companies = sorted(
        df["issuer_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_company = st.sidebar.selectbox(
        "Select Company",
        ["All"] + companies
    )

    if selected_company != "All":
        df = df[
            df["issuer_name"]
            == selected_company
        ]

# --------------------------------------------------
# TOP HOLDINGS
# --------------------------------------------------
if (
    "issuer_name" in df.columns
    and "market_value" in df.columns
):

    st.subheader("🏆 Top Holdings")

    top_holdings = (
        df.groupby("issuer_name")["market_value"]
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
        title="Top Institutional Holdings"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# TREEMAP
# --------------------------------------------------
if (
    "issuer_name" in df.columns
    and "market_value" in df.columns
):

    st.subheader("🌳 Holdings Treemap")

    tree = (
        df.groupby("issuer_name")["market_value"]
        .sum()
        .reset_index()
    )

    fig = px.treemap(
        tree,
        path=["issuer_name"],
        values="market_value"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# CONVICTION SCORE
# --------------------------------------------------
if "conviction_score" in df.columns:

    st.subheader("🎯 Conviction Score Distribution")

    fig = px.histogram(
        df,
        x="conviction_score",
        nbins=25,
        title="Conviction Score Histogram"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# SCATTER ANALYSIS
# --------------------------------------------------
if (
    "market_value" in df.columns
    and "conviction_score" in df.columns
):

    st.subheader("📍 Market Value vs Conviction")

    fig = px.scatter(
        df,
        x="conviction_score",
        y="market_value",
        hover_name="issuer_name",
        size="market_value",
        color="conviction_score"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# INSIDER TRANSACTIONS
# --------------------------------------------------
if "transaction_code" in df.columns:

    st.subheader("👨‍💼 Insider Activity")

    trans = (
        df["transaction_code"]
        .value_counts()
        .reset_index()
    )

    trans.columns = [
        "Transaction",
        "Count"
    ]

    fig = px.pie(
        trans,
        names="Transaction",
        values="Count",
        hole=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# HEATMAP
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
# TOP SMART MONEY PICKS
# --------------------------------------------------
if (
    "issuer_name" in df.columns
    and "conviction_score" in df.columns
):

    st.subheader("⭐ Smart Money Ranking")

    ranking = (
        df.groupby("issuer_name")
        ["conviction_score"]
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

# --------------------------------------------------
# AI INSIGHTS
# --------------------------------------------------
st.subheader("🤖 Auto Insights")

insights = []

if (
    "issuer_name" in df.columns
    and "market_value" in df.columns
):

    top_company = (
        df.groupby("issuer_name")
        ["market_value"]
        .sum()
        .idxmax()
    )

    top_value = (
        df.groupby("issuer_name")
        ["market_value"]
        .sum()
        .max()
    )

    insights.append(
        f"🏆 Largest Holding: {top_company} (${top_value:,.0f})"
    )

if "conviction_score" in df.columns:

    avg_score = (
        df["conviction_score"]
        .mean()
    )

    insights.append(
        f"🎯 Average Conviction Score: {avg_score:.2f}"
    )

for item in insights:
    st.success(item)

# --------------------------------------------------
# DOWNLOAD FILTERED DATA
# --------------------------------------------------
st.subheader("⬇ Download Data")

csv = df.to_csv(index=False)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption(
    "Smart Money Dashboard • Streamlit • Plotly • Pandas"
)
