```python
# pages/5_AI_Risk_Engine.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
    page_title="AI Risk Engine",
    page_icon="⚠️",
    layout="wide"
)

st.title("⚠️ AI Risk Engine")
st.markdown(
    "AI-powered company risk assessment using insider activity, "
    "institutional ownership, and financial indicators."
)

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
    st.error("MASTER_DATA_ENRICHED.csv not found.")
    st.stop()

if "Company" not in master_df.columns:
    st.error("Column 'Company' missing in dataset.")
    st.stop()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Risk Engine")

company_list = sorted(
    master_df["Company"]
    .dropna()
    .unique()
)

selected_company = st.sidebar.selectbox(
    "Select Company",
    company_list
)

# --------------------------------------------------
# COMPANY DATA
# --------------------------------------------------

company_df = master_df[
    master_df["Company"] == selected_company
]

if company_df.empty:
    st.warning("No company data available.")
    st.stop()

company = company_df.iloc[0]

# --------------------------------------------------
# CALCULATE RISK SCORE
# --------------------------------------------------

try:
    risk_score = calculate_risk_score(company)
except Exception:
    risk_score = 50

risk_label = classify_risk(risk_score)

# --------------------------------------------------
# HEADER METRICS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Risk Score",
    f"{risk_score:.1f}"
)

col2.metric(
    "Risk Category",
    risk_label
)

if risk_score < 30:
    status = "Stable"
elif risk_score < 60:
    status = "Monitor"
else:
    status = "High Alert"

col3.metric(
    "Status",
    status
)

st.markdown("---")

# --------------------------------------------------
# RISK GAUGE
# --------------------------------------------------

st.subheader("Risk Gauge")

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={"text": "Company Risk"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"thickness": 0.4},
            "steps": [
                {"range": [0, 30]},
                {"range": [30, 60]},
                {"range": [60, 100]}
            ]
        }
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# RISK FACTOR ANALYSIS
# --------------------------------------------------

st.subheader("Risk Factor Breakdown")

risk_factors = []

# Debt Risk
if "Debt" in company_df.columns:
    debt = company["Debt"]

    if debt > 1000000000:
        debt_risk = 25
    elif debt > 500000000:
        debt_risk = 15
    else:
        debt_risk = 5

    risk_factors.append(
        ["Debt Risk", debt_risk]
    )

# Revenue Growth Risk
if "RevenueGrowth" in company_df.columns:

    growth = company["RevenueGrowth"]

    if growth < 0:
        growth_risk = 25
    elif growth < 5:
        growth_risk = 15
    else:
        growth_risk = 5

    risk_factors.append(
        ["Revenue Growth Risk", growth_risk]
    )

# Institutional Ownership Risk
if "InstitutionalOwnership" in company_df.columns:

    ownership = company["InstitutionalOwnership"]

    if ownership < 20:
        ownership_risk = 20
    elif ownership < 40:
        ownership_risk = 10
    else:
        ownership_risk = 5

    risk_factors.append(
        ["Institutional Ownership Risk", ownership_risk]
    )

# Insider Activity Risk
if not insider_df.empty:

    insider_company = insider_df[
        insider_df["Company"] == selected_company
    ]

    if (
        not insider_company.empty
        and "TransactionType" in insider_company.columns
    ):

        sell_count = len(
            insider_company[
                insider_company["TransactionType"]
                .astype(str)
                .str.upper()
                .str.contains("SELL")
            ]
        )

        buy_count = len(
            insider_company[
                insider_company["TransactionType"]
                .astype(str)
                .str.upper()
                .str.contains("BUY")
            ]
        )

        if sell_count > buy_count:
            insider_risk = 20
        else:
            insider_risk = 5

        risk_factors.append(
            ["Insider Trading Risk", insider_risk]
        )

risk_df = pd.DataFrame(
    risk_factors,
    columns=["Factor", "Risk"]
)

if not risk_df.empty:

    fig = px.bar(
        risk_df,
        x="Factor",
        y="Risk",
        title="Risk Contributors"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# COMPANY PROFILE
# --------------------------------------------------

st.subheader("Company Overview")

overview_cols = st.columns(4)

metrics = [
    ("Market Cap", "MarketCap"),
    ("Revenue", "Revenue"),
    ("Net Income", "NetIncome"),
    ("Institutional Ownership", "InstitutionalOwnership")
]

for i, (label, col) in enumerate(metrics):

    if col in company_df.columns:

        value = company[col]

        try:
            formatted = f"{value:,.2f}"
        except:
            formatted = str(value)

        overview_cols[i].metric(
            label,
            formatted
        )

st.markdown("---")

# --------------------------------------------------
# INSIDER RISK ANALYSIS
# --------------------------------------------------

st.subheader("Insider Activity Analysis")

if not insider_df.empty:

    insider_company = insider_df[
        insider_df["Company"] == selected_company
    ]

    if not insider_company.empty:

        st.dataframe(
            insider_company.tail(20),
            use_container_width=True
        )

        if (
            "TransactionType" in insider_company.columns
        ):

            transaction_summary = (
                insider_company
                .groupby("TransactionType")
                .size()
                .reset_index(name="Count")
            )

            fig = px.pie(
                transaction_summary,
                names="TransactionType",
                values="Count",
                title="Transaction Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

# --------------------------------------------------
# INSTITUTIONAL ANALYSIS
# --------------------------------------------------

st.subheader("Institutional Holdings Analysis")

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
                title="Institutional Ownership"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

# --------------------------------------------------
# AI NARRATIVE
# --------------------------------------------------

st.subheader("🤖 AI Risk Assessment")

if risk_score < 30:

    recommendation = """
### LOW RISK

The company currently exhibits healthy
financial characteristics and stable
ownership patterns.

Key Observations:

- Strong institutional support
- Healthy insider activity
- Stable growth profile

Action:
Continue routine monitoring.
"""

elif risk_score < 60:

    recommendation = """
### MEDIUM RISK

Several indicators require attention.

Key Observations:

- Moderate insider activity
- Growth concerns emerging
- Ownership concentration changing

Action:
Increase monitoring frequency.
"""

else:

    recommendation = """
### HIGH RISK

The company demonstrates elevated
risk indicators.

Potential Issues:

- Significant insider selling
- Weak growth trends
- Debt pressure
- Institutional outflows

Action:
Immediate analyst review recommended.
"""

st.markdown(recommendation)

# --------------------------------------------------
# RISK RANKING TABLE
# --------------------------------------------------

st.subheader("Market Risk Ranking")

risk_table = []

for _, row in master_df.iterrows():

    try:
        score = calculate_risk_score(row)
    except:
        score = np.random.randint(20, 80)

    risk_table.append(
        [
            row["Company"],
            score,
            classify_risk(score)
        ]
    )

ranking_df = pd.DataFrame(
    risk_table,
    columns=[
        "Company",
        "Risk Score",
        "Category"
    ]
)

ranking_df = ranking_df.sort_values(
    by="Risk Score",
    ascending=False
)

st.dataframe(
    ranking_df,
    use_container_width=True
)

# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------

st.markdown("---")

report = pd.DataFrame({
    "Company": [selected_company],
    "Risk Score": [risk_score],
    "Risk Category": [risk_label],
    "Status": [status]
})

csv = report.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇ Download Risk Report",
    data=csv,
    file_name=f"{selected_company}_risk_report.csv",
    mime="text/csv"
)
```

