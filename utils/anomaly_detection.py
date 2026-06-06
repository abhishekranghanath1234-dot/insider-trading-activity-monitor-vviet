 # pages/anomaly_detection.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from utils.data_loader import load_master_data

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Anomaly Detection",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Advanced Anomaly Detection Engine")
st.caption(
    "Machine Learning Powered Outlier Detection for Institutional Data"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def get_data():
    return load_master_data()

df = get_data()

# =====================================================
# DATA PREPARATION
# =====================================================

numeric_cols = df.select_dtypes(
    include=np.number
).columns.tolist()

if len(numeric_cols) < 2:
    st.error(
        "Dataset must contain at least 2 numeric columns."
    )
    st.stop()

st.sidebar.header("Detection Settings")

selected_features = st.sidebar.multiselect(
    "Select Features",
    numeric_cols,
    default=numeric_cols[:min(5, len(numeric_cols))]
)

contamination = st.sidebar.slider(
    "Expected Anomaly Rate (%)",
    min_value=1,
    max_value=20,
    value=3
)

if len(selected_features) < 2:
    st.warning(
        "Select at least 2 numerical columns."
    )
    st.stop()

# =====================================================
# CLEAN DATA
# =====================================================

working_df = df.copy()

working_df[selected_features] = (
    working_df[selected_features]
    .replace([np.inf, -np.inf], np.nan)
)

working_df[selected_features] = (
    working_df[selected_features]
    .fillna(
        working_df[selected_features].median()
    )
)

# =====================================================
# SCALING
# =====================================================

scaler = StandardScaler()

scaled_data = scaler.fit_transform(
    working_df[selected_features]
)

# =====================================================
# ISOLATION FOREST
# =====================================================

model = IsolationForest(
    contamination=contamination / 100,
    random_state=42,
    n_estimators=200
)

predictions = model.fit_predict(
    scaled_data
)

scores = model.decision_function(
    scaled_data
)

working_df["anomaly"] = predictions
working_df["anomaly_score"] = scores

anomalies = working_df[
    working_df["anomaly"] == -1
]

normal_data = working_df[
    working_df["anomaly"] == 1
]

# =====================================================
# KPIs
# =====================================================

st.subheader("📊 Detection Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Records",
    f"{len(working_df):,}"
)

c2.metric(
    "Normal Records",
    f"{len(normal_data):,}"
)

c3.metric(
    "Anomalies",
    f"{len(anomalies):,}"
)

c4.metric(
    "Anomaly %",
    f"{(len(anomalies)/len(working_df))*100:.2f}%"
)

# =====================================================
# PIE CHART
# =====================================================

st.subheader("Anomaly Distribution")

pie_df = pd.DataFrame({
    "Category": ["Normal", "Anomaly"],
    "Count": [
        len(normal_data),
        len(anomalies)
    ]
})

fig1 = px.pie(
    pie_df,
    names="Category",
    values="Count",
    title="Normal vs Anomalous Records"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =====================================================
# ANOMALY SCORE DISTRIBUTION
# =====================================================

st.subheader("Anomaly Score Distribution")

fig2 = px.histogram(
    working_df,
    x="anomaly_score",
    nbins=50,
    title="Isolation Forest Score Distribution"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =====================================================
# PCA VISUALIZATION
# =====================================================

st.subheader("🧠 PCA Anomaly Visualization")

pca = PCA(n_components=2)

pca_result = pca.fit_transform(
    scaled_data
)

pca_df = pd.DataFrame({
    "PC1": pca_result[:, 0],
    "PC2": pca_result[:, 1],
    "Type": np.where(
        working_df["anomaly"] == -1,
        "Anomaly",
        "Normal"
    )
})

fig3 = px.scatter(
    pca_df,
    x="PC1",
    y="PC2",
    color="Type",
    title="Anomaly Clusters (PCA)"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =====================================================
# FEATURE IMPORTANCE
# =====================================================

st.subheader("📈 Feature Variability")

variance_df = pd.DataFrame({
    "Feature": selected_features,
    "Variance": (
        working_df[selected_features]
        .var()
        .values
    )
})

variance_df = variance_df.sort_values(
    "Variance",
    ascending=False
)

fig4 = px.bar(
    variance_df,
    x="Feature",
    y="Variance",
    title="Feature Variability Ranking"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# =====================================================
# CORRELATION HEATMAP
# =====================================================

st.subheader("🔥 Feature Correlation")

corr = (
    working_df[selected_features]
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
    title="Correlation Matrix"
)

st.plotly_chart(
    heatmap,
    use_container_width=True
)

# =====================================================
# ANOMALY RECORDS
# =====================================================

st.subheader("🚨 Detected Anomalies")

display_cols = []

for col in [
    "company_name",
    "issuer_name",
    "anomaly_score"
]:
    if col in anomalies.columns:
        display_cols.append(col)

display_cols.extend(selected_features)

display_cols = list(dict.fromkeys(display_cols))

st.dataframe(
    anomalies[display_cols]
    .sort_values(
        "anomaly_score"
    ),
    use_container_width=True,
    height=500
)

# =====================================================
# TOP ANOMALOUS COMPANIES
# =====================================================

company_col = None

for col in [
    "company_name",
    "issuer_name",
    "company"
]:
    if col in anomalies.columns:
        company_col = col
        break

if company_col:

    st.subheader(
        "🏢 Most Frequently Flagged Companies"
    )

    top_companies = (
        anomalies.groupby(company_col)
        .size()
        .reset_index(
            name="Anomaly Count"
        )
        .sort_values(
            "Anomaly Count",
            ascending=False
        )
        .head(20)
    )

    fig5 = px.bar(
        top_companies,
        x=company_col,
        y="Anomaly Count",
        title="Top Anomalous Companies"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

# =====================================================
# AI INSIGHTS
# =====================================================

st.subheader("🤖 AI Insights")

avg_score = anomalies[
    "anomaly_score"
].mean() if len(anomalies) else 0

st.info(f"""
Records analyzed: {len(working_df):,}

Potential anomalies detected: {len(anomalies):,}

Average anomaly score:
{avg_score:.4f}

Detection Method:
Isolation Forest (Unsupervised ML)

The system identifies unusual institutional
activity, abnormal conviction patterns,
ownership spikes, market value outliers,
and unexpected portfolio movements.

Lower anomaly scores generally indicate
higher deviation from normal behavior.
""")

# =====================================================
# DOWNLOAD REPORT
# =====================================================

st.subheader("📥 Export Report")

csv = anomalies.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Anomaly Report",
    data=csv,
    file_name="anomaly_detection_report.csv",
    mime="text/csv"
)
