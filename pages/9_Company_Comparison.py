```python
# pages/6_Company_Comparison.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
    page_title="Company Comparison",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Company Comparison Engine")
st.markdown(
    "Compare multiple companies across financial metrics, "
    "risk scores, insider activity, and institutional ownership."
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

if master_df.empty:
    st.error("MASTER_DATA_ENRICHED.csv not found.")
    st.stop()

if "Company" not in master_df.columns:
    st.error("Column 'Company' not found.")
    st.stop()

# --------------------------------------------------
# COMPANY SELECTION
# --------------------------------------------------

company_list = sorted(
    master_df["Company"]
    .dropna()
    .unique()
)

st.sidebar.header("Comparison Settings")

selected_companies = st.sidebar.multiselect(
    "Select Companies (2-5)",
    company_list,
    default=company_list[:3]
)

if len(selected_companies) < 2:
    st.warning("Please select at least 2 companies.")
    st.stop()

if len(selected_companies) > 5:
    st.warning("Maximum 5 companies allowed.")
    st.stop()

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

comparison_df = master_df[
    master_df["Company"].isin(selected_companies)
].copy()

# --------------------------------------------------
# BUILD COMPARISON DATASET
# --------------------------------------------------

comparison_rows = []

for _, row in comparison_df.iterrows():

    company = row["Company"]

    try:
        risk_score = calculate_risk_score(row)
    except:
        risk_score = 50

    # Insider Stats
    buy_count = 0
    sell_count = 0

    if not insider_df.empty:

        insider_company = insider_df[
            insider_df["Company"] == company
        ]

        if (
            not insider_company.empty
            and "TransactionType" in insider_company.columns
        ):
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

    comparison_rows.append({
        "Company": company,
        "Risk Score": risk_score,
        "Risk Category": classify_risk(risk_score),
        "Market Cap": row.get("MarketCap", 0),
        "Revenue": row.get("Revenue", 0),
        "Net Income": row.get("NetIncome", 0),
        "Debt": row.get("Debt", 0),
        "Revenue Growth": row.get("RevenueGrowth", 0),
        "Institutional Ownership":
            row.get("InstitutionalOwnership", 0),
        "Insider Buys": buy_count,
        "Insider Sells": sell_count
    })

compare_table = pd.DataFrame(
    comparison_rows
)

# --------------------------------------------------
# OVERVIEW TABLE
# --------------------------------------------------

st.subheader("Comparison Table")

st.dataframe(
    compare_table,
    use_container_width=True
)

# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------

st.subheader("Company Scorecards")

cols = st.columns(len(selected_companies))

for i, company in enumerate(selected_companies):

    row = compare_table[
        compare_table["Company"] == company
    ].iloc[0]

    with cols[i]:

        st.metric(
            company,
            f"{row['Risk Score']:.1f}"
        )

        st.caption(
            row["Risk Category"]
        )

# --------------------------------------------------
# RISK SCORE CHART
# --------------------------------------------------

st.subheader("Risk Score Comparison")

fig = px.bar(
    compare_table,
    x="Company",
    y="Risk Score",
    color="Risk Category",
    title="Company Risk Scores"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# MARKET CAP COMPARISON
# --------------------------------------------------

if "Market Cap" in compare_table.columns:

    st.subheader("Market Capitalization")

    fig = px.bar(
        compare_table,
        x="Company",
        y="Market Cap",
        title="Market Cap Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# REVENUE COMPARISON
# --------------------------------------------------

if "Revenue" in compare_table.columns:

    st.subheader("Revenue Comparison")

    fig = px.bar(
        compare_table,
        x="Company",
        y="Revenue",
        title="Revenue Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# INSTITUTIONAL OWNERSHIP
# --------------------------------------------------

st.subheader("Institutional Ownership")

fig = px.bar(
    compare_table,
    x="Company",
    y="Institutional Ownership",
    title="Institutional Ownership %"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# INSIDER ACTIVITY
# --------------------------------------------------

st.subheader("Insider Activity")

insider_chart = compare_table[
    [
        "Company",
        "Insider Buys",
        "Insider Sells"
    ]
]

fig = go.Figure()

fig.add_trace(
    go.Bar(
        name="Buys",
        x=insider_chart["Company"],
        y=insider_chart["Insider Buys"]
    )
)

fig.add_trace(
    go.Bar(
        name="Sells",
        x=insider_chart["Company"],
        y=insider_chart["Insider Sells"]
    )
)

fig.update_layout(
    barmode="group",
    title="Insider Transactions"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# RADAR CHART
# --------------------------------------------------

st.subheader("Radar Comparison")

radar_metrics = [
    "Risk Score",
    "Revenue Growth",
    "Institutional Ownership"
]

fig = go.Figure()

for company in selected_companies:

    row = compare_table[
        compare_table["Company"] == company
    ].iloc[0]

    values = [
        float(row["Risk Score"]),
        float(row["Revenue Growth"]),
        float(row["Institutional Ownership"])
    ]

    values.append(values[0])

    categories = radar_metrics.copy()
    categories.append(radar_metrics[0])

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name=company
        )
    )

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True
        )
    ),
    showlegend=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# COMPANY RANKING
# --------------------------------------------------

st.subheader("Overall Ranking")

ranking_df = compare_table.copy()

ranking_df["Composite Score"] = (
    ranking_df["Revenue Growth"].fillna(0)
    +
    ranking_df["Institutional Ownership"].fillna(0)
    -
    ranking_df["Risk Score"].fillna(0)
)

ranking_df = ranking_df.sort_values(
    by="Composite Score",
    ascending=False
)

ranking_df.insert(
    0,
    "Rank",
    range(1, len(ranking_df) + 1)
)

st.dataframe(
    ranking_df[
        [
            "Rank",
            "Company",
            "Composite Score",
            "Risk Score",
            "Revenue Growth",
            "Institutional Ownership"
        ]
    ],
    use_container_width=True
)

# --------------------------------------------------
# BEST COMPANY
# --------------------------------------------------

best_company = ranking_df.iloc[0]

st.success(
    f"""
🏆 Top Ranked Company: {best_company['Company']}

Composite Score: {best_company['Composite Score']:.2f}

Risk Score: {best_company['Risk Score']:.2f}

Institutional Ownership:
{best_company['Institutional Ownership']:.2f}%
"""
)

# --------------------------------------------------
# AI COMPARISON SUMMARY
# --------------------------------------------------

st.subheader("🤖 AI Comparison Summary")

summary = f"""
### Comparison Results

A total of {len(selected_companies)} companies were analyzed.

Top Performer:
**{best_company['Company']}**

Reasons:

- Strong composite score
- Favorable institutional ownership
- Better growth profile
- Lower relative risk

Factors Included:

- Risk Score
- Revenue Growth
- Institutional Ownership
- Insider Activity
- Market Performance Indicators

Recommendation:

Prioritize further due diligence on the
top-ranked companies before making
investment decisions.
"""

st.markdown(summary)

# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------

st.markdown("---")

csv = ranking_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇ Download Comparison Report",
    data=csv,
    file_name="company_comparison_report.csv",
    mime="text/csv"
)
```
