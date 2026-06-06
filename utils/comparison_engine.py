 # pages/comparison_engine.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_master_data

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Comparison Engine",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ AI Comparison Engine")
st.caption(
    "Advanced Multi-Company Institutional Intelligence Comparison"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def get_data():
    return load_master_data()

df = get_data()

# =====================================================
# DETECT COMPANY COLUMN
# =====================================================

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

# =====================================================
# COMPANY SELECTION
# =====================================================

companies = sorted(
    df[company_col]
    .dropna()
    .astype(str)
    .unique()
)

selected_companies = st.multiselect(
    "Select Companies",
    companies,
    default=companies[:min(5, len(companies))]
)

if len(selected_companies) < 2:
    st.warning(
        "Please select at least 2 companies."
    )
    st.stop()

compare_df = df[
    df[company_col]
    .astype(str)
    .isin(selected_companies)
]

# =====================================================
# NUMERIC COLUMNS
# =====================================================

numeric_cols = (
    compare_df
    .select_dtypes(include=np.number)
    .columns
    .tolist()
)

if len(numeric_cols) == 0:
    st.error("No numeric columns found.")
    st.stop()

# =====================================================
# AGGREGATE DATA
# =====================================================

summary = (
    compare_df
    .groupby(company_col)[numeric_cols]
    .mean()
    .reset_index()
)

# =====================================================
# KPI SECTION
# =====================================================

st.subheader("📊 Comparison Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Companies",
    len(selected_companies)
)

col2.metric(
    "Records Compared",
    len(compare_df)
)

col3.metric(
    "Metrics Used",
    len(numeric_cols)
)

col4.metric(
    "Average Metrics",
    round(
        summary[numeric_cols]
        .mean()
        .mean(),
        2
    )
)

# =====================================================
# SUMMARY TABLE
# =====================================================

st.subheader("📋 Comparison Table")

st.dataframe(
    summary,
    use_container_width=True
)

# =====================================================
# METRIC SELECTOR
# =====================================================

st.subheader("📈 Metric Comparison")

metric = st.selectbox(
    "Select Metric",
    numeric_cols
)

# =====================================================
# BAR CHART
# =====================================================

fig1 = px.bar(
    summary,
    x=company_col,
    y=metric,
    color=company_col,
    title=f"{metric} Comparison"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =====================================================
# LINE COMPARISON
# =====================================================

fig2 = px.line(
    summary,
    x=company_col,
    y=metric,
    markers=True,
    title=f"{metric} Trend"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =====================================================
# RADAR CHART
# =====================================================

st.subheader("🕸 Radar Comparison")

radar_metrics = numeric_cols[:6]

if len(radar_metrics) >= 3:

    radar_df = summary.copy()

    for m in radar_metrics:

        max_val = radar_df[m].max()

        if max_val > 0:
            radar_df[m] = (
                radar_df[m] / max_val
            ) * 100

    radar = go.Figure()

    for _, row in radar_df.iterrows():

        radar.add_trace(
            go.Scatterpolar(
                r=[
                    row[m]
                    for m in radar_metrics
                ],
                theta=radar_metrics,
                fill='toself',
                name=row[company_col]
            )
        )

    radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        ),
        showlegend=True
    )

    st.plotly_chart(
        radar,
        use_container_width=True
    )

# =====================================================
# HEATMAP
# =====================================================

st.subheader("🔥 Correlation Matrix")

corr = (
    summary[numeric_cols]
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
    title="Metric Correlation"
)

st.plotly_chart(
    heatmap,
    use_container_width=True
)

# =====================================================
# RANKING ENGINE
# =====================================================

st.subheader("🏆 AI Ranking Engine")

rank_df = summary.copy()

rank_df["overall_score"] = 0

for col in numeric_cols:

    rank_df["overall_score"] += (
        rank_df[col]
        .rank(
            ascending=False,
            method="average"
        )
    )

rank_df = rank_df.sort_values(
    "overall_score"
)

rank_df["rank"] = (
    range(
        1,
        len(rank_df) + 1
    )
)

ranking_display = rank_df[
    [
        "rank",
        company_col,
        "overall_score"
    ]
]

st.dataframe(
    ranking_display,
    use_container_width=True
)

# =====================================================
# TOP COMPANY
# =====================================================

best_company = (
    rank_df.iloc[0][company_col]
)

st.success(
    f"🏆 Highest Ranked Company: {best_company}"
)

# =====================================================
# SCORE DISTRIBUTION
# =====================================================

st.subheader("📊 Overall Score Distribution")

fig3 = px.bar(
    rank_df,
    x=company_col,
    y="overall_score",
    color="overall_score",
    title="Company Scores"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =====================================================
# AI INSIGHTS
# =====================================================

st.subheader("🤖 AI Insights")

highest_metric_company = (
    summary.loc[
        summary[metric].idxmax(),
        company_col
    ]
)

lowest_metric_company = (
    summary.loc[
        summary[metric].idxmin(),
        company_col
    ]
)

st.info(f"""
Comparison completed across
{len(selected_companies)} companies.

Selected metric:
{metric}

Highest value:
{highest_metric_company}

Lowest value:
{lowest_metric_company}

Top ranked company:
{best_company}

The ranking engine evaluates all
available numerical metrics and
generates a composite score to
identify relative leaders and laggards.

Use this comparison together with
qualitative analysis and market research
for deeper investment insights.
""")

# =====================================================
# RAW DATA
# =====================================================

with st.expander("📂 View Raw Records"):

    st.dataframe(
        compare_df,
        use_container_width=True,
        height=500
    )

# =====================================================
# EXPORT REPORT
# =====================================================

st.subheader("📥 Export Comparison Report")

csv = rank_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Comparison Report",
    data=csv,
    file_name="comparison_engine_report.csv",
    mime="text/csv"
)

# =====================================================
# EXPORT SUMMARY
# =====================================================

summary_csv = summary.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Summary Metrics",
    data=summary_csv,
    file_name="comparison_summary.csv",
    mime="text/csv"
)
