import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Insider Transactions",
    page_icon="👨‍💼",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    return pd.read_csv(
        "data/insider_transactions_data.csv"
    )

df = load_data()

# =====================================================
# PAGE TITLE
# =====================================================

st.title("👨‍💼 Insider Transactions Intelligence")

st.caption(
    "Track insider buying, selling, executive activity, and confidence scores."
)

st.divider()

# =====================================================
# DATA PREPARATION
# =====================================================

numeric_cols = [
    "shares",
    "price_per_share",
    "transaction_value",
    "confidence_score",
    "shares_owned_after"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

if "transaction_date" in df.columns:
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("🔎 Filters")

selected_company = "All"

if "company_name" in df.columns:

    companies = sorted(
        df["company_name"]
        .dropna()
        .unique()
    )

    selected_company = st.sidebar.selectbox(
        "Company",
        ["All"] + list(companies)
    )

selected_signal = "All"

if "signal" in df.columns:

    signals = sorted(
        df["signal"]
        .dropna()
        .unique()
    )

    selected_signal = st.sidebar.selectbox(
        "Signal",
        ["All"] + list(signals)
    )

selected_transaction = "All"

if "transaction_type" in df.columns:

    tx_types = sorted(
        df["transaction_type"]
        .dropna()
        .unique()
    )

    selected_transaction = st.sidebar.selectbox(
        "Transaction Type",
        ["All"] + list(tx_types)
    )

# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = df.copy()

if (
    selected_company != "All"
    and "company_name" in filtered_df.columns
):
    filtered_df = filtered_df[
        filtered_df["company_name"]
        == selected_company
    ]

if (
    selected_signal != "All"
    and "signal" in filtered_df.columns
):
    filtered_df = filtered_df[
        filtered_df["signal"]
        == selected_signal
    ]

if (
    selected_transaction != "All"
    and "transaction_type" in filtered_df.columns
):
    filtered_df = filtered_df[
        filtered_df["transaction_type"]
        == selected_transaction
    ]

# =====================================================
# KPIs
# =====================================================

total_transactions = len(filtered_df)

total_value = (
    filtered_df["transaction_value"].sum()
    if "transaction_value" in filtered_df.columns
    else 0
)

avg_confidence = (
    filtered_df["confidence_score"].mean()
    if "confidence_score" in filtered_df.columns
    else 0
)

unique_insiders = (
    filtered_df["owner_name"].nunique()
    if "owner_name" in filtered_df.columns
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Transactions",
    f"{total_transactions:,}"
)

col2.metric(
    "Transaction Value",
    f"${total_value:,.0f}"
)

col3.metric(
    "Avg Confidence",
    f"{avg_confidence:.1f}"
)

col4.metric(
    "Unique Insiders",
    f"{unique_insiders:,}"
)

st.divider()

# =====================================================
# BUY VS SELL PIE
# =====================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("📊 Buy vs Sell Distribution")

    if "transaction_type" in filtered_df.columns:

        pie_df = (
            filtered_df["transaction_type"]
            .value_counts()
            .reset_index()
        )

        pie_df.columns = [
            "Transaction Type",
            "Count"
        ]

        fig = px.pie(
            pie_df,
            names="Transaction Type",
            values="Count",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# SIGNAL DISTRIBUTION
# =====================================================

with col2:

    st.subheader("🚦 Signal Distribution")

    if "signal" in filtered_df.columns:

        signal_df = (
            filtered_df["signal"]
            .value_counts()
            .reset_index()
        )

        signal_df.columns = [
            "Signal",
            "Count"
        ]

        fig = px.bar(
            signal_df,
            x="Signal",
            y="Count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

st.divider()

# =====================================================
# TOP INSIDER BUYERS
# =====================================================

st.subheader("🏆 Top Insider Buyers")

if (
    "owner_name" in filtered_df.columns
    and "transaction_value" in filtered_df.columns
):

    buyers = (
        filtered_df
        .groupby("owner_name")["transaction_value"]
        .sum()
        .reset_index()
        .sort_values(
            "transaction_value",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        buyers,
        x="transaction_value",
        y="owner_name",
        orientation="h",
        title="Largest Insider Transactions"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# CONFIDENCE HISTOGRAM
# =====================================================

st.subheader("📈 Confidence Score Distribution")

if "confidence_score" in filtered_df.columns:

    fig = px.histogram(
        filtered_df,
        x="confidence_score",
        nbins=20
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# TRANSACTION TIMELINE
# =====================================================

st.subheader("📅 Insider Activity Timeline")

if (
    "transaction_date" in filtered_df.columns
    and "transaction_value" in filtered_df.columns
):

    timeline_df = (
        filtered_df
        .groupby("transaction_date")[
            "transaction_value"
        ]
        .sum()
        .reset_index()
    )

    fig = px.line(
        timeline_df,
        x="transaction_date",
        y="transaction_value",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# COMPANY LEADERBOARD
# =====================================================

st.subheader("🏢 Company Activity Leaderboard")

if (
    "company_name" in filtered_df.columns
    and "transaction_value" in filtered_df.columns
):

    company_df = (
        filtered_df
        .groupby("company_name")[
            "transaction_value"
        ]
        .sum()
        .reset_index()
        .sort_values(
            "transaction_value",
            ascending=False
        )
        .head(20)
    )

    fig = px.bar(
        company_df,
        x="company_name",
        y="transaction_value"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# =====================================================
# HIGH CONFIDENCE TRADES
# =====================================================

st.subheader("🔥 High Confidence Insider Trades")

if "confidence_score" in filtered_df.columns:

    high_confidence = filtered_df[
        filtered_df["confidence_score"] >= 80
    ]

    st.dataframe(
        high_confidence.sort_values(
            "confidence_score",
            ascending=False
        ),
        use_container_width=True
    )

st.divider()

# =====================================================
# FULL TRANSACTION TABLE
# =====================================================

st.subheader("📄 Insider Transaction Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500
)

# =====================================================
# DOWNLOAD OPTION
# =====================================================

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="⬇ Download Filtered Transactions",
    data=csv,
    file_name="filtered_insider_transactions.csv",
    mime="text/csv"
)

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.markdown(
    """
    ### 🧠 Insider Intelligence Engine

    Monitor executive buying, selling activity,
    confidence scoring, and smart money behavior.
    """
)
