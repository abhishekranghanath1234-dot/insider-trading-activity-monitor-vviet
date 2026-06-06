```python id="ai_alerts_page_001"
# pages/9_AI_Alerts.py

import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

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
    page_title="AI Alerts",
    page_icon="🔔",
    layout="wide"
)

st.title("🔔 AI Smart Money Alerts Engine")
st.markdown(
    "Real-time AI-generated alerts for insider trading, "
    "institutional flows, and risk anomalies."
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

if master_df.empty or insider_df.empty:
    st.error("Required datasets are missing.")
    st.stop()

# --------------------------------------------------
# ALERT CONFIG
# --------------------------------------------------

st.sidebar.header("Alert Settings")

risk_threshold = st.sidebar.slider(
    "Risk Score Threshold",
    min_value=0,
    max_value=100,
    value=60
)

buy_spike_threshold = st.sidebar.slider(
    "Insider Buy Spike (%)",
    min_value=10,
    max_value=200,
    value=50
)

sell_spike_threshold = st.sidebar.slider(
    "Insider Sell Spike (%)",
    min_value=10,
    max_value=200,
    value=50
)

# --------------------------------------------------
# ALERT GENERATION
# --------------------------------------------------

alerts = []

# Ensure datetime
if "TransactionDate" in insider_df.columns:
    insider_df["TransactionDate"] = pd.to_datetime(
        insider_df["TransactionDate"],
        errors="coerce"
    )

# Group by company
for company in master_df["Company"].dropna().unique():

    company_master = master_df[
        master_df["Company"] == company
    ]

    if company_master.empty:
        continue

    row = company_master.iloc[0]

    try:
        risk_score = calculate_risk_score(row)
    except:
        risk_score = 50

    risk_label = classify_risk(risk_score)

    insider_company = insider_df[
        insider_df["Company"] == company
    ] if "Company" in insider_df.columns else pd.DataFrame()

    buy_count = 0
    sell_count = 0

    if not insider_company.empty:

        buy_count = len(
            insider_company[
                insider_company["TransactionType"]
                .astype(str)
                .str.upper()
                .str.contains("BUY")
            ]
        )

        sell_count = len(
            insider_company[
                insider_company["TransactionType"]
                .astype(str)
                .str.upper()
                .str.contains("SELL")
            ]
        )

    # --------------------------------------------------
    # ALERT LOGIC
    # --------------------------------------------------

    if risk_score >= risk_threshold:

        alerts.append({
            "Company": company,
            "Type": "HIGH RISK",
            "Severity": "RED",
            "Message": f"Risk score {risk_score:.1f} exceeds threshold",
            "RiskScore": risk_score
        })

    if buy_count >= buy_spike_threshold:

        alerts.append({
            "Company": company,
            "Type": "INSIDER BUY SPIKE",
            "Severity": "GREEN",
            "Message": f"Unusual insider buying activity detected ({buy_count} buys)",
            "RiskScore": risk_score
        })

    if sell_count >= sell_spike_threshold:

        alerts.append({
            "Company": company,
            "Type": "INSIDER SELL SPIKE",
            "Severity": "ORANGE",
            "Message": f"High insider selling pressure ({sell_count} sells)",
            "RiskScore": risk_score
        })

    # Institutional anomaly (simple heuristic)
    if "InstitutionalOwnership" in row:

        if pd.notna(row["InstitutionalOwnership"]):

            if row["InstitutionalOwnership"] < 15:

                alerts.append({
                    "Company": company,
                    "Type": "LOW INSTITUTIONAL SUPPORT",
                    "Severity": "ORANGE",
                    "Message": "Very low institutional ownership detected",
                    "RiskScore": risk_score
                })

# --------------------------------------------------
# ALERT SUMMARY
# --------------------------------------------------

st.subheader("📊 Alert Summary")

total_alerts = len(alerts)

red_alerts = len([a for a in alerts if a["Severity"] == "RED"])
green_alerts = len([a for a in alerts if a["Severity"] == "GREEN"])
orange_alerts = len([a for a in alerts if a["Severity"] == "ORANGE"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Alerts", total_alerts)
col2.metric("🔴 High Risk", red_alerts)
col3.metric("🟢 Buy Signals", green_alerts)
col4.metric("🟠 Warning Signals", orange_alerts)

st.markdown("---")

# --------------------------------------------------
# ALERT FEED
# --------------------------------------------------

st.subheader("🚨 Live Alert Feed")

if not alerts:
    st.success("No alerts triggered at current thresholds.")
else:

    alerts_df = pd.DataFrame(alerts)

    severity_color = {
        "RED": "🔴",
        "ORANGE": "🟠",
        "GREEN": "🟢"
    }

    alerts_df["SeverityIcon"] = alerts_df["Severity"].map(severity_color)

    for _, alert in alerts_df.sort_values(
        by="RiskScore",
        ascending=False
    ).iterrows():

        st.markdown(
            f"""
            ### {alert['SeverityIcon']} {alert['Type']}
            **Company:** {alert['Company']}

            **Message:** {alert['Message']}

            **Risk Score:** {alert['RiskScore']:.1f}
            """
        )

        st.markdown("---")

# --------------------------------------------------
# ALERT ANALYTICS
# --------------------------------------------------

if alerts:

    st.subheader("📈 Alert Analytics")

    chart_df = pd.DataFrame(alerts)

    fig = px.bar(
        chart_df,
        x="Type",
        color="Severity",
        title="Alert Distribution by Type"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(
        chart_df,
        x="RiskScore",
        nbins=20,
        title="Risk Score Distribution of Alerts"
    )

    st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# TOP ALERT COMPANIES
# --------------------------------------------------

if alerts:

    st.subheader("🏢 Companies with Most Alerts")

    company_alerts = (
        pd.DataFrame(alerts)
        .groupby("Company")
        .size()
        .reset_index(name="AlertCount")
        .sort_values("AlertCount", ascending=False)
    )

    st.dataframe(company_alerts, use_container_width=True)

# --------------------------------------------------
# AI ALERT SUMMARY
# --------------------------------------------------

st.subheader("🤖 AI Alert Summary")

if total_alerts == 0:

    summary = """
### SYSTEM STATUS: NORMAL

No abnormal market activity detected
based on current thresholds.

- Insider activity within normal range
- Risk scores stable
- No institutional anomalies
"""

elif red_alerts > 0:

    summary = f"""
### SYSTEM STATUS: HIGH ALERT

{red_alerts} high-risk conditions detected.

Immediate attention recommended.

Key risks:

- Elevated risk scores
- Potential insider activity concerns
- Market instability signals

Action:
Review flagged companies immediately.
"""

else:

    summary = f"""
### SYSTEM STATUS: MONITORING

System has detected {total_alerts} alerts.

Most signals are moderate risk.

Recommended:

- Continue monitoring
- Review insider activity trends
- Adjust thresholds if needed
"""

st.markdown(summary)

# --------------------------------------------------
# DOWNLOAD ALERTS
# --------------------------------------------------

st.markdown("---")

if alerts:

    alerts_df = pd.DataFrame(alerts)

    csv = alerts_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download Alerts Report",
        data=csv,
        file_name="ai_alerts_report.csv",
        mime="text/csv"
    )
```
