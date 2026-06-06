```python id="comparison_engine_utils_001"
# utils/comparison_engine.py

import numpy as np
import pandas as pd

from utils.risk_scoring import calculate_risk_score, classify_risk


# --------------------------------------------------
# CORE COMPARISON ENGINE
# --------------------------------------------------

def compare_companies(master_df: pd.DataFrame, companies: list):
    """
    Build a structured comparison dataset for selected companies.
    """

    if master_df.empty or not companies:
        return pd.DataFrame()

    filtered = master_df[
        master_df["Company"].isin(companies)
    ].copy()

    results = []

    for _, row in filtered.iterrows():

        company = row.get("Company")

        # Risk score
        try:
            risk_score = calculate_risk_score(row)
        except:
            risk_score = 50

        risk_category = classify_risk(risk_score)

        results.append({
            "Company": company,
            "Risk Score": risk_score,
            "Risk Category": risk_category,
            "Market Cap": row.get("MarketCap", 0),
            "Revenue": row.get("Revenue", 0),
            "Net Income": row.get("NetIncome", 0),
            "Debt": row.get("Debt", 0),
            "Revenue Growth": row.get("RevenueGrowth", 0),
            "Institutional Ownership": row.get("InstitutionalOwnership", 0)
        })

    return pd.DataFrame(results)


# --------------------------------------------------
# COMPANY RANKING ENGINE
# --------------------------------------------------

def rank_companies(df: pd.DataFrame):
    """
    Rank companies using composite scoring model.
    """

    if df.empty:
        return df

    ranking_df = df.copy()

    ranking_df["Composite Score"] = (
        ranking_df["Revenue Growth"].fillna(0)
        + ranking_df["Institutional Ownership"].fillna(0)
        - ranking_df["Risk Score"].fillna(0)
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

    return ranking_df


# --------------------------------------------------
# INSIDER ACTIVITY COMPARISON
# --------------------------------------------------

def compare_insider_activity(insider_df: pd.DataFrame, companies: list):
    """
    Compare insider trading activity across companies.
    """

    if insider_df.empty:
        return pd.DataFrame()

    results = []

    for company in companies:

        df = insider_df[
            insider_df["Company"] == company
        ] if "Company" in insider_df.columns else pd.DataFrame()

        buy_count = 0
        sell_count = 0

        if not df.empty and "TransactionType" in df.columns:

            buy_count = len(
                df[
                    df["TransactionType"]
                    .astype(str)
                    .str.upper()
                    .str.contains("BUY")
                ]
            )

            sell_count = len(
                df[
                    df["TransactionType"]
                    .astype(str)
                    .str.upper()
                    .str.contains("SELL")
                ]
            )

        results.append({
            "Company": company,
            "Insider Buys": buy_count,
            "Insider Sells": sell_count,
            "Net Flow": buy_count - sell_count
        })

    return pd.DataFrame(results)


# --------------------------------------------------
# HOLDINGS COMPARISON
# --------------------------------------------------

def compare_holdings(holdings_df: pd.DataFrame, companies: list):
    """
    Compare institutional holdings across companies.
    """

    if holdings_df.empty:
        return pd.DataFrame()

    df = holdings_df[
        holdings_df["Company"].isin(companies)
    ].copy()

    if df.empty:
        return pd.DataFrame()

    summary = (
        df.groupby("Company")
        .agg(
            TotalInstitutions=("Company", "count"),
            AvgOwnership=("OwnershipPercent", "mean") if "OwnershipPercent" in df.columns else ("Company", "count")
        )
        .reset_index()
    )

    return summary


# --------------------------------------------------
# MULTI-DIMENSION SCORING
# --------------------------------------------------

def multi_factor_score(row: pd.Series):
    """
    Advanced composite scoring model for ranking.
    """

    score = 0

    try:
        # Growth
        growth = float(row.get("RevenueGrowth", 0) or 0)
        score += growth * 0.4

        # Institutional strength
        inst = float(row.get("InstitutionalOwnership", 0) or 0)
        score += inst * 0.3

        # Risk penalty
        risk = calculate_risk_score(row)
        score -= risk * 0.5

        # Market cap stability
        mcap = float(row.get("MarketCap", 0) or 0)
        if mcap > 1e11:
            score += 10
        elif mcap < 1e9:
            score -= 10

    except:
        pass

    return round(score, 2)


# --------------------------------------------------
# BEST WORST COMPARISON
# --------------------------------------------------

def best_worst(df: pd.DataFrame, metric: str):
    """
    Return best and worst companies for a given metric.
    """

    if df.empty or metric not in df.columns:
        return None, None

    best = df.loc[df[metric].idxmax()]
    worst = df.loc[df[metric].idxmin()]

    return best, worst
```
