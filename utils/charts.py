import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# TOP HOLDINGS BAR CHART
# --------------------------------------------------

def top_holdings_chart(df, top_n=10):

    if (
        df.empty or
        "issuer_name" not in df.columns or
        "market_value" not in df.columns
    ):
        return go.Figure()

    data = (
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

    fig = px.bar(
        data,
        x="issuer_name",
        y="market_value",
        color="market_value",
        title="Top Holdings"
    )

    return fig

# --------------------------------------------------
# TREEMAP
# --------------------------------------------------

def holdings_treemap(df):

    if (
        df.empty or
        "issuer_name" not in df.columns or
        "market_value" not in df.columns
    ):
        return go.Figure()

    data = (
        df.groupby("issuer_name")
        ["market_value"]
        .sum()
        .reset_index()
    )

    fig = px.treemap(
        data,
        path=["issuer_name"],
        values="market_value",
        title="Portfolio Treemap"
    )

    return fig

# --------------------------------------------------
# CONVICTION SCORE HISTOGRAM
# --------------------------------------------------

def conviction_histogram(df):

    if (
        df.empty or
        "conviction_score"
        not in df.columns
    ):
        return go.Figure()

    fig = px.histogram(
        df,
        x="conviction_score",
        nbins=20,
        title="Conviction Score Distribution"
    )

    return fig

# --------------------------------------------------
# BUY VS SELL PIE CHART
# --------------------------------------------------

def insider_pie_chart(df):

    if (
        df.empty or
        "transaction_code"
        not in df.columns
    ):
        return go.Figure()

    data = (
        df["transaction_code"]
        .value_counts()
        .reset_index()
    )

    data.columns = [
        "Transaction",
        "Count"
    ]

    fig = px.pie(
        data,
        names="Transaction",
        values="Count",
        hole=0.4,
        title="Buy vs Sell Activity"
    )

    return fig

# --------------------------------------------------
# SIGNAL STRENGTH BAR CHART
# --------------------------------------------------

def signal_strength_chart(df, top_n=15):

    if (
        df.empty or
        "signal_strength"
        not in df.columns
    ):
        return go.Figure()

    data = (
        df.sort_values(
            "signal_strength",
            ascending=False
        )
        .head(top_n)
    )

    fig = px.bar(
        data,
        x="issuer_name",
        y="signal_strength",
        color="signal_strength",
        title="Top Smart Money Signals"
    )

    return fig

# --------------------------------------------------
# RECOMMENDATION PIE CHART
# --------------------------------------------------

def recommendation_chart(df):

    if (
        df.empty or
        "recommendation"
        not in df.columns
    ):
        return go.Figure()

    fig = px.pie(
        df,
        names="recommendation",
        hole=0.4,
        title="Recommendations"
    )

    return fig

# --------------------------------------------------
# SIGNAL VS RISK SCATTER
# --------------------------------------------------

def signal_vs_risk_chart(df):

    if (
        df.empty or
        "signal_strength"
        not in df.columns or
        "risk_score"
        not in df.columns
    ):
        return go.Figure()

    fig = px.scatter(
        df,
        x="risk_score",
        y="signal_strength",
        size="signal_strength",
        color="recommendation"
        if "recommendation" in df.columns
        else None,
        hover_name="issuer_name"
        if "issuer_name" in df.columns
        else None,
        title="Signal Strength vs Risk"
    )

    return fig

# --------------------------------------------------
# SECTOR PERFORMANCE
# --------------------------------------------------

def sector_performance_chart(df):

    if (
        df.empty or
        "sector" not in df.columns or
        "signal_strength"
        not in df.columns
    ):
        return go.Figure()

    data = (
        df.groupby("sector")
        ["signal_strength"]
        .mean()
        .reset_index()
        .sort_values(
            "signal_strength",
            ascending=False
        )
    )

    fig = px.bar(
        data,
        x="sector",
        y="signal_strength",
        color="signal_strength",
        title="Sector Performance"
    )

    return fig

# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------

def correlation_heatmap(df):

    numeric_df = (
        df.select_dtypes(
            include="number"
        )
    )

    if numeric_df.empty:
        return go.Figure()

    corr = numeric_df.corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        title="Correlation Matrix"
    )

    return fig

# --------------------------------------------------
# CONVICTION VS MARKET VALUE
# --------------------------------------------------

def conviction_vs_market_chart(df):

    if (
        df.empty or
        "conviction_score"
        not in df.columns or
        "market_value"
        not in df.columns
    ):
        return go.Figure()

    fig = px.scatter(
        df,
        x="conviction_score",
        y="market_value",
        size="market_value",
        color="conviction_score",
        hover_name="issuer_name"
        if "issuer_name" in df.columns
        else None,
        title="Conviction vs Market Value"
    )

    return fig

# --------------------------------------------------
# RADAR CHART
# --------------------------------------------------

def radar_chart(df):

    required = [
        "signal_strength",
        "risk_score",
        "conviction_score"
    ]

    if (
        df.empty or
        not all(
            col in df.columns
            for col in required
        )
    ):
        return go.Figure()

    avg_signal = (
        df["signal_strength"]
        .mean()
    )

    avg_risk = (
        df["risk_score"]
        .mean()
    )

    avg_conviction = (
        df["conviction_score"]
        .mean()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=[
                avg_signal,
                avg_conviction,
                avg_risk
            ],
            theta=[
                "Signal Strength",
                "Conviction",
                "Risk Score"
            ],
            fill="toself"
        )
    )

    fig.update_layout(
        title="Smart Money Radar",
        showlegend=False
    )

    return fig

# --------------------------------------------------
# COMPANY HOLDINGS CHART
# --------------------------------------------------

def company_holdings_chart(df, company):

    if (
        df.empty or
        "issuer_name"
        not in df.columns
    ):
        return go.Figure()

    data = df[
        df["issuer_name"]
        == company
    ]

    if data.empty:
        return go.Figure()

    fig = px.bar(
        data,
        y="market_value",
        title=f"{company} Holdings"
    )

    return fig

# --------------------------------------------------
# MARKET VALUE HISTOGRAM
# --------------------------------------------------

def market_value_histogram(df):

    if (
        df.empty or
        "market_value"
        not in df.columns
    ):
        return go.Figure()

    fig = px.histogram(
        df,
        x="market_value",
        nbins=25,
        title="Market Value Distribution"
    )

    return fig

# --------------------------------------------------
# VOTING SHARES CHART
# --------------------------------------------------

def voting_shares_chart(df):

    if (
        df.empty or
        "voting_shares"
        not in df.columns
    ):
        return go.Figure()

    data = (
        df.groupby("issuer_name")
        ["voting_shares"]
        .sum()
        .reset_index()
        .sort_values(
            "voting_shares",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        data,
        x="issuer_name",
        y="voting_shares",
        color="voting_shares",
        title="Voting Shares"
    )

    return fig

# --------------------------------------------------
# DASHBOARD KPI FIGURE
# --------------------------------------------------

def empty_chart():

    fig = go.Figure()

    fig.update_layout(
        template="plotly_white"
    )

    return fig
