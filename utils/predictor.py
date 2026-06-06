 # pages/predictor.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    classification_report
)

from utils.data_loader import load_master_data

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Predictor",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 AI Prediction Engine")
st.caption(
    "Machine Learning Predictions for Institutional Analytics"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def get_data():
    return load_master_data()

df = get_data()

# =====================================================
# DATA OVERVIEW
# =====================================================

st.subheader("Dataset Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", len(df.columns))
c3.metric(
    "Numeric Columns",
    len(
        df.select_dtypes(
            include=np.number
        ).columns
    )
)

# =====================================================
# TARGET SELECTION
# =====================================================

numeric_cols = (
    df.select_dtypes(include=np.number)
    .columns
    .tolist()
)

if len(numeric_cols) < 2:
    st.error(
        "Need at least 2 numerical columns."
    )
    st.stop()

st.sidebar.header("Prediction Settings")

target = st.sidebar.selectbox(
    "Target Variable",
    numeric_cols
)

features = st.sidebar.multiselect(
    "Feature Columns",
    [col for col in numeric_cols if col != target],
    default=[
        col for col in numeric_cols
        if col != target
    ][:5]
)

if len(features) < 1:
    st.warning(
        "Please select at least one feature."
    )
    st.stop()

# =====================================================
# PREPARE DATA
# =====================================================

model_df = df[
    features + [target]
].copy()

model_df = (
    model_df
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
)

model_df = model_df.fillna(
    model_df.median(
        numeric_only=True
    )
)

X = model_df[features]
y = model_df[target]

# =====================================================
# MODEL TYPE
# =====================================================

prediction_type = st.sidebar.radio(
    "Prediction Type",
    [
        "Regression",
        "Classification"
    ]
)

# =====================================================
# TRAIN TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# =====================================================
# REGRESSION MODEL
# =====================================================

if prediction_type == "Regression":

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    st.subheader(
        "📊 Regression Performance"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "MAE",
        f"{mae:.4f}"
    )

    c2.metric(
        "RMSE",
        f"{rmse:.4f}"
    )

    c3.metric(
        "R² Score",
        f"{r2:.4f}"
    )

    # Actual vs Predicted

    results = pd.DataFrame({
        "Actual": y_test,
        "Predicted": predictions
    })

    st.subheader(
        "Actual vs Predicted"
    )

    fig1 = px.scatter(
        results,
        x="Actual",
        y="Predicted",
        title="Prediction Accuracy"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# =====================================================
# CLASSIFICATION MODEL
# =====================================================

else:

    y_class = pd.qcut(
        y,
        q=3,
        labels=[
            "Low",
            "Medium",
            "High"
        ],
        duplicates="drop"
    )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y_class,
            test_size=0.20,
            random_state=42
        )
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    st.subheader(
        "📊 Classification Performance"
    )

    st.metric(
        "Accuracy",
        f"{accuracy:.2%}"
    )

    report = classification_report(
        y_test,
        predictions,
        output_dict=True
    )

    report_df = pd.DataFrame(
        report
    ).transpose()

    st.dataframe(
        report_df,
        use_container_width=True
    )

# =====================================================
# FEATURE IMPORTANCE
# =====================================================

st.subheader(
    "🎯 Feature Importance"
)

importance_df = pd.DataFrame({
    "Feature": features,
    "Importance":
    model.feature_importances_
})

importance_df = (
    importance_df
    .sort_values(
        "Importance",
        ascending=False
    )
)

fig2 = px.bar(
    importance_df,
    x="Feature",
    y="Importance",
    title="Model Feature Importance"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =====================================================
# PREDICTION SIMULATOR
# =====================================================

st.subheader(
    "🧪 Prediction Simulator"
)

user_inputs = {}

for feature in features:

    default_value = float(
        model_df[feature].median()
    )

    user_inputs[feature] = st.number_input(
        feature,
        value=default_value
    )

input_df = pd.DataFrame(
    [user_inputs]
)

prediction = model.predict(
    input_df
)

st.success(
    f"Predicted Value: {prediction[0]}"
)

# =====================================================
# TOP PREDICTIONS
# =====================================================

st.subheader(
    "📈 Sample Predictions"
)

sample = X_test.head(50)

sample_predictions = model.predict(
    sample
)

prediction_df = sample.copy()

prediction_df["Prediction"] = (
    sample_predictions
)

st.dataframe(
    prediction_df,
    use_container_width=True
)

# =====================================================
# AI INSIGHTS
# =====================================================

st.subheader(
    "🤖 AI Insights"
)

top_feature = (
    importance_df
    .iloc[0]["Feature"]
)

st.info(f"""
Target Variable:
{target}

Model Type:
{prediction_type}

Top Predictive Feature:
{top_feature}

Features Used:
{len(features)}

Records Trained:
{len(X_train):,}

Records Tested:
{len(X_test):,}

The prediction engine uses a Random Forest
model to identify patterns in institutional
and market data. Feature importance helps
explain which variables have the strongest
impact on the selected target.
""")

# =====================================================
# DOWNLOAD RESULTS
# =====================================================

st.subheader(
    "📥 Export Results"
)

csv = importance_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Feature Importance",
    csv,
    "feature_importance.csv",
    "text/csv"
)
