```python
# pages/7_Fraud_Detection.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from utils.data_loader import (
    load_master_data,
    load_insider_data,
    load_holdings_data
)

st.set_page_config(
    page_title="Fraud Detection",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 AI Fraud Detection Engine")
st.markdown(
    "Detect suspicious insider trading activity, "
    "ownership anomalies, and abnormal corporate behavior."
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

if insider_df.empty:
    st.error("Insider transaction dataset not available.")
    st.stop()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Detection Settings")

contamination = st.sidebar.slider(
    "Anomaly Sensitivity",
    min_value=0.01,
    max_value=0.25,
    value=0.05,
    step=0.01
)

selected_company = "All Companies"

if "Company" in insider_df.columns:
    company_options = ["All Companies"] + sorted(
        insider_df["Company"].dropna().unique().tolist()
    )

    selected_company = st.sidebar.selectbox(
        "Company Filter",
        company_options
    )

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

analysis_df = insider_df.copy()

if (
    selected_company != "All Companies"
    and "Company" in analysis_df.columns
):
    analysis_df = analysis_df[
        analysis_df["Company"] == selected_company
    ]

if analysis_df.empty:
    st.warning("No records found.")
    st.stop()

# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

working_df = analysis_df.copy()

numeric_features = []

candidate_columns = [
    "Shares",
    "TransactionValue",
    "Price",
    "OwnershipPercent",
    "MarketCap"
]

for col in candidate_columns:
    if col in working_df.columns:
        working_df[col] = pd.to_numeric(
            working_df[col],
            errors="coerce"
        )
        numeric_features.append(col)

if len(numeric_features) == 0:
    st.error(
        "No numeric columns available for anomaly detection."
    )
    st.stop()

working_df = working_df.dropna(
    subset=numeric_features
)

if len(working_df) < 10:
    st.warning(
        "Not enough records for reliable anomaly detection."
    )
    st.stop()

# --------------------------------------------------
# MODEL
# --------------------------------------------------

scaler = StandardScaler()

X = scaler.fit_transform(
    working_df[numeric_features]
)

model = IsolationForest(
    contamination=contamination,
    random_state=42,
    n_estimators=200
)

model.fit(X)

predictions = model.predict(X)

scores = model.decision_function(X)

working_df["AnomalyFlag"] = predictions
working_df["AnomalyScore"] = scores

working_df["RiskLabel"] = np.where(
    working_df["AnomalyFlag"] == -1,
    "Suspicious",
    "Normal"
)

# --------------------------------------------------
# METRICS
# --------------------------------------------------

total_records = len(working_df)

suspicious_records = len(
    working_df[
        working_df["RiskLabel"] == "Suspicious"
    ]
)

fraud_rate = (
    suspicious_records / total_records
) * 100

col1, col2, col3 = st.columns(3)

col1.metric(
    "Transactions Analysed",
    f"{total_records:,}"
)

col2.metric(
    "Suspicious Records",
    f"{suspicious_records:,}"
)

col3.metric(
    "Fraud Risk %",
    f"{fraud_rate:.2f}%"
)

st.markdown("---")

# --------------------------------------------------
# FRAUD STATUS
# --------------------------------------------------

if fraud_rate < 3:
    st.success(
        "🟢 Low Fraud Risk Environment"
    )
elif fraud_rate < 10:
    st.warning(
        "🟠 Moderate Fraud Risk Environment"
    )
else:
    st.error(
        "🔴 High Fraud Risk Environment"
    )

# --------------------------------------------------
# ANOMALY DISTRIBUTION
# --------------------------------------------------

st.subheader("Anomaly Distribution")

fig = px.histogram(
    working_df,
    x="AnomalyScore",
    color="RiskLabel",
    nbins=40,
    title="Anomaly Score Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# SCATTER ANALYSIS
# --------------------------------------------------

if len(numeric_features) >= 2:

    st.subheader(
        "Suspicious Transaction Mapping"
    )

    fig = px.scatter(
        working_df,
        x=numeric_features[0],
        y=numeric_features[1],
        color="RiskLabel",
        hover_data=working_df.columns,
        title="Detected Outliers"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# TOP SUSPICIOUS RECORDS
# --------------------------------------------------

st.subheader(
    "Top Suspicious Transactions"
)

fraud_df = working_df[
    working_df["RiskLabel"] == "Suspicious"
].copy()

fraud_df = fraud_df.sort_values(
    by="AnomalyScore"
)

if not fraud_df.empty:

    st.dataframe(
        fraud_df.head(50),
        use_container_width=True
    )

else:
    st.info(
        "No suspicious records detected."
    )

# --------------------------------------------------
# COMPANY RISK TABLE
# --------------------------------------------------

if "Company" in working_df.columns:

    st.subheader(
        "Company Fraud Risk Ranking"
    )

    company_risk = (
        working_df
        .groupby("Company")
        .agg(
            TotalTransactions=("Company", "count"),
            SuspiciousCount=(
                "RiskLabel",
                lambda x: (
                    x == "Suspicious"
                ).sum()
            )
        )
        .reset_index()
    )

    company_risk["RiskRate"] = (
        company_risk["SuspiciousCount"]
        /
        company_risk["TotalTransactions"]
    ) * 100

    company_risk = company_risk.sort_values(
        by="RiskRate",
        ascending=False
    )

    st.dataframe(
        company_risk,
        use_container_width=True
    )

    fig = px.bar(
        company_risk.head(20),
        x="Company",
        y="RiskRate",
        title="Top Risk Companies"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# EXECUTIVE ANALYSIS
# --------------------------------------------------

if "InsiderName" in working_df.columns:

    st.subheader(
        "High-Risk Insider Ranking"
    )

    insider_risk = (
        working_df
        .groupby("InsiderName")
        .agg(
            Transactions=("InsiderName", "count"),
            Suspicious=(
                "RiskLabel",
                lambda x: (
                    x == "Suspicious"
                ).sum()
            )
        )
        .reset_index()
    )

    insider_risk["RiskRate"] = (
        insider_risk["Suspicious"]
        /
        insider_risk["Transactions"]
    ) * 100

    insider_risk = insider_risk.sort_values(
        by="RiskRate",
        ascending=False
    )

    st.dataframe(
        insider_risk.head(25),
        use_container_width=True
    )

# --------------------------------------------------
# AI FRAUD SUMMARY
# --------------------------------------------------

st.subheader(
    "🤖 AI Fraud Assessment"
)

if fraud_rate < 3:

    summary = f"""
### Overall Assessment: LOW RISK

The anomaly detection engine analyzed
{total_records:,} insider transactions.

Only {suspicious_records:,} transactions
were classified as anomalous.

Current trading activity appears normal.

Recommended Actions:

- Continue monitoring
- Weekly risk review
- Track large insider purchases
"""

elif fraud_rate < 10:

    summary = f"""
### Overall Assessment: MODERATE RISK

The engine detected
{suspicious_records:,} unusual transactions.

Several trading patterns differ from
historical behavior.

Recommended Actions:

- Investigate large transactions
- Monitor executive activity
- Review ownership changes
"""

else:

    summary = f"""
### Overall Assessment: HIGH RISK

The AI engine detected a significant
number of suspicious transactions.

Potential warning signs:

- Abnormal trading volumes
- Unusual insider behavior
- Ownership concentration shifts

Immediate review recommended.
"""

st.markdown(summary)

# --------------------------------------------------
# DOWNLOAD RESULTS
# --------------------------------------------------

st.markdown("---")

csv = working_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇ Download Fraud Detection Report",
    data=csv,
    file_name="fraud_detection_report.csv",
    mime="text/csv"
)
```
