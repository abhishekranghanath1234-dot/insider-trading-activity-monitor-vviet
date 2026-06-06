 # pages/Fraud_Detection.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest

from utils.data_loader import load_master_data

st.set_page_config(
    page_title="Fraud Detection",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 Fraud Detection & Anomaly Analytics")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = load_master_data()

st.sidebar.header("Filters")

# --------------------------------------------------
# SELECT NUMERIC FEATURES
# --------------------------------------------------

possible_features = [
    "market_value",
    "conviction_score",
    "shares_owned",
    "shares_change",
    "ownership_percentage"
]

features = [c for c in possible_features if c in df.columns]

if len(features) < 2:
    st.error(
        "Not enough numeric columns found for anomaly detection."
    )
    st.stop()

selected_features = st.sidebar.multiselect(
    "Select Features",
    features,
    default=features[:3]
)

# --------------------------------------------------
# CLEAN DATA
# --------------------------------------------------

anomaly_df = df[selected_features].copy()

anomaly_df = anomaly_df.replace(
    [np.inf, -np.inf],
    np.nan
)

anomaly_df = anomaly_df.fillna(
    anomaly_df.median(numeric_only=True)
)

# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = IsolationForest(
    contamination=0.03,
    random_state=42
)

predictions = model.fit_predict(
    anomaly_df
)

scores = model.decision_function(
    anomaly_df
)

df["anomaly"] = predictions
df["anomaly_score"] = scores

fraud_df = df[
    df["anomaly"] == -1
]

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

st.subheader("Detection Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{len(df):,}"
)

col2.metric(
    "Anomalies Found",
    f"{len(fraud_df):,}"
)

col3.metric(
    "Fraud Rate",
    f"{(len(fraud_df)/len(df))*100:.2f}%"
)

col4.metric(
    "Features Used",
    len(selected_features)
)

# --------------------------------------------------
# ANOMALY DISTRIBUTION
# --------------------------------------------------

st.subheader("Anomaly Distribution")

chart_df = pd.DataFrame({
    "Category": ["Normal", "Anomaly"],
    "Count": [
        len(df[df["anomaly"] == 1]),
        len(df[df["anomaly"] == -1])
    ]
})

fig = px.pie(
    chart_df,
    names="Category",
    values="Count",
    title="Fraud vs Normal Records"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# ANOMALY SCORE HISTOGRAM
# --------------------------------------------------

st.subheader("Anomaly Score Distribution")

fig2 = px.histogram(
    df,
    x="anomaly_score",
    nbins=50,
    title="Isolation Forest Score Distribution"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# --------------------------------------------------
# SCATTER ANALYSIS
# --------------------------------------------------

if len(selected_features) >= 2:

    st.subheader("Fraud Cluster Visualization")

    fig3 = px.scatter(
        df,
        x=selected_features[0],
        y=selected_features[1],
        color=df["anomaly"].astype(str),
        hover_data=["anomaly_score"],
        title="Anomaly Clusters"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# --------------------------------------------------
# HIGH-RISK RECORDS
# --------------------------------------------------

st.subheader("High Risk Records")

display_cols = []

preferred_cols = [
    "company_name",
    "issuer_name",
    "market_value",
    "conviction_score",
    "anomaly_score"
]

for col in preferred_cols:
    if col in fraud_df.columns:
        display_cols.append(col)

if len(display_cols) > 0:
    st.dataframe(
        fraud_df[display_cols]
        .sort_values(
            "anomaly_score",
            ascending=True
        ),
        use_container_width=True
    )
else:
    st.dataframe(
        fraud_df.head(100),
        use_container_width=True
    )

# --------------------------------------------------
# TOP SUSPICIOUS COMPANIES
# --------------------------------------------------

if "company_name" in fraud_df.columns:

    st.subheader("Most Suspicious Companies")

    suspicious = (
        fraud_df.groupby("company_name")
        .size()
        .reset_index(name="anomaly_count")
        .sort_values(
            "anomaly_count",
            ascending=False
        )
        .head(20)
    )

    fig4 = px.bar(
        suspicious,
        x="company_name",
        y="anomaly_count",
        title="Top Suspicious Companies"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# --------------------------------------------------
# AI INSIGHTS
# --------------------------------------------------

st.subheader("🤖 AI Insights")

fraud_percent = (
    len(fraud_df) / len(df)
) * 100

st.info(
    f"""
    • Total records analyzed: {len(df):,}

    • Potential anomalies detected: {len(fraud_df):,}

    • Estimated anomaly rate: {fraud_percent:.2f}%

    • Isolation Forest identified records that differ
      significantly from normal institutional behavior.

    • Unusual conviction scores combined with large
      position changes may indicate abnormal activity.

    • Review high-risk entities before making
      investment decisions.
    """
)

# --------------------------------------------------
# DOWNLOAD RESULTS
# --------------------------------------------------

st.subheader("Export Results")

csv = fraud_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "📥 Download Fraud Report",
    csv,
    "fraud_detection_report.csv",
    "text/csv"
)
