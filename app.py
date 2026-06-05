import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------------
# PAGE CONFIG
# ---------------------------------

st.set_page_config(
    page_title="Smart Money Surveillance",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------
# CUSTOM CSS
# ---------------------------------

css_file = Path("assets/styles.css")

if css_file.exists():
    with open(css_file) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# ---------------------------------
# SIDEBAR
# ---------------------------------

with st.sidebar:

    st.image(
        "assets/logo.png",
        use_container_width=True
    )

    st.title("🧠 Smart Money")

    st.markdown("---")

    st.markdown(
        """
        ### Platform Modules

        📊 Dashboard

        👨‍💼 Insider Transactions

        🏛 Institutional Holdings

        📈 Smart Money Signals

        🤖 AI Insights
        """
    )

    st.markdown("---")

    st.success("Live Intelligence Platform")

# ---------------------------------
# LOAD DATA
# ---------------------------------

@st.cache_data
def load_master():
    try:
        return pd.read_csv(
            "data/MASTER_DATA_ENRICHED.csv"
        )
    except:
        return pd.DataFrame()

@st.cache_data
def load_signals():
    try:
        return pd.read_csv(
            "data/PREMIUM_CROSS_MARKET_SIGNALS.csv"
        )
    except:
        return pd.DataFrame()

master_df = load_master()
signals_df = load_signals()

# ---------------------------------
# HEADER
# ---------------------------------

st.title("🧠 Smart Money Surveillance Platform")

st.caption(
    "Institutional Holdings • Insider Activity • Cross-Market Signals • AI Intelligence"
)

st.markdown("---")

# ---------------------------------
# KPI SECTION
# ---------------------------------

if not master_df.empty:

    total_records = len(master_df)

    total_companies = (
        master_df["company_name"].nunique()
        if "company_name" in master_df.columns
        else 0
    )

    total_value = (
        master_df["market_value"].sum()
        if "market_value" in master_df.columns
        else 0
    )

    avg_conviction = (
        master_df["conviction_score"].mean()
        if "conviction_score" in master_df.columns
        else 0
    )

else:

    total_records = 0
    total_companies = 0
    total_value = 0
    avg_conviction = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Filings",
        f"{total_records:,}"
    )

with col2:
    st.metric(
        "Companies",
        f"{total_companies:,}"
    )

with col3:
    st.metric(
        "Portfolio Value",
        f"${total_value/1e9:.2f}B"
    )

with col4:
    st.metric(
        "Avg Conviction",
        f"{avg_conviction:.2f}"
    )

st.markdown("---")

# ---------------------------------
# DATASET OVERVIEW
# ---------------------------------

col_left, col_right = st.columns([2, 1])

with col_left:

    st.subheader("📂 Available Datasets")

    datasets = pd.DataFrame(
        {
            "Dataset": [
                "MASTER_DATA_ENRICHED",
                "PREMIUM_CROSS_MARKET_SIGNALS"
            ],
            "Rows": [
                len(master_df),
                len(signals_df)
            ]
        }
    )

    st.dataframe(
        datasets,
        use_container_width=True
    )

with col_right:

    st.subheader("📈 Coverage")

    st.info(
        f"""
        Companies: {total_companies}

        Holdings: {total_records}

        Signals: {len(signals_df)}
        """
    )

st.markdown("---")

# ---------------------------------
# COLUMN INSPECTION
# ---------------------------------

st.subheader("🔍 Data Explorer")

tab1, tab2 = st.tabs(
    [
        "MASTER_DATA_ENRICHED",
        "PREMIUM_SIGNALS"
    ]
)

with tab1:

    if not master_df.empty:

        st.write("Rows:", len(master_df))
        st.write("Columns:", len(master_df.columns))

        selected_cols = st.multiselect(
            "Choose Columns",
            master_df.columns.tolist(),
            default=master_df.columns[:10]
        )

        st.dataframe(
            master_df[selected_cols],
            use_container_width=True
        )

    else:
        st.warning("MASTER_DATA_ENRICHED.csv not found.")

with tab2:

    if not signals_df.empty:

        st.write("Rows:", len(signals_df))
        st.write("Columns:", len(signals_df.columns))

        selected_cols = st.multiselect(
            "Signal Columns",
            signals_df.columns.tolist(),
            default=signals_df.columns[:10],
            key="signal_cols"
        )

        st.dataframe(
            signals_df[selected_cols],
            use_container_width=True
        )

    else:
        st.warning(
            "PREMIUM_CROSS_MARKET_SIGNALS.csv not found."
        )

st.markdown("---")

# ---------------------------------
# TOP SIGNALS PREVIEW
# ---------------------------------

st.subheader("🚨 Smart Money Opportunities")

if not signals_df.empty:

    score_column = None

    candidate_columns = [
        "signal_score",
        "conviction_score",
        "score",
        "strength"
    ]

    for col in candidate_columns:
        if col in signals_df.columns:
            score_column = col
            break

    if score_column:

        top_signals = (
            signals_df
            .sort_values(
                score_column,
                ascending=False
            )
            .head(20)
        )

        st.dataframe(
            top_signals,
            use_container_width=True
        )

    else:

        st.dataframe(
            signals_df.head(20),
            use_container_width=True
        )

else:

    st.info(
        "Signals dataset will appear here."
    )

st.markdown("---")

# ---------------------------------
# PLATFORM STATUS
# ---------------------------------

st.subheader("⚙️ System Status")

status1, status2, status3 = st.columns(3)

with status1:
    st.success("Data Engine Online")

with status2:
    st.success("Analytics Ready")

with status3:
    st.success("Streamlit Running")

# ---------------------------------
# FOOTER
# ---------------------------------

st.markdown("---")

st.markdown(
    """
    <center>

    <h4>🧠 Smart Money Surveillance Platform</h4>

    Institutional Holdings • Insider Tracking • AI Signals

    </center>
    """,
    unsafe_allow_html=True
)
