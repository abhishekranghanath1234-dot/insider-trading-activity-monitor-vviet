import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Money Signals",
    page_icon="🚀",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(
        "PREMIUM_CROSS_MARKET_SIGNALS.csv"
    )

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🚀 Smart Money Signals")

st.markdown("""
Cross-Market Signal Analysis combining
Institutional Holdings, Insider Activity,
Risk Metrics and Opportunity Scores.
""")

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Filters")

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

    if selected_sector != "All":
        df = df[
            df["sector"] ==
            selected_sector
        ]

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
total_signals = len(df)

avg_signal = (
    df["signal_strength"].mean()
    if "signal_strength" in df.columns
    else 0
)

avg_risk = (
    df["risk_score"].mean()
    if "risk_score" in df.columns
    else 0
)

strong_buy_count = 0

if "recommendation" in df.columns:
    strong_buy_count = len(
        df[
            df["recommendation"]
            .astype(str)
            .str.upper()
            .str.contains("BUY")
        ]
    )

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Signals",
    f"{total_signals:,}"
)

col2.metric(
    "Strong Buy Signals",
    strong_buy_count
)

col3.metric(
    "Avg Signal Strength",
    f"{avg_signal:.1f}"
)

col4.metric(
    "Avg Risk Score",
    f"{avg_risk:.1f}"
)

st.divider()

# --------------------------------------------------
# TOP SIGNALS
# --------------------------------------------------
if (
    "issuer_name" in df.columns
    and "signal_strength" in df.columns
):

    st.subheader("🏆 Top Signal Rankings")

    top_signals = (
        df.sort_values(
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
        text_auto=True,
        title="Highest Signal Strength"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# RECOMMENDATION DISTRIBUTION
# --------------------------------------------------
if "recommendation" in df.columns:

    st.subheader("📋 Recommendation Distribution")

    fig = px.pie(
        df,
        names="recommendation",
        hole=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# SIGNAL VS RISK
# --------------------------------------------------
if (
    "signal_strength" in df.columns
    and "risk_score" in df.columns
):

    st.subheader(
        "⚖️ Signal Strength vs Risk"
    )

    fig = px.scatter(
        df,
        x="risk_score",
        y="signal_strength",
        color="recommendation"
        if "recommendation" in df.columns
        else None,
        size="signal_strength",
        hover_name="issuer_name"
        if "issuer_name" in df.columns
        else None
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# SECTOR ANALYSIS
# --------------------------------------------------
if (
    "sector" in df.columns
    and "signal_strength" in df.columns
):

    st.subheader("🏢 Sector Analysis")

    sector_df = (
        df.groupby("sector")
        ["signal_strength"]
        .mean()
        .reset_index()
        .sort_values(
            "signal_strength",
            ascending=False
        )
    )

    fig = px.bar(
        sector_df,
        x="sector",
        y="signal_strength",
        color="signal_strength",
        title="Average Signal Strength by Sector"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# HEATMAP
# --------------------------------------------------
if (
    "sector" in df.columns
    and "recommendation" in df.columns
):

    st.subheader("🔥 Signal Heatmap")

    heatmap_df = pd.crosstab(
        df["sector"],
        df["recommendation"]
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

# --------------------------------------------------
# RADAR CHART
# --------------------------------------------------
if (
    "signal_strength" in df.columns
    and "risk_score" in df.columns
    and "conviction_score" in df.columns
):

    st.subheader("📡 Signal Radar")

    avg_signal_strength = (
        df["signal_strength"].mean()
    )

    avg_risk_score = (
        df["risk_score"].mean()
    )

    avg_conviction = (
        df["conviction_score"].mean()
    )

    radar = go.Figure()

    radar.add_trace(
        go.Scatterpolar(
            r=[
                avg_signal_strength,
                avg_conviction,
                avg_risk_score
            ],
            theta=[
                "Signal Strength",
                "Conviction",
                "Risk Score"
            ],
            fill="toself",
            name="Average Metrics"
        )
    )

    radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        ),
        showlegend=False
    )

    st.plotly_chart(
        radar,
        use_container_width=True
    )

# --------------------------------------------------
# TOP OPPORTUNITIES TABLE
# --------------------------------------------------
if (
    "signal_strength" in df.columns
):

    st.subheader("⭐ Top Opportunities")

    opportunities = (
        df.sort_values(
            "signal_strength",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        opportunities,
        use_container_width=True
    )

# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------
st.subheader("📊 Correlation Matrix")

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
# AI INSIGHTS
# --------------------------------------------------
st.subheader("🤖 Smart Money Insights")

if (
    "issuer_name" in df.columns
    and "signal_strength" in df.columns
):

    strongest = df.loc[
        df["signal_strength"].idxmax()
    ]

    st.success(
        f"🏆 Strongest Signal: "
        f"{strongest['issuer_name']} "
        f"(Score: {strongest['signal_strength']})"
    )

if (
    "sector" in df.columns
    and "signal_strength" in df.columns
):

    best_sector = (
        df.groupby("sector")
        ["signal_strength"]
        .mean()
        .idxmax()
    )

    st.success(
        f"🚀 Best Performing Sector: "
        f"{best_sector}"
    )

if (
    "risk_score" in df.columns
):

    lowest_risk = (
        df["risk_score"].min()
    )

    st.info(
        f"🛡 Lowest Risk Score: "
        f"{lowest_risk}"
    )

# --------------------------------------------------
# RAW DATA
# --------------------------------------------------
st.subheader("📄 Signal Dataset")

st.dataframe(
    df,
    use_container_width=True
)

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------
csv = df.to_csv(index=False)

st.download_button(
    "⬇ Download Signals Data",
    csv,
    "smart_money_signals.csv",
    "text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")

st.caption(
    "Smart Money Dashboard | Smart Money Signals Module"
)
