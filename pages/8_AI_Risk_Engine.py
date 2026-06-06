 # pages/_AI_Risk_Engine.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest

from utils.data_loader import load_master_data

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Risk Engine",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Risk Engine")
st.caption("Predictive Institutional Risk & Opportunity Scoring")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def get_data():
    return load_master_data()

df = get_data()

# --------------------------------------------------
# COMPANY COLUMN DETECTION
# --------------------------------------------------

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

# --------------------------------------------------
# REQUIRED FEATURES
# --------------------------------------------------

feature_candidates = [
    "market_value",
    "conviction_score",
    "shares_owned",
    "shares_change",
    "ownership_percentage"
]

features = [
    col for col in feature_candidates
    if col in df.columns
]

if len(features) < 2:
    st.error("Not enough numerical features available.")
    st.stop()

# --------------------------------------------------
# PREP DATA
# --------------------------------------------------

working_df = df.copy()

for col in features:
    working_df[col] = pd.to_numeric(
        working_df[col],
        errors="coerce"
    )

working_df[features] = (
    working_df[features]
    .replace([np.inf, -np.inf], np.nan)
    .fillna(0)
)

# --------------------------------------------------
# ANOMALY DETECTION
# --------------------------------------------------

iso = IsolationForest(
    contamination=0.03,
    random_state=42
)

working_df["anomaly"] = iso.fit_predict(
    working_df[features]
)

working_df["anomaly_score"] = (
    iso.decision_function(
        working_df[features]
    )
)

# --------------------------------------------------
# COMPANY AGGREGATION
# --------------------------------------------------

agg_dict = {}

if "market_value" in features:
    agg_dict["market_value"] = "sum"

if "conviction_score" in features:
    agg_dict["conviction_score"] = "mean"

if "shares_owned" in features:
    agg_dict["shares_owned"] = "sum"

if "shares_change" in features:
    agg_dict["shares_change"] = "mean"

if "ownership_percentage" in features:
    agg_dict["ownership_percentage"] = "mean"

agg_dict["anomaly_score"] = "mean"

risk_df = (
    working_df
    .groupby(company_col)
    .agg(agg_dict)
    .reset_index()
)

# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

score_cols = risk_df.columns.drop(company_col)

scaler = MinMaxScaler()

risk_df[score_cols] = scaler.fit_transform(
    risk_df[score_cols]
)

# --------------------------------------------------
# AI RISK SCORE
# --------------------------------------------------

risk_df["risk_score"] = (
    risk_df.get("shares_change", 0) * 0.25 +
    risk_df.get("ownership_percentage", 0) * 0.15 +
    risk_df.get("anomaly_score", 0) * 0.30 +
    (1 - risk_df.get("conviction_score", 0)) * 0.30
)

risk_df["risk_score"] = (
    risk_df["risk_score"] * 100
).round(2)

# --------------------------------------------------
# RISK CATEGORY
# --------------------------------------------------

def classify(score):

    if score >= 75:
        return "High Risk"

    elif score >= 50:
        return "Medium Risk"

    return "Low Risk"

risk_df["risk_category"] = (
    risk_df["risk_score"]
    .apply(classify)
)

# --------------------------------------------------
# KPIs
# --------------------------------------------------

st.subheader("📊 Portfolio Risk Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    f"{len(risk_df):,}"
)

c2.metric(
    "High Risk",
    len(
        risk_df[
            risk_df["risk_category"]
            == "High Risk"
        ]
    )
)

c3.metric(
    "Medium Risk",
    len(
        risk_df[
            risk_df["risk_category"]
            == "Medium Risk"
        ]
    )
)

c4.metric(
    "Low Risk",
    len(
        risk_df[
            risk_df["risk_category"]
            == "Low Risk"
        ]
    )
)

# --------------------------------------------------
# RISK DISTRIBUTION
# --------------------------------------------------

st.subheader("Risk Distribution")

fig1 = px.histogram(
    risk_df,
    x="risk_score",
    nbins=40,
    title="AI Risk Score Distribution"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# --------------------------------------------------
# CATEGORY BREAKDOWN
# --------------------------------------------------

st.subheader("Risk Categories")

cat_df = (
    risk_df["risk_category"]
    .value_counts()
    .reset_index()
)

cat_df.columns = [
    "Category",
    "Count"
]

fig2 = px.pie(
    cat_df,
    names="Category",
    values="Count",
    title="Risk Classification"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# --------------------------------------------------
# TOP RISK COMPANIES
# --------------------------------------------------

st.subheader("🚨 Highest Risk Companies")

top_risk = (
    risk_df
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(25)
)

fig3 = px.bar(
    top_risk,
    x=company_col,
    y="risk_score",
    color="risk_category",
    title="Top 25 Highest Risk Companies"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# --------------------------------------------------
# OPPORTUNITY SCORING
# --------------------------------------------------

risk_df["opportunity_score"] = (
    100 - risk_df["risk_score"]
)

st.subheader("🚀 Opportunity Leaders")

top_opportunity = (
    risk_df
    .sort_values(
        "opportunity_score",
        ascending=False
    )
    .head(20)
)

fig4 = px.bar(
    top_opportunity,
    x=company_col,
    y="opportunity_score",
    title="Top Opportunity Companies"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.subheader("🔍 Company Explorer")

selected_category = st.selectbox(
    "Risk Category",
    ["All"] +
    sorted(
        risk_df["risk_category"]
        .unique()
        .tolist()
    )
)

filtered = risk_df.copy()

if selected_category != "All":
    filtered = filtered[
        filtered["risk_category"]
        == selected_category
    ]

st.dataframe(
    filtered.sort_values(
        "risk_score",
        ascending=False
    ),
    use_container_width=True
)

# --------------------------------------------------
# AI INSIGHTS
# --------------------------------------------------

st.subheader("🤖 AI Generated Insights")

high_risk_count = len(
    risk_df[
        risk_df["risk_category"]
        == "High Risk"
    ]
)

avg_risk = risk_df[
    "risk_score"
].mean()

st.info(f"""
Total companies analyzed: {len(risk_df):,}

Average portfolio risk score: {avg_risk:.2f}

High-risk companies detected: {high_risk_count}

The AI Risk Engine combines:

• Conviction Score Analysis

• Institutional Ownership Patterns

• Position Change Trends

• Market Concentration Signals

• Isolation Forest Anomaly Detection

Companies with elevated risk scores may
require deeper due diligence and monitoring.
""")

# --------------------------------------------------
# EXPORT
# --------------------------------------------------

st.subheader("📥 Export Risk Report")

csv = risk_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download AI Risk Report",
    csv,
    "ai_risk_engine_report.csv",
    "text/csv"
)
