import pandas as pd
import numpy as np

# =====================================================
# CONVICTION SCORE ENGINE
# =====================================================

def calculate_conviction_score(df):

    df = df.copy()

    if "market_value" not in df.columns:
        return df

    market_rank = (
        df["market_value"]
        .rank(pct=True)
        .fillna(0)
    )

    shares_rank = (
        df.get(
            "shares_amount",
            pd.Series(index=df.index)
        )
        .rank(pct=True)
        .fillna(0)
    )

    df["conviction_score"] = (
        (
            market_rank * 0.60 +
            shares_rank * 0.40
        ) * 100
    ).round(2)

    return df


# =====================================================
# WHALE DETECTION
# =====================================================

def detect_whales(
    df,
    threshold=1000000000
):

    if "market_value" not in df.columns:
        return pd.DataFrame()

    whales = df[
        df["market_value"] >= threshold
    ].copy()

    whales["whale_flag"] = "YES"

    return whales.sort_values(
        "market_value",
        ascending=False
    )


# =====================================================
# TOP HOLDINGS
# =====================================================

def get_top_holdings(
    df,
    top_n=20
):

    required = [
        "company_name",
        "market_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return pd.DataFrame()

    return (
        df.groupby("company_name")
        ["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(top_n)
    )


# =====================================================
# PORTFOLIO CONCENTRATION
# =====================================================

def portfolio_concentration(df):

    if "market_value" not in df.columns:
        return 0

    total = df["market_value"].sum()

    if total == 0:
        return 0

    top10 = (
        df["market_value"]
        .nlargest(10)
        .sum()
    )

    return round(
        (top10 / total) * 100,
        2
    )


# =====================================================
# SMART MONEY SIGNAL SCORE
# =====================================================

def calculate_signal_score(df):

    df = df.copy()

    required = [
        "conviction_score",
        "insider_score",
        "institutional_score"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return df

    df["signal_score"] = (
        df["conviction_score"] * 0.50 +
        df["insider_score"] * 0.30 +
        df["institutional_score"] * 0.20
    ).round(2)

    return df


# =====================================================
# SIGNAL CLASSIFICATION
# =====================================================

def classify_signal(score):

    if score >= 80:
        return "STRONG BUY"

    elif score >= 65:
        return "BUY"

    elif score >= 50:
        return "WATCHLIST"

    elif score >= 35:
        return "REDUCE"

    return "SELL"


def generate_signals(df):

    df = calculate_signal_score(df)

    if "signal_score" not in df.columns:
        return df

    df["recommendation"] = (
        df["signal_score"]
        .apply(classify_signal)
    )

    return df


# =====================================================
# TOP OPPORTUNITIES
# =====================================================

def top_opportunities(
    df,
    top_n=20
):

    if "signal_score" not in df.columns:

        df = generate_signals(df)

    return (
        df.sort_values(
            "signal_score",
            ascending=False
        )
        .head(top_n)
    )


# =====================================================
# INSIDER BUY ANALYSIS
# =====================================================

def insider_buy_sell_summary(df):

    if "transaction_type" not in df.columns:
        return pd.DataFrame()

    summary = (
        df["transaction_type"]
        .value_counts()
        .reset_index()
    )

    summary.columns = [
        "transaction_type",
        "count"
    ]

    return summary


# =====================================================
# TOP INSIDERS
# =====================================================

def top_insiders(
    df,
    top_n=10
):

    required = [
        "owner_name",
        "transaction_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return pd.DataFrame()

    return (
        df.groupby("owner_name")
        ["transaction_value"]
        .sum()
        .reset_index()
        .sort_values(
            "transaction_value",
            ascending=False
        )
        .head(top_n)
    )


# =====================================================
# INSTITUTIONAL LEADERBOARD
# =====================================================

def institutional_leaderboard(
    df,
    top_n=20
):

    required = [
        "institution_name",
        "market_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return pd.DataFrame()

    return (
        df.groupby("institution_name")
        ["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(top_n)
    )


# =====================================================
# SECTOR ANALYSIS
# =====================================================

def sector_analysis(df):

    required = [
        "sector",
        "market_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return pd.DataFrame()

    return (
        df.groupby("sector")
        .agg(
            market_value=(
                "market_value",
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
    )


# =====================================================
# RISK SCORE
# =====================================================

def calculate_risk_score(df):

    if "conviction_score" not in df.columns:
        return 50

    avg_conviction = (
        df["conviction_score"]
        .mean()
    )

    risk_score = max(
        0,
        min(
            100,
            100 - avg_conviction
        )
    )

    return round(
        risk_score,
        2
    )


# =====================================================
# DATA HEALTH
# =====================================================

def dataset_health(df):

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values":
            int(df.isnull().sum().sum()),
        "duplicates":
            int(df.duplicated().sum())
    }


# =====================================================
# DASHBOARD KPIs
# =====================================================

def dashboard_metrics(df):

    metrics = {}

    metrics["total_records"] = len(df)

    metrics["total_companies"] = (
        df["company_name"].nunique()
        if "company_name" in df.columns
        else 0
    )

    metrics["total_market_value"] = (
        df["market_value"].sum()
        if "market_value" in df.columns
        else 0
    )

    metrics["avg_conviction"] = (
        round(
            df["conviction_score"]
            .mean(),
            2
        )
        if "conviction_score" in df.columns
        else 0
    )

    return metrics


# =====================================================
# AI SUMMARY GENERATOR
# =====================================================

def generate_ai_summary(df):

    metrics = dashboard_metrics(df)

    summary = f"""
Smart Money Analytics Summary

Total Records:
{metrics['total_records']:,}

Companies Covered:
{metrics['total_companies']:,}

Assets Monitored:
${metrics['total_market_value']:,.0f}

Average Conviction:
{metrics['avg_conviction']}

Key Observations:

• Institutional ownership remains concentrated.

• High conviction positions continue
  attracting capital allocation.

• Whale activity remains elevated.

• Smart money signals indicate
  several strong-buy opportunities.

• Portfolio concentration should be
  monitored for diversification risk.
"""

    return summary
