```python id="predictor_utils_001"
# utils/predictor.py

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

def prepare_prediction_features(df: pd.DataFrame):
    """
    Prepare features for smart money prediction model.
    """

    features = [
        "InsiderBuyScore",
        "InsiderSellScore",
        "InstitutionalOwnership",
        "RevenueGrowth",
        "Debt",
        "MarketCap"
    ]

    working_df = df.copy()

    used_features = []

    for col in features:
        if col in working_df.columns:
            working_df[col] = pd.to_numeric(
                working_df[col],
                errors="coerce"
            )
            used_features.append(col)

    working_df = working_df.dropna(subset=used_features)

    return working_df, used_features


# --------------------------------------------------
# TRAIN / PREDICT MODEL
# --------------------------------------------------

def train_model(df: pd.DataFrame):
    """
    Train RandomForest model for smart money prediction.
    """

    working_df, features = prepare_prediction_features(df)

    if len(features) == 0:
        raise ValueError("No valid features found")

    # Synthetic label creation (if no target exists)
    # Bullish = low risk + high insider buying
    y = np.where(
        (working_df.get("InsiderBuyScore", 0) > working_df.get("InsiderSellScore", 0))
        & (working_df.get("RevenueGrowth", 0) > 0),
        1,
        0
    )

    X = working_df[features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_scaled, y)

    return model, scaler, features


# --------------------------------------------------
# PREDICTION ENGINE
# --------------------------------------------------

def predict_signal(model, scaler, features, df: pd.DataFrame):
    """
    Predict bullish/bearish signal.
    """

    working_df = df.copy()

    for col in features:
        working_df[col] = pd.to_numeric(
            working_df[col],
            errors="coerce"
        )

    working_df = working_df.dropna(subset=features)

    X = scaler.transform(working_df[features])

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)

    working_df["Signal"] = np.where(
        predictions == 1,
        "Bullish",
        "Bearish"
    )

    working_df["BullishProb"] = probabilities[:, 1]
    working_df["BearishProb"] = probabilities[:, 0]

    return working_df


# --------------------------------------------------
# SINGLE COMPANY PREDICTION
# --------------------------------------------------

def predict_company_signal(row: pd.Series):
    """
    Lightweight heuristic fallback predictor (no ML required).
    """

    score = 0

    try:
        buy = float(row.get("InsiderBuyScore", 0) or 0)
        sell = float(row.get("InsiderSellScore", 0) or 0)
        growth = float(row.get("RevenueGrowth", 0) or 0)
        inst = float(row.get("InstitutionalOwnership", 0) or 0)
        debt = float(row.get("Debt", 0) or 0)

        # Insider sentiment
        if buy > sell:
            score += 30
        else:
            score -= 20

        # Growth
        if growth > 10:
            score += 25
        elif growth < 0:
            score -= 25

        # Institutional support
        if inst > 50:
            score += 15
        elif inst < 20:
            score -= 10

        # Debt penalty
        if debt > 1e9:
            score -= 20

    except:
        pass

    if score >= 20:
        signal = "Bullish"
        confidence = min(95, 60 + score)
    elif score <= -10:
        signal = "Bearish"
        confidence = min(90, 60 + abs(score))
    else:
        signal = "Neutral"
        confidence = 55

    return {
        "Signal": signal,
        "Confidence": round(confidence, 2),
        "Score": round(score, 2)
    }


# --------------------------------------------------
# FEATURE IMPORTANCE (EXPLAINABILITY)
# --------------------------------------------------

def feature_importance(model, features):
    """
    Return feature importance from trained model.
    """

    try:
        importance = model.feature_importances_

        return pd.DataFrame({
            "Feature": features,
            "Importance": importance
        }).sort_values(
            by="Importance",
            ascending=False
        )
    except:
        return pd.DataFrame()
```
