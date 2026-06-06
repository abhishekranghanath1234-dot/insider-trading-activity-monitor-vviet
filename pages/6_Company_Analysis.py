 # pages/Company_Analysis.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_master_data

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Company Analysis",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Company Analysis Dashboard")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def get_data():
    return load_master_data()

df = get_data()

# ---------------------------------------------------
# COMPANY SELECTION
# ---------------------------------------------------

company_col = None

possible_company_cols = [
    "company_name",
    "issuer_name",
    "company",
    "issuer"
]

for col in possible_company_cols:
    if col in df.columns:
        company_col = col
        break

if company_col is None:
    st.error("Company column not found in dataset.")
    st.stop()

companies = sorted(
    df[company_col]
    .dropna()
    .astype(str)
    .unique()
)

selected_company = st.sidebar.selectbox(
    "Select Company",
    companies
)

company_df = df[
    df[company_col].astype(str) == selected_company
]

# ---------------------------------------------------
# KPIs
# ---------------------------------------------------

st.subheader(f"📈 {selected_company} Overview")

col1, col2, col3, col4 = st.columns(4)

total_records = len(company_df)

market_value = (
    company_df["market_value"].sum()
    if "market_value" in company_df.columns
    else 0
)

avg_conviction = (
    company_df["conviction_score"].mean()
    if "conviction_score" in company_df.columns
    else 0
)

institution_count = (
    company_df["institution_name"].nunique()
    if "institution_name" in company_df.columns
    else 0
)

col1.metric(
    "Records",
    f"{total_records:,}"
)

col2.metric(
    "Market Value",
    f"${market_value:,.0f}"
)

col3.metric(
    "Avg Conviction",
    f"{avg_conviction:.2f}"
)

col4.metric(
    "Institutions",
    f"{institution_count:,}"
)

# ---------------------------------------------------
# MARKET VALUE ANALYSIS
# ---------------------------------------------------

if "market_value" in company_df.columns:

    st.subheader("💰 Market Value Distribution")

    fig = px.histogram(
        company_df,
        x="market_value",
        nbins=30,
        title="Market Value Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# CONVICTION ANALYSIS
# ---------------------------------------------------

if "conviction_score" in company_df.columns:

    st.subheader("🎯 Conviction Score Analysis")

    fig2 = px.box(
        company_df,
        y="conviction_score",
        title="Conviction Score Spread"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ---------------------------------------------------
# INSTITUTIONAL HOLDINGS
# ---------------------------------------------------

if (
    "institution_name" in company_df.columns
    and "market_value" in company_df.columns
):

    st.subheader("🏦 Top Institutional Holders")

    holders = (
        company_df
        .groupby("institution_name")
        ["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(15)
    )

    fig3 = px.bar(
        holders,
        x="institution_name",
        y="market_value",
        title="Largest Holders"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# ---------------------------------------------------
# POSITION CHANGES
# ---------------------------------------------------

if "shares_change" in company_df.columns:

    st.subheader("📊 Position Changes")

    fig4 = px.histogram(
        company_df,
        x="shares_change",
        nbins=40,
        title="Shares Change Distribution"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# ---------------------------------------------------
# CORRELATION HEATMAP
# ---------------------------------------------------

st.subheader("🔥 Numerical Correlations")

numeric_df = company_df.select_dtypes(
    include=np.number
)

if len(numeric_df.columns) > 1:

    corr = numeric_df.corr()

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

# ---------------------------------------------------
# DATA QUALITY SUMMARY
# ---------------------------------------------------

st.subheader("📋 Data Quality")

quality = pd.DataFrame({
    "Column": company_df.columns,
    "Missing Values":
    company_df.isnull().sum().values,
    "Data Type":
    company_df.dtypes.values.astype(str)
})

st.dataframe(
    quality,
    use_container_width=True
)

# ---------------------------------------------------
# RAW DATA
# ---------------------------------------------------

st.subheader("🗂 Company Records")

st.dataframe(
    company_df,
    use_container_width=True,
    height=400
)

# ---------------------------------------------------
# AI INSIGHTS
# ---------------------------------------------------

st.subheader("🤖 AI Insights")

insights = []

if market_value > 0:
    insights.append(
        f"Total tracked market value is ${market_value:,.0f}."
    )

if avg_conviction > 0:
    insights.append(
        f"Average conviction score is {avg_conviction:.2f}."
    )

if institution_count > 0:
    insights.append(
        f"{institution_count} institutions currently hold positions."
    )

if "shares_change" in company_df.columns:

    avg_change = company_df[
        "shares_change"
    ].mean()

    insights.append(
        f"Average share change is {avg_change:,.0f}."
    )

for item in insights:
    st.info(item)

# ---------------------------------------------------
# EXPORT SECTION
# ---------------------------------------------------

st.subheader("📥 Export Company Report")

csv = company_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download CSV Report",
    data=csv,
    file_name=f"{selected_company}_analysis.csv",
    mime="text/csv"
)
