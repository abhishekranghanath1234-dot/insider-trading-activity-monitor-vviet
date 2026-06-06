 # pages/AI_Alerts.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest

from utils.data_loader import load_master_data

# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------

st.set_page_config(
    page_title="AI Alerts",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 AI Alerts Center")
st.caption(
    "Real-Time Institutional Intelligence & Alert Engine"
)

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------

@st.cache_data
def get_data():
    return load_master_data()

df = get_data()

# -----------------------------------------------------
# COMPANY COLUMN DETECTION
# -----------------------------------------------------

company_col = None

for col in [
    "company_name",
    "issuer_name",
    "company",
    "issuer"
]:
    if col in df.columns:
        company_col = col
        break

if company_col is None:
    st.error("Company column not found.")
    st.stop()

# -----------------------------------------------------
# NUMERIC CLEANUP
# -----------------------------------------------------

numeric_cols = df.select_dtypes(
    include=np.number
).columns.tolist()

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df[numeric_cols] = (
    df[numeric_cols]
    .replace([np.inf, -np.inf], np.nan)
    .fillna(0)
)

# -----------------------------------------------------
# ANOMALY DETECTION
# -----------------------------------------------------

features = []

for col in [
    "market_value",
    "conviction_score",
    "shares_owned",
    "shares_change",
    "ownership_percentage"
]:
    if col in df.columns:
        features.append(col)

if len(features) >= 2:

    iso = IsolationForest(
        contamination=0.03,
        random_state=42
    )

    df["anomaly_flag"] = iso.fit_predict(
        df[features]
    )

    df["anomaly_score"] = (
        iso.decision_function(
            df[features]
        )
    )

else:

    df["anomaly_flag"] = 1
    df["anomaly_score"] = 0

# -----------------------------------------------------
# ALERT ENGINE
# -----------------------------------------------------

alerts = []

for _, row in df.iterrows():

    company = row.get(company_col, "Unknown")

    # High Conviction Alert
    if (
        "conviction_score" in df.columns
        and row.get("conviction_score", 0) > 85
    ):
        alerts.append({
            "Company": company,
            "Alert Type":
            "High Conviction",
            "Priority": "High",
            "Message":
            "Institutional conviction extremely strong."
        })

    # Ownership Concentration
    if (
        "ownership_percentage" in df.columns
        and row.get(
            "ownership_percentage",
            0
        ) > 20
    ):
        alerts.append({
            "Company": company,
            "Alert Type":
            "Ownership Concentration",
            "Priority": "Medium",
            "Message":
            "Institutional ownership highly concentrated."
        })

    # Large Position Increase
    if (
        "shares_change" in df.columns
        and row.get(
            "shares_change",
            0
        ) > 100000
    ):
        alerts.append({
            "Company": company,
            "Alert Type":
            "Accumulation Signal",
            "Priority": "High",
            "Message":
            "Large institutional buying activity detected."
        })

    # Large Position Reduction
    if (
        "shares_change" in df.columns
        and row.get(
            "shares_change",
            0
        ) < -100000
    ):
        alerts.append({
            "Company": company,
            "Alert Type":
            "Distribution Signal",
            "Priority": "High",
            "Message":
            "Large institutional selling activity detected."
        })

    # Anomaly Alert
    if row["anomaly_flag"] == -1:

        alerts.append({
            "Company": company,
            "Alert Type":
            "Anomaly Detected",
            "Priority": "Critical",
            "Message":
            "Unusual behavior identified by AI engine."
        })

# -----------------------------------------------------
# ALERT DATAFRAME
# -----------------------------------------------------

alerts_df = pd.DataFrame(alerts)

if alerts_df.empty:

    st.success(
        "No significant alerts detected."
    )
    st.stop()

# -----------------------------------------------------
# SUMMARY KPIs
# -----------------------------------------------------

st.subheader("📊 Alert Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Alerts",
    len(alerts_df)
)

c2.metric(
    "Critical",
    len(
        alerts_df[
            alerts_df["Priority"]
            == "Critical"
        ]
    )
)

c3.metric(
    "High",
    len(
        alerts_df[
            alerts_df["Priority"]
            == "High"
        ]
    )
)

c4.metric(
    "Medium",
    len(
        alerts_df[
            alerts_df["Priority"]
            == "Medium"
        ]
    )
)

# -----------------------------------------------------
# ALERT BREAKDOWN
# -----------------------------------------------------

st.subheader("Alert Categories")

alert_counts = (
    alerts_df["Alert Type"]
    .value_counts()
    .reset_index()
)

alert_counts.columns = [
    "Alert Type",
    "Count"
]

fig1 = px.bar(
    alert_counts,
    x="Alert Type",
    y="Count",
    color="Alert Type",
    title="AI Alert Distribution"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# -----------------------------------------------------
# PRIORITY BREAKDOWN
# -----------------------------------------------------

st.subheader("Priority Distribution")

priority_df = (
    alerts_df["Priority"]
    .value_counts()
    .reset_index()
)

priority_df.columns = [
    "Priority",
    "Count"
]

fig2 = px.pie(
    priority_df,
    names="Priority",
    values="Count",
    title="Alert Priority Levels"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# -----------------------------------------------------
# FILTERS
# -----------------------------------------------------

st.subheader("🔍 Alert Explorer")

priority_filter = st.multiselect(
    "Filter Priority",
    sorted(
        alerts_df["Priority"]
        .unique()
    ),
    default=sorted(
        alerts_df["Priority"]
        .unique()
    )
)

filtered_alerts = alerts_df[
    alerts_df["Priority"]
    .isin(priority_filter)
]

st.dataframe(
    filtered_alerts,
    use_container_width=True,
    height=500
)

# -----------------------------------------------------
# TOP ALERT COMPANIES
# -----------------------------------------------------

st.subheader("🏆 Most Alerted Companies")

top_alerts = (
    alerts_df.groupby("Company")
    .size()
    .reset_index(name="Alert Count")
    .sort_values(
        "Alert Count",
        ascending=False
    )
    .head(20)
)

fig3 = px.bar(
    top_alerts,
    x="Company",
    y="Alert Count",
    title="Companies Generating Most Alerts"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# -----------------------------------------------------
# AI INSIGHTS
# -----------------------------------------------------

st.subheader("🤖 AI Insights")

critical_count = len(
    alerts_df[
        alerts_df["Priority"]
        == "Critical"
    ]
)

high_count = len(
    alerts_df[
        alerts_df["Priority"]
        == "High"
    ]
)

st.info(f"""
Total AI alerts generated: {len(alerts_df)}

Critical alerts detected: {critical_count}

High-priority alerts detected: {high_count}

The AI engine continuously monitors:

• Conviction Score Changes

• Institutional Accumulation

• Institutional Distribution

• Ownership Concentration

• Statistical Anomalies

Companies generating repeated alerts
may require additional due diligence
and deeper institutional analysis.
""")

# -----------------------------------------------------
# DOWNLOAD REPORT
# -----------------------------------------------------

st.subheader("📥 Export Alerts")

csv = alerts_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download AI Alerts Report",
    data=csv,
    file_name="AI_Alerts_Report.csv",
    mime="text/csv"
)
