 # pages/risk_scoring.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest

from utils.data_loader import load_master_data

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Risk Scoring Engine",
    page_icon="⚠️",
    layout="wide"
)

st.title("⚠️ AI Risk Scoring Engine")
st.caption(
    "Institutional Risk Assessment & Portfolio Intelligence"
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def get_data():
    return load_master_data()

df = get_data()

# =========================================================
# COMPANY COLUMN DETECTION
# =========================================================

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
    st.error("No company column found.")
    st.stop()

# =========================================================
# NUMERIC FEATURES
# =========================================================

numeric_cols = (
    df.select_dtypes(include=np.number)
    .columns
    .tolist()
)

if len(numeric_cols) < 2:
    st.error(
        "At least 2 numeric columns are required."
    )
    st.stop()

# =========================================================
# FEATURE SELECTION
# =========================================================

st.sidebar.header("Risk Settings")

selected_features = st.sidebar.multiselect(
    "Select Risk Factors",
    numeric_cols,
    default=numeric_cols[:min(5, len(numeric_cols))]
)

if len(selected_features) < 2:
    st.warning(
        "Please select at least 2 features."
    )
    st.stop()

# =========================================================
# CLEAN DATA
# =========================================================

working_df = df.copy()

working_df[selected_features] = (
    working_df[selected_features]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
)

working_df[selected_features] = (
    working_df[selected_features]
    .fillna(
        working_df[selected_features]
        .median()
    )
)

# =========================================================
# COMPANY AGGREGATION
# =========================================================

risk_df = (
    working_df
    .groupby(company_col)[selected_features]
    .mean()
    .reset_index()
)

# =========================================================
# NORMALIZATION
# =========================================================

scaler = MinMaxScaler()

risk_df[selected_features] = (
    scaler.fit_transform(
        risk_df[selected_features]
    )
)

# =========================================================
# ANOMALY DETECTION
# =========================================================

iso = IsolationForest(
    contamination=0.05,
    random_state=42
)

risk_df["anomaly"] = iso.fit_predict(
    risk_df[selected_features]
)

risk_df["anomaly_score"] = (
    iso.decision_function(
        risk_df[selected_features]
    )
)

# =========================================================
# RISK SCORE CALCULATION
# =========================================================

risk_df["risk_score"] = (
    risk_df[selected_features]
    .mean(axis=1)
)

risk_df["risk_score"] += (
    (risk_df["anomaly"] == -1)
    .astype(int)
    * 0.20
)

risk_df["risk_score"] = (
    risk_df["risk_score"] * 100
)

risk_df["risk_score"] = (
    risk_df["risk_score"]
    .clip(0, 100)
)

# =========================================================
# RISK CATEGORY
# =========================================================

def classify_risk(score):

    if score >= 75:
        return "High Risk"

    elif score >= 50:
        return "Medium Risk"

    else:
        return "Low Risk"

risk_df["risk_category"] = (
    risk_df["risk_score"]
    .apply(classify_risk)
)

# =========================================================
# KPI SECTION
# =========================================================

st.subheader("📊 Portfolio Risk Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    len(risk_df)
)

c2.metric(
    "Average Risk",
    f"{risk_df['risk_score'].mean():.2f}"
)

c3.metric(
    "Highest Risk",
    f"{risk_df['risk_score'].max():.2f}"
)

c4.metric(
    "Anomalies",
    len(
        risk_df[
            risk_df["anomaly"] == -1
        ]
    )
)

# =========================================================
# RISK DISTRIBUTION
# =========================================================

st.subheader("📈 Risk Score Distribution")

fig1 = px.histogram(
    risk_df,
    x="risk_score",
    nbins=30,
    title="Risk Score Distribution"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =========================================================
# RISK CATEGORY PIE CHART
# =========================================================

st.subheader("🥧 Risk Categories")

category_df = (
    risk_df["risk_category"]
    .value_counts()
    .reset_index()
)

category_df.columns = [
    "Category",
    "Count"
]

fig2 = px.pie(
    category_df,
    names="Category",
    values="Count",
    title="Risk Classification"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================================
# TOP HIGH-RISK COMPANIES
# =========================================================

st.subheader("🚨 Highest Risk Companies")

top_risk = (
    risk_df
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(20)
)

fig3 = px.bar(
    top_risk,
    x=company_col,
    y="risk_score",
    color="risk_category",
    title="Top Risk Companies"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================================
# FEATURE HEATMAP
# =========================================================

st.subheader("🔥 Risk Factor Correlation")

corr = (
    risk_df[selected_features]
    .corr()
)

heatmap = go.Figure(
    data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns
    )
)

heatmap.update_layout(
    title="Risk Factor Correlation Matrix"
)

st.plotly_chart(
    heatmap,
    use_container_width=True
)

# =========================================================
# FEATURE CONTRIBUTION
# =========================================================

st.subheader("📌 Average Risk Factor Contribution")

contrib_df = pd.DataFrame({
    "Feature": selected_features,
    "Average Value":
    risk_df[selected_features]
    .mean()
    .values
})

fig4 = px.bar(
    contrib_df,
    x="Feature",
    y="Average Value",
    title="Average Risk Contribution"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# =========================================================
# COMPANY EXPLORER
# =========================================================

st.subheader("🔍 Company Risk Explorer")

selected_company = st.selectbox(
    "Select Company",
    sorted(
        risk_df[company_col]
        .astype(str)
        .unique()
    )
)

company_data = risk_df[
    risk_df[company_col]
    == selected_company
]

st.dataframe(
    company_data,
    use_container_width=True
)

# =========================================================
# RISK RANKINGS
# =========================================================

st.subheader("🏆 Risk Rankings")

ranking_df = (
    risk_df
    .sort_values(
        "risk_score",
        ascending=False
    )
)

ranking_df["Rank"] = range(
    1,
    len(ranking_df) + 1
)

st.dataframe(
    ranking_df[
        [
            "Rank",
            company_col,
            "risk_score",
            "risk_category"
        ]
    ],
    use_container_width=True
)

# =========================================================
# AI INSIGHTS
# =========================================================

st.subheader("🤖 AI Insights")

high_risk = len(
    risk_df[
        risk_df["risk_category"]
        == "High Risk"
    ]
)

medium_risk = len(
    risk_df[
        risk_df["risk_category"]
        == "Medium Risk"
    ]
)

low_risk = len(
    risk_df[
        risk_df["risk_category"]
        == "Low Risk"
    ]
)

top_company = (
    risk_df.sort_values(
        "risk_score",
        ascending=False
    )
    .iloc[0][company_col]
)

st.info(f"""
Companies Analyzed: {len(risk_df)}

High Risk Companies: {high_risk}

Medium Risk Companies: {medium_risk}

Low Risk Companies: {low_risk}

Highest Risk Entity:
{top_company}

Risk scoring combines:

• Selected Risk Factors

• Statistical Normalization

• Isolation Forest Anomaly Detection

• Multi-Factor Composite Scoring

Companies with higher risk scores
should be reviewed further for
portfolio concentration, ownership
changes, conviction shifts, and
abnormal institutional behavior.
""")

# =========================================================
# DOWNLOAD REPORT
# =========================================================

st.subheader("📥 Export Risk Report")

csv = risk_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Risk Report",
    csv,
    "risk_scoring_report.csv",
    "text/csv"
)
