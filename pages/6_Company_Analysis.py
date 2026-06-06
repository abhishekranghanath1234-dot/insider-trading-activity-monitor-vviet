import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import (
    load_master_data,
    load_insider_data,
    load_holdings_data
)

from utils.risk_scoring import (
    calculate_risk_score,
    classify_risk
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Company Analysis",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Company Analysis")
st.markdown("Comprehensive company intelligence dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    master = load_master_data()
    insider = load_insider_data()
    holdings = load_holdings_data()
    return master, insider, holdings


master_df, insider_df, holdings_df = load_data()

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

if master_df.empty:
    st.error("MASTER_DATA_ENRICHED.csv not found or empty")
    st.stop()

if "Company" not in master_df.columns:
    st.error("Column 'Company' not found in MASTER_DATA_ENRICHED.csv")
    st.stop()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

company_list = sorted(master_df["Company"].dropna().unique())

selected_company = st.sidebar.selectbox(
    "Select Company",
    company_list
)

# --------------------------------------------------
# COMPANY DATA
# --------------------------------------------------

company_data = master_df[
    master_df["Company"] == selected_company
]

if company_data.empty:
    st.warning("No data available.")
    st.stop()

company = company_data.iloc[0]

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(selected_company)

    if "Sector" in company_data.columns:
        st.write(f"**Sector:** {company['Sector']}")

    if "Industry" in company_data.columns:
        st.write(f"**Industry:** {company['Industry']}")

with col2:
    st.metric(
        "Market Cap",
        f"${company.get('MarketCap',0):,.0f}"
        if pd.notna(company.get("MarketCap", 0))
        else "N/A"
    )

st.markdown("---")

# --------------------------------------------------
# RISK SCORE
# --------------------------------------------------

try:
    risk_score = calculate_risk_score(company)
except:
    risk_score = 50

risk_level = classify_risk(risk_score)

c1, c2, c3 = st.columns(3)

c1.metric("Risk Score", f"{risk_score:.1f}")
c2.metric("Risk Category", risk_level)

if "RevenueGrowth" in company_data.columns:
    c3.metric(
        "Revenue Growth",
        f"{company['RevenueGrowth']}%"
    )

st.markdown("---")

# --------------------------------------------------
# COMPANY FUNDAMENTALS
# --------------------------------------------------

st.subheader("📊 Fundamental Metrics")

metric_cols = st.columns(4)

metrics = [
    ("Revenue", "Revenue"),
    ("Net Income", "NetIncome"),
    ("Debt", "Debt"),
    ("Institutional Ownership", "InstitutionalOwnership")
]

for idx, (label, column) in enumerate(metrics):
    if column in company_data.columns:
        metric_cols[idx].metric(
            label,
            f"{company[column]:,.2f}"
            if pd.notna(company[column])
            else "N/A"
        )

st.markdown("---")

# --------------------------------------------------
# INSIDER TRANSACTIONS
# --------------------------------------------------

st.subheader("👤 Insider Activity")

if not insider_df.empty:

    insider_company = insider_df[
        insider_df["Company"] == selected_company
    ]

    if not insider_company.empty:

        buy_count = len(
            insider_company[
                insider_company["TransactionType"]
                .str.upper()
                .str.contains("BUY")
            ]
        )

        sell_count = len(
            insider_company[
                insider_company["TransactionType"]
                .str.upper()
                .str.contains("SELL")
            ]
        )

        col1, col2 = st.columns(2)

        col1.metric("Buy Transactions", buy_count)
        col2.metric("Sell Transactions", sell_count)

        if "TransactionDate" in insider_company.columns:

            insider_company["TransactionDate"] = pd.to_datetime(
                insider_company["TransactionDate"],
                errors="coerce"
            )

            trend = (
                insider_company
                .groupby("TransactionDate")
                .size()
                .reset_index(name="Count")
            )

            fig = px.line(
                trend,
                x="TransactionDate",
                y="Count",
                title="Insider Activity Trend"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.dataframe(
            insider_company.sort_values(
                by=insider_company.columns[0],
                ascending=False
            ),
            use_container_width=True
        )

    else:
        st.info("No insider activity found.")

else:
    st.info("Insider transaction dataset unavailable.")

st.markdown("---")

# --------------------------------------------------
# INSTITUTIONAL HOLDINGS
# --------------------------------------------------

st.subheader("🏦 Institutional Holdings")

if not holdings_df.empty:

    holdings_company = holdings_df[
        holdings_df["Company"] == selected_company
    ]

    if not holdings_company.empty:

        st.dataframe(
            holdings_company,
            use_container_width=True
        )

        if (
            "Institution" in holdings_company.columns
            and "OwnershipPercent" in holdings_company.columns
        ):

            fig = px.bar(
                holdings_company,
                x="Institution",
                y="OwnershipPercent",
                title="Institutional Ownership Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.info("No institutional holdings data found.")

else:
    st.info("Holdings dataset unavailable.")

st.markdown("---")

# --------------------------------------------------
# COMPANY HEALTH
# --------------------------------------------------

st.subheader("🩺 Company Health Assessment")

health_score = 100

if "Debt" in company_data.columns:
    if company["Debt"] > 1000000000:
        health_score -= 20

if "RevenueGrowth" in company_data.columns:
    if company["RevenueGrowth"] < 0:
        health_score -= 25

if risk_score > 70:
    health_score -= 30

health_score = max(0, health_score)

if health_score >= 80:
    health_status = "Excellent"
elif health_score >= 60:
    health_status = "Good"
elif health_score >= 40:
    health_status = "Average"
else:
    health_status = "Weak"

col1, col2 = st.columns(2)

col1.metric("Health Score", health_score)
col2.metric("Assessment", health_status)

st.markdown("---")

# --------------------------------------------------
# AI SUMMARY
# --------------------------------------------------

st.subheader("🤖 AI Company Summary")

summary = f"""
### {selected_company}

**Risk Assessment:** {risk_level}

**Risk Score:** {risk_score:.1f}

**Health Status:** {health_status}

The company operates in the
{company.get('Sector', 'Unknown')} sector.

Current institutional ownership and insider
activity patterns suggest monitoring of future
capital flows and executive trading behavior.

Recommended focus areas:

- Insider transaction trends
- Institutional accumulation/distribution
- Revenue growth sustainability
- Debt management
- Risk score changes
"""

st.markdown(summary)

# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------

st.markdown("---")

report_df = pd.DataFrame({
    "Metric": [
        "Company",
        "Risk Score",
        "Risk Category",
        "Health Score",
        "Health Status"
    ],
    "Value": [
        selected_company,
        risk_score,
        risk_level,
        health_score,
        health_status
    ]
})

csv = report_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Company Report",
    data=csv,
    file_name=f"{selected_company}_analysis.csv",
    mime="text/csv"
)
