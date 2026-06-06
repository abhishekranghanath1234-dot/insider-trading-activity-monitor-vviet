```python id="risk_scoring_utils_001"
# utils/risk_scoring.py

import numpy as np
import pandas as pd

# --------------------------------------------------
# RISK CLASSIFICATION
# --------------------------------------------------

def classify_risk(score: float) -> str:
    """
    Convert numeric risk score into category.
    """
    try:
        score = float(score)
    except:
        return "Unknown"

    if score <= 30:
        return "Low Risk"
    elif score <= 60:
        return "Medium Risk"
    else:
        return "High Risk"


# --------------------------------------------------
# CORE RISK ENGINE
# --------------------------------------------------

def calculate_risk_score(row: pd.Series) -> float:
    """
    AI-style heuristic risk scoring engine based on:
    - Debt
    - Revenue growth
    - Institutional ownership
    - Insider signals (optional if available)
    """

    score = 50  # baseline risk

    # -----------------------------
    # Debt Risk
    # -----------------------------
    try:
        debt = float(row.get("Debt", 0) or 0)

        if debt > 5e9:
            score += 20
        elif debt > 1e9:
            score += 10
        elif debt > 5e8:
            score += 5
        else:
            score -= 5
    except:
        pass

    # -----------------------------
    # Revenue Growth Risk
    # -----------------------------
    try:
        growth = float(row.get("RevenueGrowth", 0) or 0)

        if growth < 0:
            score += 20
        elif growth < 5:
            score += 10
        elif growth > 20:
            score -= 10
    except:
        pass

    # -----------------------------
    # Institutional Ownership
    # -----------------------------
    try:
        inst = float(row.get("InstitutionalOwnership", 0) or 0)

        if inst < 10:
            score += 15
        elif inst < 25:
            score += 8
        elif inst > 60:
            score -= 10
    except:
        pass

    # -----------------------------
    # Market Cap Stability Proxy
    # -----------------------------
    try:
        mcap = float(row.get("MarketCap", 0) or 0)

        if mcap < 1e9:
            score += 10
        elif mcap > 1e11:
            score -= 5
    except:
        pass

    # -----------------------------
    # Insider Sentiment (if present)
    # -----------------------------
    try:
        buy = float(row.get("InsiderBuyScore", 0) or 0)
        sell = float(row.get("InsiderSellScore", 0) or 0)

        score += (sell * 0.5)
        score -= (buy * 0.3)
    except:
        pass

    # -----------------------------
    # Clamp score
    # -----------------------------
    score = max(0, min(100, score))

    return round(score, 2)


# --------------------------------------------------
# NORMALIZED RISK FACTORS
# --------------------------------------------------

def risk_breakdown(row: pd.Series) -> dict:
    """
    Return individual risk components for explainability.
    """

    breakdown = {}

    # Debt
    debt = float(row.get("Debt", 0) or 0)
    if debt > 5e9:
        breakdown["Debt Risk"] = 20
    elif debt > 1e9:
        breakdown["Debt Risk"] = 10
    else:
        breakdown["Debt Risk"] = 3

    # Revenue Growth
    growth = float(row.get("RevenueGrowth", 0) or 0)
    if growth < 0:
        breakdown["Growth Risk"] = 20
    elif growth < 5:
        breakdown["Growth Risk"] = 10
    else:
        breakdown["Growth Risk"] = 5

    # Institutional Ownership
    inst = float(row.get("InstitutionalOwnership", 0) or 0)
    if inst < 10:
        breakdown["Institutional Risk"] = 15
    elif inst < 25:
        breakdown["Institutional Risk"] = 8
    else:
        breakdown["Institutional Risk"] = 4

    return breakdown
```
