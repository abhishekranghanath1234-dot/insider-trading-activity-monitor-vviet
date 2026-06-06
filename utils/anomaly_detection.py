```python id="anomaly_detection_utils_001"
# utils/anomaly_detection.py

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

def prepare_features(df: pd.DataFrame, feature_cols=None):
    """
    Prepare numeric feature matrix for anomaly detection.
    """

    if feature_cols is None:
        feature_cols = [
            "Shares",
            "TransactionValue",
            "Price",
            "OwnershipPercent",
            "MarketCap"
        ]

    working_df = df.copy()

    numeric_features = []

    for col in feature_cols:
        if col in working_df.columns:
            working_df[col] = pd.to_numeric(
                working_df[col],
                errors="coerce"
            )
            numeric_features.append(col)

    working_df = working_df.dropna(subset=numeric_features)

    return working_df, numeric_features


# --------------------------------------------------
# ANOMALY DETECTION ENGINE
# --------------------------------------------------

def detect_anomalies(
    df: pd.DataFrame,
    contamination: float = 0.05,
    feature_cols=None
):
    """
    Runs Isolation Forest anomaly detection.
    Returns dataframe with anomaly flags and scores.
    """

    working_df, numeric_features = prepare_features(df, feature_cols)

    if len(numeric_features) == 0:
        raise ValueError("No valid numeric features found")

    if len(working_df) < 10:
        raise ValueError("Not enough data for anomaly detection")

    scaler = StandardScaler()
    X = scaler.fit_transform(working_df[numeric_features])

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=200
    )

    model.fit(X)

    predictions = model.predict(X)
    scores = model.decision_function(X)

    working_df["AnomalyFlag"] = predictions
    working_df["AnomalyScore"] = scores

    working_df["RiskLabel"] = np.where(
        working_df["AnomalyFlag"] == -1,
        "Suspicious",
        "Normal"
    )

    return working_df


# --------------------------------------------------
# COMPANY-LEVEL FRAUD AGGREGATION
# --------------------------------------------------

def company_anomaly_summary(df: pd.DataFrame):
    """
    Aggregate anomaly results at company level.
    """

    if df.empty or "Company" not in df.columns:
        return pd.DataFrame()

    summary = (
        df.groupby("Company")
        .agg(
            TotalTransactions=("Company", "count"),
            SuspiciousCount=(
                "RiskLabel",
                lambda x: (x == "Suspicious").sum()
            ),
            AvgAnomalyScore=("AnomalyScore", "mean")
        )
        .reset_index()
    )

    summary["RiskRate"] = (
        summary["SuspiciousCount"]
        / summary["TotalTransactions"]
    ) * 100

    return summary.sort_values(
        by="RiskRate",
        ascending=False
    )


# --------------------------------------------------
# INSIDER-LEVEL ANOMALY SUMMARY
# --------------------------------------------------

def insider_anomaly_summary(df: pd.DataFrame):
    """
    Aggregate anomaly results at insider level.
    """

    if df.empty or "InsiderName" not in df.columns:
        return pd.DataFrame()

    summary = (
        df.groupby("InsiderName")
        .agg(
            Transactions=("InsiderName", "count"),
            Suspicious=("RiskLabel", lambda x: (x == "Suspicious").sum()),
            AvgScore=("AnomalyScore", "mean")
        )
        .reset_index()
    )

    summary["RiskRate"] = (
        summary["Suspicious"]
        / summary["Transactions"]
    ) * 100

    return summary.sort_values(
        by="RiskRate",
        ascending=False
    )


# --------------------------------------------------
# QUICK ANOMALY SCORER (SINGLE ROW)
# --------------------------------------------------

def score_transaction(row: pd.Series) -> float:
    """
    Simple anomaly heuristic score for a single transaction.
    """

    score = 0

    try:
        shares = float(row.get("Shares", 0) or 0)
        value = float(row.get("TransactionValue", 0) or 0)
        price = float(row.get("Price", 0) or 0)

        # Large transaction size risk
        if value > 1e7:
            score += 30
        elif value > 5e6:
            score += 15

        # Abnormal share volume
        if shares > 1e6:
            score += 20
        elif shares > 5e5:
            score += 10

        # Price distortion indicator
        if price > 500:
            score += 10

    except:
        pass

    return min(score, 100)
```
