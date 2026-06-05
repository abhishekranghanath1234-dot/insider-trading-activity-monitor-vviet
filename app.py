import streamlit as st
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Smart Money Surveillance",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

css_file = Path("assets/styles.css")

if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    logo_path = Path("assets/logo.png")

    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)

    st.title("Smart Money Surveillance")

    st.markdown("---")

    st.markdown(
        """
### Platform Modules

📊 Dashboard

👨‍💼 Insider Transactions

🏛 Institutional Holdings

🚨 Smart Money Signals

🤖 AI Insights
"""
    )

    st.markdown("---")

    st.info(
        """
Monitor institutional investors,
insider trades, whale positions,
and AI-powered investment signals.
"""
    )

# =====================================================
# HERO SECTION
# =====================================================

st.title("📈 Smart Money Surveillance Platform")

st.markdown(
    """
### Institutional Intelligence Platform

Track:

- Insider Transactions
- Institutional Holdings
- Whale Activity
- Conviction Scores
- Smart Money Signals
- AI Generated Insights

Built with Streamlit, Plotly, Pandas and AI.
"""
)

st.divider()

# =====================================================
# OVERVIEW CARDS
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Modules",
        "5"
    )

with col2:
    st.metric(
        "Analytics",
        "25+"
    )

with col3:
    st.metric(
        "Charts",
        "15+"
    )

with col4:
    st.metric(
        "AI Reports",
        "Enabled"
    )

st.divider()

# =====================================================
# FEATURE GRID
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🏛 Institutional Intelligence")

    st.markdown(
        """
- Top Institutional Holders
- Portfolio Allocation
- Sector Analysis
- Whale Tracking
- Conviction Rankings
"""
    )

    st.subheader("👨‍💼 Insider Monitoring")

    st.markdown(
        """
- Executive Purchases
- Executive Sales
- Confidence Scores
- Transaction Timeline
- Insider Sentiment
"""
    )

with col2:

    st.subheader("🚨 Smart Money Signals")

    st.markdown(
        """
- Signal Scoring Engine
- Buy/Sell Recommendations
- Opportunity Ranking
- Sector Heatmaps
- Cross-Market Analytics
"""
    )

    st.subheader("🤖 AI Intelligence")

    st.markdown(
        """
- Automated Reports
- Whale Detection
- Risk Analysis
- GPT Insights
- Investment Summaries
"""
    )

st.divider()

# =====================================================
# DATASETS
# =====================================================

st.subheader("📂 Connected Datasets")

datasets = [
    "MASTER_DATA_ENRICHED.csv",
    "PREMIUM_CROSS_MARKET_SIGNALS.csv",
    "insider_transactions_data.csv",
    "institutional_holdings_data.csv"
]

for dataset in datasets:
    st.success(f"✓ {dataset}")

st.divider()

# =====================================================
# QUICK START
# =====================================================

st.subheader("🚀 Quick Start")

st.markdown(
    """
1. Open the sidebar navigation.
2. Select Dashboard for overview analytics.
3. Explore Insider Transactions.
4. Review Institutional Holdings.
5. Analyze Smart Money Signals.
6. Generate AI Insights.
"""
)

st.divider()

# =====================================================
# PROJECT STRUCTURE
# =====================================================

with st.expander("📁 Project Structure"):

    st.code(
        """
smart-money-surveillance/
│
├── app.py
├── requirements.txt
├── README.md
│
├── assets/
│   ├── logo.png
│   └── styles.css
│
├── data/
│   ├── MASTER_DATA_ENRICHED.csv
│   ├── PREMIUM_CROSS_MARKET_SIGNALS.csv
│   ├── insider_transactions_data.csv
│   └── institutional_holdings_data.csv
│
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Insider_Transactions.py
│   ├── 3_Institutional_Holdings.py
│   ├── 4_Smart_Money_Signals.py
│   └── 5_AI_Insights.py
│
└── utils/
    ├── analytics.py
    ├── charts.py
    └── data_loader.py
"""
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
### 🧠 Smart Money Surveillance

Institutional Holdings • Insider Trading • Smart Money Signals • AI Research

Built using Streamlit + Plotly + Python
"""
)
