 # pages/Company_Comparison.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_master_data

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Company Comparison",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Company Comparison Dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def get_data():
    return load_master_data()

df = get_data()

# --------------------------------------------------
# IDENTIFY COMPANY COLUMN
# --------------------------------------------------

company_col = None

possible_cols = [
    "company_name",
    "issuer_name",
    "company",
    "issuer"
]

for col in possible_cols:
    if col in df.columns:
        company_col = col
        break

if company_col is None:
    st.error("Company column not found.")
    st.stop()

# --------------------------------------------------
# COMPANY SELECTION
# --------------------------------------------------

companies = sorted(
    df[company_col]
    .dropna()
    .astype(str)
    .unique()
)

selected_companies = st.multiselect(
    "Select Companies To Compare",
    companies,
    default=companies[:3]
)

if len(selected_companies) < 2:
    st.warning("Select at least 2 companies.")
    st.stop()

compare_df = df[
    df[company_col].astype(str)
    .isin(selected_companies)
]

# --------------------------------------------------
# AGGREGATE DATA
# --------------------------------------------------

summary = pd.DataFrame()

summary[company_col] = selected_companies

summary = (
    compare_df
    .groupby(company_col)
    .agg({
        col: "mean"
        for col in compare_df.select_dtypes(
            include=np.number
        ).columns
    })
    .reset_index()
)

# --------------------------------------------------
# KPI TABLE
# --------------------------------------------------

st.subheader("📊 Comparison Overview")

st.dataframe(
    summary,
    use_container_width=True
)

# --------------------------------------------------
# MARKET VALUE COMPARISON
# --------------------------------------------------

if "market_value" in summary.columns:

    st.subheader("💰 Market Value Comparison")

    fig1 = px.bar(
        summary,
        x=company_col,
        y="market_value",
        color=company_col,
        title="Market Value"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# --------------------------------------------------
# CONVICTION SCORE COMPARISON
# --------------------------------------------------

if "conviction_score" in summary.columns:

    st.subheader("🎯 Conviction Score Comparison")

    fig2 = px.bar(
        summary,
        x=company_col,
        y="conviction_score",
        color="conviction_score",
        title="Average Conviction Score"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# --------------------------------------------------
# OWNERSHIP COMPARISON
# --------------------------------------------------

if "ownership_percentage" in summary.columns:

    st.subheader("🏦 Ownership Percentage")

    fig3 = px.bar(
        summary,
        x=company_col,
        y="ownership_percentage",
        color=company_col,
        title="Institutional Ownership"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# --------------------------------------------------
# SHARES CHANGE
# --------------------------------------------------

if "shares_change" in summary.columns:

    st.subheader("📈 Position Change Analysis")

    fig4 = px.bar(
        summary,
        x=company_col,
        y="shares_change",
        color=company_col,
        title="Average Shares Change"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# --------------------------------------------------
# RADAR CHART
# --------------------------------------------------

st.subheader("🕸 Multi-Metric Radar Comparison")

radar_metrics = []

for metric in [
    "market_value",
    "conviction_score",
    "shares_owned",
    "shares_change",
    "ownership_percentage"
]:
    if metric in summary.columns:
        radar_metrics.append(metric)

if len(radar_metrics) >= 3:

    radar_df = summary.copy()

    for metric in radar_metrics:
        max_val = radar_df[metric].max()

        if max_val > 0:
            radar_df[metric] = (
                radar_df[metric] / max_val
            ) * 100

    fig_radar = go.Figure()

    for _, row in radar_df.iterrows():

        fig_radar.add_trace(
            go.Scatterpolar(
                r=[row[m] for m in radar_metrics],
                theta=radar_metrics,
                fill='toself',
                name=row[company_col]
            )
        )

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True
    )

    st.plotly_chart(
        fig_radar,
        use_container_width=True
    )

# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------

st.subheader("🔥 Correlation Analysis")

numeric_cols = summary.select_dtypes(
    include=np.number
)

if len(numeric_cols.columns) > 1:

    corr = numeric_cols.corr()

    heatmap = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns
        )
    )

    heatmap.update_layout(
        title="Metric Correlation Matrix"
    )

    st.plotly_chart(
        heatmap,
        use_container_width=True
    )

# --------------------------------------------------
# RANKING ENGINE
# --------------------------------------------------

st.subheader("🏆 Company Ranking")

ranking_metrics = [
    col
    for col in summary.columns
    if col != company_col
]

rank_df = summary.copy()

rank_df["overall_score"] = 0

for metric in ranking_metrics:

    rank_df["overall_score"] += (
        rank_df[metric]
        .rank(
            ascending=False,
            method="average"
        )
    )

rank_df = rank_df.sort_values(
    "overall_score"
)

rank_df["Rank"] = range(
    1,
    len(rank_df) + 1
)

st.dataframe(
    rank_df[
        ["Rank", company_col, "overall_score"]
    ],
    use_container_width=True
)

# --------------------------------------------------
# AI INSIGHTS
# --------------------------------------------------

st.subheader("🤖 AI Comparison Insights")

top_company = rank_df.iloc[0][company_col]

st.info(f"""
Top ranked company: {top_company}

Comparison performed using:

• Market Value

• Conviction Score

• Ownership Percentage

• Shares Owned

• Position Changes

Companies with higher conviction scores,
larger ownership concentrations, and
consistent institutional accumulation
typically demonstrate stronger institutional
confidence.

Use these insights alongside qualitative
research before making investment decisions.
""")

# --------------------------------------------------
# RAW DATA
# --------------------------------------------------

with st.expander("📂 View Raw Records"):
    st.dataframe(
        compare_df,
        use_container_width=True,
        height=400
    )

# --------------------------------------------------
# EXPORT REPORT
# --------------------------------------------------

st.subheader("📥 Export Comparison Report")

csv = rank_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Comparison Report",
    csv,
    "company_comparison_report.csv",
    "text/csv"
)
