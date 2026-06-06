import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.ensemble import IsolationForest

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Insider Trading Activity Monitor",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.metric-card {
    background-color:#1E1E1E;
    padding:15px;
    border-radius:10px;
}

h1,h2,h3 {
    color:white;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("📈 Insider Trading Activity Monitor")

st.markdown("""
Monitor insider buying, selling activity,
detect anomalies and generate AI insights.
""")

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload Insider Trading Dataset",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

else:

    st.warning("Upload a CSV file to continue.")
    st.stop()

# ---------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------

df.columns = df.columns.str.lower()

date_cols = [
    col for col in df.columns
    if "date" in col
]

for col in date_cols:
    try:
        df[col] = pd.to_datetime(df[col])
    except:
        pass

# ---------------------------------------------------
# DETECT IMPORTANT COLUMNS
# ---------------------------------------------------

company_col = None
shares_col = None
price_col = None
owner_col = None

for col in df.columns:

    if "company" in col:
        company_col = col

    if "share" in col:
        shares_col = col

    if "price" in col:
        price_col = col

    if "owner" in col:
        owner_col = col

# ---------------------------------------------------
# CREATE TRANSACTION VALUE
# ---------------------------------------------------

if shares_col and price_col:

    df["transaction_value"] = (
        pd.to_numeric(df[shares_col], errors="coerce")
        *
        pd.to_numeric(df[price_col], errors="coerce")
    )

else:

    df["transaction_value"] = 0

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_transactions = len(df)

total_value = df["transaction_value"].sum()

avg_value = df["transaction_value"].mean()

unique_companies = (
    df[company_col].nunique()
    if company_col
    else 0
)

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.metric(
        "Transactions",
        f"{total_transactions:,}"
    )

with col2:
    st.metric(
        "Companies",
        f"{unique_companies:,}"
    )

with col3:
    st.metric(
        "Transaction Value",
        f"${total_value:,.0f}"
    )

with col4:
    st.metric(
        "Avg Value",
        f"${avg_value:,.0f}"
    )

st.divider()

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

if company_col:

    companies = sorted(
        df[company_col].dropna().unique()
    )

    selected_companies = st.sidebar.multiselect(
        "Select Companies",
        companies
    )

    if selected_companies:

        df = df[
            df[company_col].isin(selected_companies)
        ]

# ---------------------------------------------------
# TRANSACTION TREND
# ---------------------------------------------------

st.subheader("📅 Insider Activity Trend")

date_column = None

for col in df.columns:

    if "date" in col:
        date_column = col
        break

if date_column:

    trend = (
        df.groupby(date_column)
        .size()
        .reset_index(name="transactions")
    )

    fig = px.line(
        trend,
        x=date_column,
        y="transactions",
        markers=True,
        title="Transaction Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# TOP COMPANIES
# ---------------------------------------------------

if company_col:

    st.subheader("🏢 Top Active Companies")

    company_summary = (
        df.groupby(company_col)
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        company_summary,
        x=company_col,
        y="count",
        title="Most Active Companies"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# TRANSACTION VALUE HISTOGRAM
# ---------------------------------------------------

st.subheader("💰 Transaction Value Distribution")

fig = px.histogram(
    df,
    x="transaction_value",
    nbins=50
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------------------------
# TOP INSIDERS
# ---------------------------------------------------

if owner_col:

    st.subheader("👤 Most Active Insiders")

    insider_summary = (
        df.groupby(owner_col)
        .size()
        .reset_index(name="transactions")
        .sort_values(
            "transactions",
            ascending=False
        )
        .head(20)
    )

    fig = px.bar(
        insider_summary,
        x=owner_col,
        y="transactions"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# ANOMALY DETECTION
# ---------------------------------------------------

st.subheader("🚨 Insider Trading Anomaly Detection")

features = pd.DataFrame()

features["transaction_value"] = (
    df["transaction_value"]
    .fillna(0)
)

if shares_col:

    features["shares"] = (
        pd.to_numeric(
            df[shares_col],
            errors="coerce"
        )
        .fillna(0)
    )

if len(features) > 20:

    model = IsolationForest(
        contamination=0.03,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(
        features
    )

    anomalies = df[
        df["anomaly"] == -1
    ]

    fig = px.scatter(
        df,
        x=features.columns[0],
        y=features.columns[-1],
        color=df["anomaly"].astype(str),
        title="Anomaly Detection"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.write(
        f"Detected {len(anomalies)} suspicious transactions."
    )

# ---------------------------------------------------
# AI INSIGHTS
# ---------------------------------------------------

st.subheader("🤖 AI Insights")

insights = []

if company_col:

    top_company = (
        df[company_col]
        .value_counts()
        .idxmax()
    )

    insights.append(
        f"Most insider activity observed in {top_company}."
    )

if len(df) > 0:

    high_value = (
        df["transaction_value"]
        .quantile(0.95)
    )

    insights.append(
        f"Top 5% transactions exceed ${high_value:,.0f}."
    )

if "anomaly" in df.columns:

    anomaly_count = (
        df["anomaly"] == -1
    ).sum()

    insights.append(
        f"{anomaly_count} abnormal transactions detected."
    )

for item in insights:

    st.success(item)

# ---------------------------------------------------
# DATA TABLE
# ---------------------------------------------------

st.subheader("📋 Insider Transactions")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# ---------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------

csv = df.to_csv(index=False)

st.download_button(
    label="⬇ Download Filtered Data",
    data=csv,
    file_name="filtered_transactions.csv",
    mime="text/csv"
)
