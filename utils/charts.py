import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# GLOBAL THEME
# =====================================================

PLOT_THEME = "plotly_dark"

# =====================================================
# TOP HOLDINGS BAR CHART
# =====================================================

def top_holdings_chart(df):

    required = [
        "company_name",
        "market_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return go.Figure()

    chart_df = (
        df.groupby("company_name")
        ["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        chart_df,
        x="market_value",
        y="company_name",
        orientation="h",
        template=PLOT_THEME,
        title="Top Holdings"
    )

    fig.update_layout(height=550)

    return fig


# =====================================================
# CONVICTION HISTOGRAM
# =====================================================

def conviction_histogram(df):

    if "conviction_score" not in df.columns:
        return go.Figure()

    fig = px.histogram(
        df,
        x="conviction_score",
        nbins=30,
        template=PLOT_THEME,
        title="Conviction Score Distribution"
    )

    return fig


# =====================================================
# TREEMAP
# =====================================================

def holdings_treemap(df):

    required = [
        "company_name",
        "market_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return go.Figure()

    chart_df = (
        df.groupby("company_name")
        ["market_value"]
        .sum()
        .reset_index()
    )

    fig = px.treemap(
        chart_df,
        path=["company_name"],
        values="market_value",
        template=PLOT_THEME,
        title="Portfolio Allocation"
    )

    fig.update_layout(height=700)

    return fig


# =====================================================
# BUBBLE CHART
# =====================================================

def conviction_vs_market_value(df):

    required = [
        "market_value",
        "conviction_score"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return go.Figure()

    fig = px.scatter(
        df,
        x="conviction_score",
        y="market_value",
        size="market_value",
        hover_data=["company_name"]
        if "company_name" in df.columns
        else None,
        template=PLOT_THEME,
        title="Conviction vs Market Value"
    )

    fig.update_layout(height=650)

    return fig


# =====================================================
# BUY SELL PIE
# =====================================================

def insider_buy_sell_pie(df):

    if "transaction_type" not in df.columns:
        return go.Figure()

    chart_df = (
        df["transaction_type"]
        .value_counts()
        .reset_index()
    )

    chart_df.columns = [
        "Transaction",
        "Count"
    ]

    fig = px.pie(
        chart_df,
        names="Transaction",
        values="Count",
        hole=0.45,
        template=PLOT_THEME,
        title="Buy vs Sell Distribution"
    )

    return fig


# =====================================================
# TOP INSIDER BUYERS
# =====================================================

def top_insider_chart(df):

    required = [
        "owner_name",
        "transaction_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return go.Figure()

    chart_df = (
        df.groupby("owner_name")
        ["transaction_value"]
        .sum()
        .reset_index()
        .sort_values(
            "transaction_value",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        chart_df,
        x="transaction_value",
        y="owner_name",
        orientation="h",
        template=PLOT_THEME,
        title="Top Insider Transactions"
    )

    return fig


# =====================================================
# INSIDER TIMELINE
# =====================================================

def insider_timeline(df):

    required = [
        "transaction_date",
        "transaction_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return go.Figure()

    chart_df = (
        df.groupby("transaction_date")
        ["transaction_value"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        chart_df,
        x="transaction_date",
        y="transaction_value",
        markers=True,
        template=PLOT_THEME,
        title="Insider Activity Timeline"
    )

    return fig


# =====================================================
# INSTITUTIONAL LEADERBOARD
# =====================================================

def institution_chart(df):

    required = [
        "institution_name",
        "market_value"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return go.Figure()

    chart_df = (
        df.groupby("institution_name")
        ["market_value"]
        .sum()
        .reset_index()
        .sort_values(
            "market_value",
            ascending=False
        )
        .head(15)
    )

    fig = px.bar(
        chart_df,
        x="market_value",
        y="institution_name",
        orientation="h",
        template=PLOT_THEME,
        title="Top Institutions"
    )

    return fig


# =====================================================
# SECTOR ALLOCATION
# =====================================================

def sector_allocation_chart(df):

    if (
        "sector" not in df.columns
        or "market_value" not in df.columns
    ):
        return go.Figure()

    chart_df = (
        df.groupby("sector")
        ["market_value"]
        .sum()
        .reset_index()
    )

    fig = px.sunburst(
        chart_df,
        path=["sector"],
        values="market_value",
        template=PLOT_THEME,
        title="Sector Allocation"
    )

    return fig


# =====================================================
# SIGNAL DISTRIBUTION
# =====================================================

def signal_distribution(df):

    if "recommendation" not in df.columns:
        return go.Figure()

    chart_df = (
        df["recommendation"]
        .value_counts()
        .reset_index()
    )

    chart_df.columns = [
        "Signal",
        "Count"
    ]

    fig = px.bar(
        chart_df,
        x="Signal",
        y="Count",
        template=PLOT_THEME,
        title="Signal Distribution"
    )

    return fig


# =====================================================
# SIGNAL HEATMAP
# =====================================================

def signal_heatmap(df):

    required = [
        "sector",
        "recommendation"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return go.Figure()

    heatmap_df = pd.crosstab(
        df["sector"],
        df["recommendation"]
    )

    fig = px.imshow(
        heatmap_df,
        text_auto=True,
        aspect="auto",
        template=PLOT_THEME
    )

    fig.update_layout(
        title="Signal Heatmap"
    )

    return fig


# =====================================================
# SIGNAL SCORE HISTOGRAM
# =====================================================

def signal_score_histogram(df):

    if "signal_score" not in df.columns:
        return go.Figure()

    fig = px.histogram(
        df,
        x="signal_score",
        nbins=25,
        template=PLOT_THEME,
        title="Signal Score Distribution"
    )

    return fig


# =====================================================
# OPPORTUNITY MATRIX
# =====================================================

def opportunity_matrix(df):

    required = [
        "conviction_score",
        "insider_score"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return go.Figure()

    fig = px.scatter(
        df,
        x="conviction_score",
        y="insider_score",
        size="signal_score"
        if "signal_score" in df.columns
        else None,
        color="recommendation"
        if "recommendation" in df.columns
        else None,
        hover_data=["company_name"]
        if "company_name" in df.columns
        else None,
        template=PLOT_THEME,
        title="Opportunity Matrix"
    )

    fig.update_layout(height=650)

    return fig


# =====================================================
# WHALE POSITIONS
# =====================================================

def whale_chart(df):

    if "market_value" not in df.columns:
        return go.Figure()

    whales = df[
        df["market_value"]
        >= 1000000000
    ]

    if whales.empty:
        return go.Figure()

    fig = px.bar(
        whales.head(20),
        x="company_name",
        y="market_value",
        template=PLOT_THEME,
        title="Whale Positions"
    )

    return fig


# =====================================================
# KPI GAUGE
# =====================================================

def conviction_gauge(score):

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={
                "text":
                "Average Conviction"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                }
            }
        )
    )

    fig.update_layout(
        template=PLOT_THEME,
        height=350
    )

    return fig
