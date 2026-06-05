import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Insider Transactions",
    page_icon="👨‍💼",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("MASTER_DATA_ENRICHED.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("👨‍💼 Insider Transactions Analysis")
st.markdown(
    "Monitor insider buying and selling activity across companies."
)

st.divider()

# --------------------------------------------------
# CHECK REQUIRED COLUMN
# --------------------------------------------------
if "transaction_code" not in df.columns:
    st.warning(
        "transaction_code column not found in dataset."
    )
    st.stop()

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.sidebar.header("Filters")

if "issuer_name" in df.columns:

    companies = sorted(
        df["issuer_name"]
        .dropna()
        .unique()
    )

    selected_company = st.sidebar.selectbox(
        "Company",
        ["All"] + list(companies)
    )

    if selected_company != "All":
        df = df[
            df["issuer_name"] ==
            selected_company
        ]

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
buy_count = len(
    df[df["transaction_code"] == "P"]
)

sell_count = len(
    df[df["transaction_code"] == "S"]
)

total_transactions = len(df)

buy_ratio = (
    buy_count / total_transactions * 100
    if total_transactions > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Transactions",
    total_transactions
)

col2.metric(
    "Buy Transactions",
    buy_count
)

col3.metric(
    "Sell Transactions",
    sell_count
)

col4.metric(
    "Buy Ratio %",
    f"{buy_ratio:.1f}%"
)

st.divider()

# --------------------------------------------------
# BUY VS SELL PIE CHART
# --------------------------------------------------
st.subheader("📊 Buy vs Sell Distribution")

transaction_summary = (
    df["transaction_code"]
    .value_counts()
    .reset_index()
)

transaction_summary.columns = [
    "Transaction",
    "Count"
]

fig = px.pie(
    transaction_summary,
    names="Transaction",
    values="Count",
    hole=0.5,
    title="Insider Activity"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# BAR CHART
# --------------------------------------------------
st.subheader("📈 Transaction Counts")

fig = px.bar(
    transaction_summary,
    x="Transaction",
    y="Count",
    color="Count",
    text="Count"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------------------------
# COMPANY LEVEL ANALYSIS
# --------------------------------------------------
if "issuer_name" in df.columns:

    st.subheader(
        "🏢 Insider Activity by Company"
    )

    company_activity = (
        df.groupby(
            ["issuer_name",
             "transaction_code"]
        )
        .size()
        .reset_index(name="Count")
    )

    fig = px.bar(
        company_activity,
        x="issuer_name",
        y="Count",
        color="transaction_code",
        barmode="group",
        title="Company Insider Activity"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# MARKET VALUE ANALYSIS
# --------------------------------------------------
if (
    "market_value" in df.columns
):

    st.subheader(
        "💰 Market Value Distribution"
    )

    fig = px.histogram(
        df,
        x="market_value",
        nbins=30,
        title="Market Value"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# CONVICTION SCORE ANALYSIS
# --------------------------------------------------
if (
    "conviction_score"
    in df.columns
):

    st.subheader(
        "🎯 Conviction Score Analysis"
    )

    fig = px.box(
        df,
        x="transaction_code",
        y="conviction_score",
        color="transaction_code"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# HEATMAP
# --------------------------------------------------
st.subheader("🔥 Correlation Analysis")

numeric_df = df.select_dtypes(
    include=np.number
)

if len(numeric_df.columns) > 1:

    corr = numeric_df.corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# TOP BUY COMPANIES
# --------------------------------------------------
if (
    "issuer_name" in df.columns
):

    st.subheader(
        "⭐ Top Insider Buy Companies"
    )

    buy_df = df[
        df["transaction_code"] == "P"
    ]

    if len(buy_df) > 0:

        top_buy = (
            buy_df.groupby(
                "issuer_name"
            )
            .size()
            .reset_index(
                name="Buy_Count"
            )
            .sort_values(
                "Buy_Count",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            top_buy,
            use_container_width=True
        )

# --------------------------------------------------
# RAW DATA
# --------------------------------------------------
st.subheader("📄 Transaction Records")

st.dataframe(
    df,
    use_container_width=True
)

# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------
csv = df.to_csv(index=False)

st.download_button(
    "⬇ Download Transactions",
    csv,
    "insider_transactions.csv",
    "text/csv"
)

# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------
st.subheader("🤖 Insider Insights")

if buy_count > sell_count:
    st.success(
        "Bullish signal: Insider buying exceeds selling."
    )
elif sell_count > buy_count:
    st.warning(
        "Bearish signal: Insider selling exceeds buying."
    )
else:
    st.info(
        "Neutral signal: Buying and selling are balanced."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")

st.caption(
    "Smart Money Dashboard | Insider Transactions Module"
)
