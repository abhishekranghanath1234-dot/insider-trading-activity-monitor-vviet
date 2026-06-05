import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# DATA DIRECTORY
# =====================================================

DATA_DIR = Path("data")

# =====================================================
# GENERIC CSV LOADER
# =====================================================

@st.cache_data(show_spinner=False)
def load_csv(file_path):

    try:

        df = pd.read_csv(file_path)

        return df

    except Exception as e:

        st.error(
            f"Error loading {file_path}: {e}"
        )

        return pd.DataFrame()


# =====================================================
# MASTER DATA
# =====================================================

@st.cache_data(show_spinner=False)
def load_master_data():

    file_path = (
        DATA_DIR /
        "MASTER_DATA_ENRICHED.csv"
    )

    df = load_csv(file_path)

    numeric_columns = [
        "market_value",
        "shares_amount",
        "conviction_score",
        "transaction_shares",
        "transaction_price",
        "shares_owned_after",
        "confidence_score"
    ]

    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    date_columns = [
        "filing_date",
        "transaction_date",
        "deemed_execution_date"
    ]

    for col in date_columns:

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

    return df


# =====================================================
# SIGNALS DATA
# =====================================================

@st.cache_data(show_spinner=False)
def load_signals_data():

    file_path = (
        DATA_DIR /
        "PREMIUM_CROSS_MARKET_SIGNALS.csv"
    )

    df = load_csv(file_path)

    numeric_columns = [
        "conviction_score",
        "insider_score",
        "institutional_score",
        "market_value",
        "signal_score"
    ]

    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    if "signal_date" in df.columns:

        df["signal_date"] = pd.to_datetime(
            df["signal_date"],
            errors="coerce"
        )

    return df


# =====================================================
# INSIDER DATA
# =====================================================

@st.cache_data(show_spinner=False)
def load_insider_data():

    file_path = (
        DATA_DIR /
        "insider_transactions_data.csv"
    )

    df = load_csv(file_path)

    numeric_columns = [
        "shares",
        "price_per_share",
        "transaction_value",
        "shares_owned_after",
        "confidence_score"
    ]

    for col in numeric_columns:

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

    return df


# =====================================================
# HOLDINGS DATA
# =====================================================

@st.cache_data(show_spinner=False)
def load_holdings_data():

    file_path = (
        DATA_DIR /
        "institutional_holdings_data.csv"
    )

    df = load_csv(file_path)

    numeric_columns = [
        "shares_held",
        "market_value",
        "portfolio_weight",
        "conviction_score",
        "sole_voting_shares",
        "shared_voting_shares",
        "total_voting_shares"
    ]

    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    if "filing_date" in df.columns:

        df["filing_date"] = pd.to_datetime(
            df["filing_date"],
            errors="coerce"
        )

    return df


# =====================================================
# LOAD ALL DATASETS
# =====================================================

@st.cache_data(show_spinner=False)
def load_all_data():

    return {
        "master": load_master_data(),
        "signals": load_signals_data(),
        "insiders": load_insider_data(),
        "holdings": load_holdings_data()
    }


# =====================================================
# DATA SUMMARY
# =====================================================

def get_dataset_summary():

    datasets = load_all_data()

    summary = []

    for name, df in datasets.items():

        summary.append({
            "dataset": name,
            "rows": len(df),
            "columns": len(df.columns)
        })

    return pd.DataFrame(summary)


# =====================================================
# DATA HEALTH CHECK
# =====================================================

def data_health_check(df):

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values":
            int(df.isna().sum().sum()),
        "duplicates":
            int(df.duplicated().sum())
    }


# =====================================================
# FILTER HELPERS
# =====================================================

def filter_company(df, company):

    if (
        company == "All"
        or company is None
        or "company_name" not in df.columns
    ):
        return df

    return df[
        df["company_name"] == company
    ]


def filter_sector(df, sector):

    if (
        sector == "All"
        or sector is None
        or "sector" not in df.columns
    ):
        return df

    return df[
        df["sector"] == sector
    ]


def filter_signal(df, signal):

    if (
        signal == "All"
        or signal is None
        or "signal" not in df.columns
    ):
        return df

    return df[
        df["signal"] == signal
    ]


# =====================================================
# EXPORT HELPERS
# =====================================================

def dataframe_to_csv(df):

    return df.to_csv(
        index=False
    )


def dataframe_to_excel(df, file_name):

    with pd.ExcelWriter(
        file_name,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False
        )

    return file_name
