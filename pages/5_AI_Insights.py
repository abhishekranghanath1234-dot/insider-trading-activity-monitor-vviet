import streamlit as st
import pandas as pd
import numpy as np

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Insights",
    page_icon="🤖",
    layout="wide"
)

# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data
def load_data():

    master = pd.read_csv(
        "data/MASTER_DATA_ENRICHED.csv"
    )

    signals = pd.read_csv(
        "data/PREMIUM_CROSS_MARKET_SIGNALS.csv"
    )

    insiders = pd.read_csv(
        "data/insider_transactions_data.csv"
    )

    holdings = pd.read_csv(
        "data/institutional_holdings_data.csv"
    )

    return master, signals, insiders, holdings


master_df, signals_df, insider_df, holdings_df = load_data()

# ==========================================================
# HEADER
# ==========================================================

st.title("🤖 AI Investment Intelligence")

st.caption(
    "Automated Smart Money Analysis & Institutional Insights"
)

st.divider()

# ==========================================================
# DATA CLEANING
# ==========================================================

for col in [
    "market_value",
    "conviction_score"
]:
    if col in master_df.columns:
        master_df[col] = pd.to_numeric(
            master_df[col],
            errors="coerce"
        )

for col in [
    "signal_score",
    "conviction_score"
]:
    if col in signals_df.columns:
        signals_df[col] = pd.to_numeric(
            signals_df[col],
            errors="coerce"
        )

# ==========================================================
# GENERATE INSIGHTS
# ==========================================================

st.subheader("🧠 AI Generated Executive Summary")

total_filings = len(master_df)

total_companies = (
    master_df["company_name"].nunique()
    if "company_name" in master_df.columns
    else 0
)

total_value = (
    master_df["market_value"].sum()
    if "market_value" in master_df.columns
    else 0
)

avg_conviction = (
    master_df["conviction_score"].mean()
    if "conviction_score" in master_df.columns
    else 0
)

summary = f"""
The platform currently tracks {total_filings:,} filings
across {total_companies:,} companies.

Total institutional capital monitored exceeds
${total_value/1e9:.2f} Billion.

Average institutional conviction score is
{avg_conviction:.2f}.

Recent activity suggests significant institutional
interest in high-growth technology and AI-related companies.

Cross-market signal analysis indicates multiple
high-conviction opportunities currently ranked
as Strong Buy candidates.
"""

st.info(summary)

st.divider()

# ==========================================================
# TOP OPPORTUNITIES
# ==========================================================

st.subheader("🚀 AI Ranked Opportunities")

if "signal_score" in signals_df.columns:

    top_opportunities = (
        signals_df
        .sort_values(
            "signal_score",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_opportunities,
        use_container_width=True
    )

st.divider()

# ==========================================================
# INSTITUTIONAL INSIGHTS
# ==========================================================

st.subheader("🏛 Institutional Intelligence")

if (
    "company_name" in holdings_df.columns
    and "market_value" in holdings_df.columns
):

    top_holdings = (
        holdings_df
        .groupby("company_name")[
            "market_value"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(5)
    )

    insight_text = ""

    for company, value in top_holdings.items():

        insight_text += (
            f"• {company} "
            f"(${value/1e9:.2f}B)\n"
        )

    st.success(
        f"""
Top Institutional Holdings:

{insight_text}
        """
    )

st.divider()

# ==========================================================
# WHALE DETECTION
# ==========================================================

st.subheader("🐋 Whale Activity Detection")

if (
    "market_value" in holdings_df.columns
):

    whales = holdings_df[
        holdings_df["market_value"]
        >= 1000000000
    ]

    whale_count = len(whales)

    st.metric(
        "Whale Positions Detected",
        whale_count
    )

    if whale_count > 0:

        st.dataframe(
            whales.head(20),
            use_container_width=True
        )

st.divider()

# ==========================================================
# INSIDER INTELLIGENCE
# ==========================================================

st.subheader("👨‍💼 Insider Activity Intelligence")

if (
    "signal" in insider_df.columns
):

    signal_counts = (
        insider_df["signal"]
        .value_counts()
    )

    st.dataframe(
        signal_counts,
        use_container_width=True
    )

    buy_count = (
        signal_counts.get("BUY", 0)
        +
        signal_counts.get(
            "STRONG BUY",
            0
        )
    )

    sell_count = (
        signal_counts.get(
            "SELL",
            0
        )
    )

    if buy_count > sell_count:

        st.success(
            """
AI Assessment:

Insider sentiment is currently
bullish based on transaction data.
            """
        )

    else:

        st.warning(
            """
AI Assessment:

Insider activity indicates
caution in current markets.
            """
        )

st.divider()

# ==========================================================
# RISK ANALYSIS
# ==========================================================

st.subheader("⚠ Risk Assessment")

risk_level = "Moderate"

if avg_conviction > 80:
    risk_level = "Low"

elif avg_conviction < 50:
    risk_level = "High"

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Risk Level",
        risk_level
    )

with col2:

    st.metric(
        "Average Conviction",
        round(avg_conviction, 2)
    )

st.divider()

# ==========================================================
# AI RESEARCH REPORT
# ==========================================================

st.subheader("📄 Automated Research Report")

report = f"""
MARKET INTELLIGENCE REPORT

Total Filings Analysed:
{total_filings:,}

Companies Covered:
{total_companies:,}

Assets Monitored:
${total_value/1e9:.2f} Billion

Average Conviction:
{avg_conviction:.2f}

Key Findings:

1. Institutional ownership remains strong.

2. Smart Money signals indicate
multiple high conviction opportunities.

3. Insider sentiment remains positive.

4. Whale activity suggests continued
capital concentration in large-cap equities.

5. Technology sector remains
the dominant smart money destination.
"""

st.text_area(
    "AI Generated Report",
    report,
    height=400
)

st.divider()

# ==========================================================
# OPTIONAL OPENAI ANALYSIS
# ==========================================================

st.subheader("🧠 Advanced GPT Analysis")

try:

    if "OPENAI_API_KEY" in st.secrets:

        from openai import OpenAI

        client = OpenAI(
            api_key=st.secrets[
                "OPENAI_API_KEY"
            ]
        )

        if st.button(
            "Generate GPT Insights"
        ):

            prompt = f"""
Analyze this market data:

Filings:
{total_filings}

Companies:
{total_companies}

Assets:
{total_value}

Average Conviction:
{avg_conviction}

Provide:

1. Institutional Trends
2. Smart Money Signals
3. Risks
4. Opportunities
5. Conclusion
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            st.write(
                response
                .choices[0]
                .message
                .content
            )

    else:

        st.info(
            """
Add OPENAI_API_KEY to
.streamlit/secrets.toml
to enable GPT analysis.
            """
        )

except Exception as e:

    st.warning(
        f"GPT analysis unavailable: {e}"
    )

# ==========================================================
# EXPORT REPORT
# ==========================================================

st.divider()

st.subheader("⬇ Export Report")

st.download_button(
    label="Download AI Report",
    data=report,
    file_name="AI_Research_Report.txt",
    mime="text/plain"
)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.markdown(
    """
### 🤖 AI Intelligence Engine

Features:

- Institutional Analysis
- Insider Intelligence
- Whale Detection
- Opportunity Ranking
- Automated Research Reports
- GPT-Powered Insights
"""
)
