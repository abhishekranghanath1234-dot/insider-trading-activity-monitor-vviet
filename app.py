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
# LOAD CUSTOM CSS
# =====================================================

with open("assets/style.css", "r", encoding="utf-8") as f:
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

    st.markdown("""
### Platform Modules

📊 Dashboard

👨‍💼 Insider Transactions

🏛 Institutional Holdings

🚨 Smart Money Signals

🤖 AI Insights
""")

    st.markdown("---")

    st.info("""
Monitor institutional investors,
insider trades, whale positions,
and AI-powered investment signals.
""")

# =====================================================
# PREMIUM HERO SECTION
# =====================================================

st.markdown("""
<div class="hero-header">
    <h1>📈 Smart Money Surveillance</h1>
    <p>
        AI-Powered Institutional Intelligence Platform
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
### Institutional Intelligence Platform

Track:

- Insider Transactions
- Institutional Holdings
- Whale Activity
- Conviction Scores
- Smart Money Signals
- AI Generated Insights

Built with Streamlit, Plotly, Pandas and AI.
""")

st.divider()

# =====================================================
# KPI SECTION
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Modules", "5")

with col2:
    st.metric("Analytics", "25+")

with col3:
    st.metric("Charts", "15+")

with col4:
    st.metric("AI Reports", "Enabled")

st.divider()

# =====================================================
# FEATURE GRID
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.markdown("""
<div class="glass">
<h3>🏛 Institutional Intelligence</h3>

- Top Institutional Holders
- Portfolio Allocation
- Sector Analysis
- Whale Tracking
- Conviction Rankings

<br>

<h3>👨‍💼 Insider Monitoring</h3>

- Executive Purchases
- Executive Sales
- Confidence Scores
- Transaction Timeline
- Insider Sentiment
</div>
""", unsafe_allow_html=True)

with col2:

    st.markdown("""
<div class="glass">
<h3>🚨 Smart Money Signals</h3>

- Signal Scoring Engine
- Buy/Sell Recommendations
- Opportunity Ranking
- Sector Heatmaps
- Cross-Market Analytics

<br>

<h3>🤖 AI Intelligence</h3>

- Automated Reports
- Whale Detection
- Risk Analysis
- GPT Insights
- Investment Summaries
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
1. Open the sidebar navigation.
2. Select Dashboard for overview analytics.
3. Explore Insider Transactions.
4. Review Institutional Holdings.
5. Analyze Smart Money Signals.
6. Generate AI Insights.
""")

st.divider()

# =====================================================
# PROJECT STRUCTURE
# =====================================================

with st.expander("📁 Project Structure"):

    st.code("""
smart-money-surveillance/
│
├── app.py
├── requirements.txt
├── README.md
│
├── assets/
│   ├── logo.png
│   └── style.css
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
""")

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown("""
<div class="footer">
<h4>🧠 Smart Money Surveillance</h4>

Institutional Holdings • Insider Trading • Smart Money Signals • AI Research

<br><br>

Built using Streamlit + Plotly + Python
</div>
""", unsafe_allow_html=True)
