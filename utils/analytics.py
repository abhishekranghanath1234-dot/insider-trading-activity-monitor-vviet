import pandas as pd
import numpy as np

# --------------------------------------------------
# PORTFOLIO SUMMARY
# --------------------------------------------------

def portfolio_summary(df):
    """
    Generate portfolio summary metrics
    """

    if df.empty:
        return {}

    summary = {
        "total_records": len(df),
        "total_companies":
            df["issuer_name"].nunique()
            if "issuer_name" in df.columns else 0,

        "total_market_value":
            df["market_value"].sum()
            if "market_value" in df.columns else 0,

        "average_market_value":
            df["market_value"].mean()
            if "market_value" in df.columns else 0,

        "average_conviction":
            df["conviction_score"].mean()
            if "conviction_score" in df.columns else 0
    }

    return summary

# --------------------------------------------------
# TOP HOLDINGS
# --------------------------------------------------

def top_holdings(df, top_n=10):
    """
    Largest institutional holdings
    """

    if (
        df.empty or
        "issuer_name" not in df.columns or
        "market_value" not in df.columns
    ):
        return pd.DataFrame()

    return (
        df.groupby("issuer_name")
        ["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(top_n)
    )

# --------------------------------------------------
# TOP CONVICTION PICKS
# --------------------------------------------------

def top_conviction_stocks(df, top_n=10):
    """
    Highest conviction companies
    """

    if (
        df.empty or
        "issuer_name" not in df.columns or
        "conviction_score" not in df.columns
    ):
        return pd.DataFrame()

    return (
        df.groupby("issuer_name")
        ["conviction_score"]
        .mean()
        .reset_index()
        .sort_values(
            "conviction_score",
            ascending=False
        )
        .head(top_n)
    )

# --------------------------------------------------
# INSIDER ACTIVITY
# --------------------------------------------------

def insider_activity_summary(df):
    """
    Buy vs Sell summary
    """

    if (
        df.empty or
        "transaction_code" not in df.columns
    ):
        return {}

    buys = len(
        df[df["transaction_code"] == "P"]
    )

    sells = len(
        df[df["transaction_code"] == "S"]
    )

    total = buys + sells

    buy_ratio = (
        round((buys / total) * 100, 2)
        if total > 0
        else 0
    )

    return {
        "buy_transactions": buys,
        "sell_transactions": sells,
        "buy_ratio": buy_ratio
    }

# --------------------------------------------------
# SIGNAL SUMMARY
# --------------------------------------------------

def signal_summary(df):
    """
    Signal dataset summary
    """

    if df.empty:
        return {}

    return {
        "total_signals": len(df),

        "avg_signal_strength":
            df["signal_strength"].mean()
            if "signal_strength" in df.columns
            else 0,

        "avg_risk_score":
            df["risk_score"].mean()
            if "risk_score" in df.columns
            else 0
    }

# --------------------------------------------------
# TOP SIGNALS
# --------------------------------------------------

def strongest_signals(df, top_n=10):
    """
    Highest signal opportunities
    """

    if (
        df.empty or
        "signal_strength"
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
# BEST SECTOR
# --------------------------------------------------

def best_sector(df):
    """
    Best performing sector
    """

    if (
        df.empty or
        "sector" not in df.columns or
        "signal_strength" not in df.columns
    ):
        return None

    sector_scores = (
        df.groupby("sector")
        ["signal_strength"]
        .mean()
    )

    return sector_scores.idxmax()

# --------------------------------------------------
# SECTOR ANALYSIS
# --------------------------------------------------

def sector_performance(df):
    """
    Sector level performance
    """

    if (
        df.empty or
        "sector" not in df.columns or
        "signal_strength"
        not in df.columns
    ):
        return pd.DataFrame()

    return (
        df.groupby("sector")
        ["signal_strength"]
        .mean()
        .reset_index()
        .sort_values(
            "signal_strength",
            ascending=False
        )
    )

# --------------------------------------------------
# RISK ANALYSIS
# --------------------------------------------------

def risk_analysis(df):
    """
    Risk score statistics
    """

    if (
        df.empty or
        "risk_score" not in df.columns
    ):
        return {}

    return {
        "minimum":
            df["risk_score"].min(),

        "maximum":
            df["risk_score"].max(),

        "average":
            df["risk_score"].mean(),

        "median":
            df["risk_score"].median()
    }

# --------------------------------------------------
# RECOMMENDATION BREAKDOWN
# --------------------------------------------------

def recommendation_breakdown(df):
    """
    Buy/Hold/Sell counts
    """

    if (
        df.empty or
        "recommendation"
        not in df.columns
    ):
        return pd.DataFrame()

    return (
        df["recommendation"]
        .value_counts()
        .reset_index()
        .rename(
            columns={
                "index":
                    "Recommendation",
                "recommendation":
                    "Count"
            }
        )
    )

# --------------------------------------------------
# CORRELATION MATRIX
# --------------------------------------------------

def correlation_matrix(df):
    """
    Numeric correlation matrix
    """

    if df.empty:
        return pd.DataFrame()

    numeric_df = (
        df.select_dtypes(
            include=np.number
        )
    )

    if numeric_df.empty:
        return pd.DataFrame()

    return numeric_df.corr()

# --------------------------------------------------
# COMPANY SCORECARD
# --------------------------------------------------

def company_scorecard(df, company):
    """
    Detailed company analytics
    """

    if (
        df.empty or
        "issuer_name"
        not in df.columns
    ):
        return {}

    company_df = df[
        df["issuer_name"] == company
    ]

    if company_df.empty:
        return {}

    return {
        "company": company,

        "market_value":
            company_df["market_value"].sum()
            if "market_value" in company_df.columns
            else 0,

        "avg_conviction":
            company_df["conviction_score"].mean()
            if "conviction_score" in company_df.columns
            else 0,

        "records":
            len(company_df)
    }

# --------------------------------------------------
# AI STYLE INSIGHTS
# --------------------------------------------------

def generate_ai_insights(
    master_df,
    signals_df
):
    """
    Generate dashboard insights
    """

    insights = []

    if (
        not master_df.empty and
        "market_value"
        in master_df.columns and
        "issuer_name"
        in master_df.columns
    ):

        top_company = (
            master_df.groupby(
                "issuer_name"
            )["market_value"]
            .sum()
            .idxmax()
        )

        insights.append(
            f"Largest holding is {top_company}."
        )

    if (
        not master_df.empty and
        "conviction_score"
        in master_df.columns
    ):

        avg_conviction = (
            master_df[
                "conviction_score"
            ].mean()
        )

        insights.append(
            f"Average conviction score is "
            f"{avg_conviction:.2f}."
        )

    if (
        not signals_df.empty and
        "signal_strength"
        in signals_df.columns
    ):

        strongest = (
            signals_df.loc[
                signals_df[
                    "signal_strength"
                ].idxmax()
            ]
        )

        insights.append(
            f"Strongest signal belongs to "
            f"{strongest['issuer_name']}."
        )

    return insights

# --------------------------------------------------
# PORTFOLIO CONCENTRATION
# --------------------------------------------------

def portfolio_concentration(df):
    """
    Top 10 concentration %
    """

    if (
        df.empty or
        "market_value"
        not in df.columns
    ):
        return 0

    total = df["market_value"].sum()

    top10 = (
        df.sort_values(
            "market_value",
            ascending=False
        )
        .head(10)
        ["market_value"]
        .sum()
    )

    if total == 0:
        return 0

    return round(
        (top10 / total) * 100,
        2
    )
