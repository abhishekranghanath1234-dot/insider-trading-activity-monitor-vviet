import pandas as pd
import streamlit as st
from pathlib import Path

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_FILE = BASE_DIR / "MASTER_DATA_ENRICHED.csv"

SIGNALS_FILE = (
    BASE_DIR /
    "PREMIUM_CROSS_MARKET_SIGNALS.csv"
)

# --------------------------------------------------
# LOAD MASTER DATA
# --------------------------------------------------

@st.cache_data
def load_master_data():
    """
    Load institutional holdings dataset
    """

    try:

        df = pd.read_csv(MASTER_FILE)

        return df

    except Exception as e:

        st.error(
            f"Error loading master dataset: {e}"
        )

        return pd.DataFrame()

# --------------------------------------------------
# LOAD SIGNALS DATA
# --------------------------------------------------

@st.cache_data
def load_signals_data():
    """
    Load smart money signals dataset
    """

    try:

        df = pd.read_csv(SIGNALS_FILE)

        return df

    except Exception as e:

        st.error(
            f"Error loading signals dataset: {e}"
        )

        return pd.DataFrame()

# --------------------------------------------------
# LOAD ALL DATA
# --------------------------------------------------

@st.cache_data
def load_all_data():
    """
    Load all datasets
    """

    master_df = load_master_data()

    signals_df = load_signals_data()

    return master_df, signals_df

# --------------------------------------------------
# DATA SUMMARY
# --------------------------------------------------

def get_data_summary(df):
    """
    Return dataset summary statistics
    """

    if df.empty:

        return {
            "rows": 0,
            "columns": 0,
            "missing_values": 0
        }

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values":
        df.isnull().sum().sum()
    }

# --------------------------------------------------
# CLEAN DATA
# --------------------------------------------------

def clean_data(df):
    """
    Basic cleaning
    """

    if df.empty:
        return df

    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates()

    # Fill numeric columns
    numeric_cols = (
        df.select_dtypes(
            include=["number"]
        ).columns
    )

    df[numeric_cols] = (
        df[numeric_cols]
        .fillna(0)
    )

    # Fill text columns
    text_cols = (
        df.select_dtypes(
            include=["object"]
        ).columns
    )

    df[text_cols] = (
        df[text_cols]
        .fillna("Unknown")
    )

    return df

# --------------------------------------------------
# FILTER BY COMPANY
# --------------------------------------------------

def filter_company(
    df,
    company_name
):
    """
    Filter dataset by company
    """

    if (
        df.empty
        or company_name == "All"
    ):
        return df

    if "issuer_name" not in df.columns:
        return df

    return df[
        df["issuer_name"]
        == company_name
    ]

# --------------------------------------------------
# FILTER BY SECTOR
# --------------------------------------------------

def filter_sector(
    df,
    sector_name
):
    """
    Filter dataset by sector
    """

    if (
        df.empty
        or sector_name == "All"
    ):
        return df

    if "sector" not in df.columns:
        return df

    return df[
        df["sector"]
        == sector_name
    ]

# --------------------------------------------------
# TOP HOLDINGS
# --------------------------------------------------

def get_top_holdings(
    df,
    top_n=10
):
    """
    Get largest holdings
    """

    if (
        df.empty
        or "issuer_name"
        not in df.columns
        or "market_value"
        not in df.columns
    ):
        return pd.DataFrame()

    return (
        df.groupby(
            "issuer_name"
        )["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(top_n)
    )

# --------------------------------------------------
# TOP SIGNALS
# --------------------------------------------------

def get_top_signals(
    df,
    top_n=10
):
    """
    Get strongest smart money signals
    """

    if (
        df.empty
        or "signal_strength"
        not in df.columns
    ):
        return pd.DataFrame()

    return (
        df.sort_values(
            "signal_strength",
            ascending=False
        )
        .head(top_n)
    )

# --------------------------------------------------
# COMPANY LIST
# --------------------------------------------------

def get_company_list(df):
    """
    Return sorted company list
    """

    if (
        df.empty
        or "issuer_name"
        not in df.columns
    ):
        return []

    return sorted(
        df["issuer_name"]
        .dropna()
        .unique()
        .tolist()
    )

# --------------------------------------------------
# SECTOR LIST
# --------------------------------------------------

def get_sector_list(df):
    """
    Return sorted sector list
    """

    if (
        df.empty
        or "sector"
        not in df.columns
    ):
        return []

    return sorted(
        df["sector"]
        .dropna()
        .unique()
        .tolist()
    )

# --------------------------------------------------
# PORTFOLIO METRICS
# --------------------------------------------------

def get_portfolio_metrics(df):
    """
    Dashboard KPI metrics
    """

    if df.empty:

        return {
            "companies": 0,
            "records": 0,
            "market_value": 0,
            "avg_conviction": 0
        }

    return {
        "companies":
        df["issuer_name"].nunique()
        if "issuer_name" in df.columns
        else 0,

        "records":
        len(df),

        "market_value":
        df["market_value"].sum()
        if "market_value" in df.columns
        else 0,

        "avg_conviction":
        round(
            df["conviction_score"].mean(),
            2
        )
        if "conviction_score"
        in df.columns
        else 0
    }

# --------------------------------------------------
# EXPORT CSV
# --------------------------------------------------

def convert_to_csv(df):
    """
    Convert dataframe to CSV
    """

    if df.empty:
        return ""

    return df.to_csv(
        index=False
    )
