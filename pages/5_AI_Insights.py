import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI Insights",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():

    master = pd.read_csv(
        "MASTER_DATA_ENRICHED.csv"
    )

    signals = pd.read_csv(
        "PREMIUM_CROSS_MARKET_SIGNALS.csv"
    )

    return master, signals

try:
    master_df, signals_df = load_data()

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🤖 AI Smart Money Insights")

st.markdown("""
Automated insights generated from
Institutional Holdings, Insider Activity,
Conviction Scores and Market Signals.
""")

st.divider()

# --------------------------------------------------
# EXECUTIVE SUMMARY
# --------------------------------------------------
st.subheader("📋 Executive Summary")

total_companies = (
    master_df["issuer_name"]
    .nunique()
)

total_value = (
    master_df["market_value"]
    .sum()
)

avg_conviction = (
    master_df["conviction_score"]
    .mean()
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Companies",
    total_companies
)

col2.metric(
    "Portfolio Value",
    f"${total_value:,.0f}"
)

col3.metric(
    "Avg Conviction",
    f"{avg_conviction:.2f}"
)

st.divider()

# --------------------------------------------------
# TOP HOLDING INSIGHT
# --------------------------------------------------
st.subheader("🏆 Largest Institutional Holding")

top_company = (
    master_df.groupby("issuer_name")
    ["market_value"]
    .sum()
    .idxmax()
)

top_value = (
    master_df.groupby("issuer_name")
    ["market_value"]
    .sum()
    .max()
)

st.success(
    f"""
    Largest Holding:
    {top_company}

    Market Value:
    ${top_value:,.0f}
    """
)

# --------------------------------------------------
# CONVICTION INSIGHT
# --------------------------------------------------
st.subheader("🎯 Highest Conviction Pick")

conviction_df = (
    master_df.groupby("issuer_name")
    ["conviction_score"]
    .mean()
)

best_conviction = conviction_df.idxmax()
best_score = conviction_df.max()

st.success(
    f"""
    Highest Conviction Company:
    {best_conviction}

    Conviction Score:
    {best_score:.2f}
    """
)

# --------------------------------------------------
# STRONGEST SIGNAL
# --------------------------------------------------
if (
    "signal_strength"
    in signals_df.columns
):

    st.subheader("🚀 Strongest Signal")

    strongest = signals_df.loc[
        signals_df["signal_strength"]
        .idxmax()
    ]

    st.success(
        f"""
        Company:
        {strongest['issuer_name']}

        Signal Strength:
        {strongest['signal_strength']}
        """
    )

# --------------------------------------------------
# BEST SECTOR
# --------------------------------------------------
if (
    "sector" in signals_df.columns
):

    st.subheader("🏢 Best Performing Sector")

    sector_scores = (
        signals_df.groupby("sector")
        ["signal_strength"]
        .mean()
    )

    best_sector = sector_scores.idxmax()
    best_sector_score = sector_scores.max()

    st.success(
        f"""
        Sector:
        {best_sector}

        Avg Signal Strength:
        {best_sector_score:.2f}
        """
    )

# --------------------------------------------------
# RECOMMENDATION ANALYSIS
# --------------------------------------------------
if (
    "recommendation"
    in signals_df.columns
):

    st.subheader(
        "📊 Recommendation Breakdown"
    )

    rec_counts = (
        signals_df["recommendation"]
        .value_counts()
        .reset_index()
    )

    rec_counts.columns = [
        "Recommendation",
        "Count"
    ]

    fig = px.pie(
        rec_counts,
        names="Recommendation",
        values="Count",
        hole=0.4
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# TOP OPPORTUNITIES
# --------------------------------------------------
if (
    "signal_strength"
    in signals_df.columns
):

    st.subheader(
        "⭐ Top Investment Opportunities"
    )

    opportunities = (
        signals_df.sort_values(
            "signal_strength",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        opportunities[
            [
                "issuer_name",
                "signal_strength",
                "risk_score",
                "recommendation"
            ]
        ],
        use_container_width=True
    )

# --------------------------------------------------
# RISK ANALYSIS
# --------------------------------------------------
if (
    "risk_score"
    in signals_df.columns
):

    st.subheader("⚠ Risk Analysis")

    fig = px.histogram(
        signals_df,
        x="risk_score",
        nbins=20,
        title="Risk Score Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# AI GENERATED REPORT
# --------------------------------------------------
st.subheader("📝 Automated AI Report")

report = f"""
SMART MONEY REPORT

Total Companies Analysed:
{total_companies}

Total Portfolio Value:
${total_value:,.0f}

Highest Conviction Pick:
{best_conviction}

Largest Holding:
{top_company}

Top Sector:
{best_sector if 'sector' in signals_df.columns else 'N/A'}

Market Outlook:
Positive institutional activity detected.

Recommended Focus:
Top conviction and strong signal companies.
"""

st.text_area(
    "Generated Report",
    report,
    height=300
)

# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------
st.download_button(
    label="⬇ Download AI Report",
    data=report,
    file_name="AI_Smart_Money_Report.txt",
    mime="text/plain"
)

# --------------------------------------------------
# INSIGHT SCORECARD
# --------------------------------------------------
st.subheader("📈 Insight Scorecard")

scorecard = pd.DataFrame({
    "Metric": [
        "Portfolio Value",
        "Average Conviction",
        "Largest Holding",
        "Best Conviction Pick"
    ],
    "Value": [
        f"${total_value:,.0f}",
        round(avg_conviction, 2),
        top_company,
        best_conviction
    ]
})

st.dataframe(
    scorecard,
    use_container_width=True
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")

st.caption(
    "Smart Money Dashboard | AI Insights Module"
)
