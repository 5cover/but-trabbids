"""Application Dash interactive pour l'oral."""

from __future__ import annotations

from datetime import date
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dash_table, dcc, html
from dash.dash_table import FormatTemplate
from dash.dash_table.Format import Format

from src import analysis

MAX_TICKERS = 5
DEFAULT_SYMBOLS = ["AAPL", "QQQ", "TQQQ"]
BACKTEST_START = pd.Timestamp("2020-01-02")
BACKTEST_END = pd.Timestamp("2020-03-31")

PRICES = analysis.load_prices()
RETURNS_WIDE = analysis.load_returns_wide()
SELECTION = analysis.load_selection()
ALL_STATS = analysis.compute_descriptive_stats()


def sanitize_selection(selected: List[str] | None) -> List[str]:
    symbols: List[str] = []
    for symbol in (selected or []):
        symbol = symbol.upper()
        if symbol in RETURNS_WIDE.columns and symbol not in symbols:
            symbols.append(symbol)
    if not symbols:
        symbols = [s for s in DEFAULT_SYMBOLS if s in RETURNS_WIDE.columns]
    warning = ""
    if len(symbols) > MAX_TICKERS:
        warning = f"Sélection limitée à {MAX_TICKERS} tickers pour préserver la lisibilité."
        symbols = symbols[:MAX_TICKERS]
    return symbols, warning


def format_info(symbols: List[str], stats: pd.DataFrame) -> str:
    start = stats["start_date"].min()
    end = stats["end_date"].max()
    return (
        f"{len(symbols)} titres sélectionnés · Période {start} → {end} · "
        "Source : NASDAQ (Kaggle) · Méthode : volume x catégorie"
    )


def build_price_figure(symbols: List[str], mode: str) -> go.Figure:
    data = PRICES[PRICES["Symbol"].isin(symbols)]
    if data.empty:
        return go.Figure()
    y_col = "Adj Close" if mode == "price" else "Normalized"
    title = "Prix ajustés" if mode == "price" else "Indices base 100"
    fig = px.line(
        data,
        x="Date",
        y=y_col,
        color="Symbol",
        hover_data={"SecurityName": True},
        template="plotly_white",
        title=title,
    )
    fig.update_layout(legend_title_text="Ticker")
    if mode == "price":
        fig.update_yaxes(title="Adj Close ($)")
    else:
        fig.update_yaxes(title="Base 100 (début période)")
    return fig


def stats_table_columns() -> List[dict]:
    return [
        {"name": "Ticker", "id": "Symbol"},
        {"name": "Nom", "id": "Security Name"},
        {
            "name": "μ annualisé",
            "id": "mean_annual_return",
            "type": "numeric",
            "format": FormatTemplate.percentage(1),
        },
        {
            "name": "σ annualisé",
            "id": "vol_annual",
            "type": "numeric",
            "format": FormatTemplate.percentage(1),
        },
        {
            "name": "μ/σ",
            "id": "return_risk_ratio",
            "type": "numeric",
            "format": Format(precision=2),
        },
        {
            "name": "Volume moyen",
            "id": "avg_volume",
            "type": "numeric",
            "format": Format(precision=0, group=True),
        },
        {
            "name": "Volume total",
            "id": "total_volume",
            "type": "numeric",
            "format": Format(precision=0, group=True),
        },
    ]


def build_risk_scatter(stats: pd.DataFrame) -> go.Figure:
    df = stats.copy()
    df["Rendement (%)"] = df["mean_annual_return"] * 100
    df["Risque (%)"] = df["vol_annual"] * 100
    fig = px.scatter(
        df,
        x="Risque (%)",
        y="Rendement (%)",
        size="return_risk_ratio",
        color="Symbol",
        hover_name="Security Name",
        template="plotly_white",
    )
    fig.update_traces(mode="markers+text", text=df["Symbol"], textposition="top center")
    fig.update_layout(title="Nuage risque vs rendement", showlegend=False)
    return fig


def build_corr_heatmap(symbols: List[str]) -> go.Figure:
    matrix = analysis.correlation_matrix(symbols)
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=matrix.columns,
            y=matrix.index,
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            colorbar=dict(title="Corrélation"),
        )
    )
    fig.update_layout(
        template="plotly_white",
        title="Matrice de corrélation",
        xaxis_title="",
        yaxis_title="",
    )
    return fig


def build_weights_chart(solution: analysis.PortfolioSolution) -> go.Figure:
    df = solution.weights.reset_index()
    df.columns = ["Symbol", "Weight"]
    fig = px.bar(
        df,
        x="Symbol",
        y="Weight",
        text="Weight",
        template="plotly_white",
        title="Poids du portefeuille",
    )
    fig.update_traces(texttemplate="%{text:.1%}")
    fig.update_yaxes(tickformat=".0%", range=[0, min(1, df["Weight"].max() * 1.2)])
    return fig


def build_metrics(solution: analysis.PortfolioSolution) -> html.Div:
    cards = [
        ("Rendement annualisé", f"{solution.expected_return_annual:.1%}"),
        ("Volatilité annualisée", f"{solution.volatility_annual:.1%}"),
        ("Ratio μ/σ", f"{solution.ratio:.2f}"),
    ]
    return html.Div(
        [
            html.Div(
                [html.Span(label, className="metric-label"), html.H3(value)],
                className="metric-card",
            )
            for label, value in cards
        ],
        className="metric-grid",
    )


def build_frontier_figure(
    solution: analysis.PortfolioSolution,
    stats: pd.DataFrame,
    model: analysis.MarkowitzModel,
) -> go.Figure:
    frontier = model.efficient_frontier()
    if not frontier:
        return go.Figure()

    frontier_df = pd.DataFrame(
        {
            "Risque": [pt.volatility_annual for pt in frontier],
            "Rendement": [pt.expected_return_annual for pt in frontier],
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frontier_df["Risque"],
            y=frontier_df["Rendement"],
            mode="lines+markers",
            name="Frontière efficiente",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=stats["vol_annual"],
            y=stats["mean_annual_return"],
            mode="markers",
            marker=dict(size=10, color="grey"),
            name="Titres",
            text=stats["Symbol"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[solution.volatility_annual],
            y=[solution.expected_return_annual],
            mode="markers",
            marker=dict(size=14, color="#ff5722"),
            name="Portefeuille optimisé",
        )
    )
    fig.update_layout(
        title="Frontière moyenne-variance",
        xaxis_title="Risque annualisé",
        yaxis_title="Rendement annualisé",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    )
    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(tickformat=".0%")
    return fig


def build_backtest_figure(symbols: List[str], weights: pd.Series) -> go.Figure:
    returns = RETURNS_WIDE[symbols]
    subset = returns.loc[BACKTEST_START:BACKTEST_END].dropna()
    if subset.empty:
        return go.Figure()

    weight_vec = weights.reindex(symbols).fillna(0).values
    optimized = subset.mul(weight_vec).sum(axis=1)
    equal = subset.mul(1 / len(symbols)).sum(axis=1)

    bench_symbol = "QQQ" if "QQQ" in subset.columns else symbols[0]
    benchmark = subset[bench_symbol]

    def to_index(series: pd.Series) -> pd.Series:
        return (1 + series).cumprod() * 100

    df = pd.DataFrame(
        {
            "Date": subset.index,
            "Optimisé": to_index(optimized),
            "Égalitaire": to_index(equal),
            f"Benchmark ({bench_symbol})": to_index(benchmark),
        }
    )

    fig = go.Figure()
    for column in df.columns[1:]:
        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[column],
                mode="lines",
                name=column,
            )
        )
    fig.update_layout(
        title="Backtest Jan-Mars 2020 (indice base 100)",
        template="plotly_white",
        yaxis_title="Indice (base 100)",
    )
    return fig


ticker_options = [
    {
        "label": f"{row['Symbol']} — {row['Security Name']} ({row['Market Category'] or 'Unk.'})",
        "value": row["Symbol"],
    }
    for _, row in SELECTION.iterrows()
]

app = Dash(__name__)
app.title = "Portefeuille NASDAQ"
server = app.server

app.layout = html.Div(
    [
        html.H1("Portefeuille NASDAQ pré-Covid"),
        html.P(
            "Sélectionnez jusqu'à cinq actions/ETF pour explorer les métriques, "
            "les corrélations et optimiser votre portefeuille moyenne-variance.",
            className="subtitle",
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="ticker-dropdown",
                    options=ticker_options,
                    value=[s for s in DEFAULT_SYMBOLS if s in RETURNS_WIDE.columns],
                    multi=True,
                    placeholder="Choisir jusqu'à 5 tickers",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("Visualisation :"),
                                dcc.RadioItems(
                                    id="price-mode",
                                    options=[
                                        {"label": "Prix", "value": "price"},
                                        {"label": "Rendement cumulatif", "value": "normalized"},
                                    ],
                                    value="normalized",
                                    inline=True,
                                ),
                            ],
                            className="control-block",
                        ),
                        html.Div(
                            [
                                html.Span("Mode portefeuille :"),
                                dcc.RadioItems(
                                    id="portfolio-mode",
                                    options=[
                                        {"label": "Variance minimale", "value": "min"},
                                        {"label": "Cible rendement", "value": "target"},
                                    ],
                                    value="target",
                                    inline=True,
                                ),
                            ],
                            className="control-block",
                        ),
                        html.Div(
                            [
                                html.Span("Rendement annuel cible"),
                                dcc.Slider(
                                    id="target-return-slider",
                                    min=0.0,
                                    max=1.0,
                                    step=0.02,
                                    value=0.20,
                                    marks={
                                        0.0: "0%",
                                        0.2: "20%",
                                        0.4: "40%",
                                        0.6: "60%",
                                        0.8: "80%",
                                        1.0: "100%",
                                    },
                                ),
                            ],
                            className="control-block",
                        ),
                        html.Button("Optimiser", id="optimize-button", className="primary"),
                    ],
                    className="controls-grid",
                ),
            ],
            className="controls-wrapper",
        ),
        html.Div(id="warning-banner", className="warning"),
        html.Div(id="selection-info", className="selection-info"),
        html.Div(
            [
                dcc.Graph(id="price-graph", className="card"),
                dash_table.DataTable(
                    id="stats-table",
                    columns=stats_table_columns(),
                    data=[],
                    page_size=10,
                    sort_action="native",
                    style_table={"height": "400px", "overflowY": "auto"},
                ),
            ],
            className="grid two",
        ),
        html.Div(
            [
                dcc.Graph(id="risk-graph", className="card"),
                dcc.Graph(id="correlation-graph", className="card"),
            ],
            className="grid two",
        ),
        html.Div(
            [
                dcc.Graph(id="weights-graph", className="card"),
                html.Div(id="portfolio-metrics", className="card metrics-card"),
            ],
            className="grid two",
        ),
        html.Div(
            [
                dcc.Graph(id="frontier-graph", className="card"),
                dcc.Graph(id="backtest-graph", className="card"),
            ],
            className="grid two",
        ),
    ],
    className="app-container",
)


@callback(
    Output("price-graph", "figure"),
    Output("stats-table", "data"),
    Output("selection-info", "children"),
    Output("risk-graph", "figure"),
    Output("correlation-graph", "figure"),
    Output("weights-graph", "figure"),
    Output("portfolio-metrics", "children"),
    Output("frontier-graph", "figure"),
    Output("backtest-graph", "figure"),
    Output("warning-banner", "children"),
    Input("ticker-dropdown", "value"),
    Input("price-mode", "value"),
    Input("portfolio-mode", "value"),
    Input("target-return-slider", "value"),
    Input("optimize-button", "n_clicks"),
)
def update_dashboard(selected, price_mode, mode, target_return, _):
    symbols, warning = sanitize_selection(selected)
    stats = analysis.compute_descriptive_stats(symbols)
    price_fig = build_price_figure(symbols, price_mode)
    info = format_info(symbols, stats)
    risk_fig = build_risk_scatter(stats)
    corr_fig = build_corr_heatmap(symbols)

    try:
        model = analysis.MarkowitzModel.from_symbols(symbols)
        if mode == "min":
            solution = model.minimum_variance()
        else:
            solution = model.optimize(target_annual_return=target_return)
    except Exception as exc:  # pragma: no cover - affichage utilisateur
        warning = f"{warning} Optimisation impossible: {exc}"
        empty_fig = go.Figure()
        return (
            price_fig,
            stats.to_dict("records"),
            info,
            risk_fig,
            corr_fig,
            empty_fig,
            html.Div("Sélectionner au moins deux titres."),
            empty_fig,
            empty_fig,
            warning,
        )

    weights_fig = build_weights_chart(solution)
    metrics = build_metrics(solution)
    frontier_fig = build_frontier_figure(solution, stats, model)
    backtest_fig = build_backtest_figure(symbols, solution.weights)

    return (
        price_fig,
        stats.to_dict("records"),
        info,
        risk_fig,
        corr_fig,
        weights_fig,
        metrics,
        frontier_fig,
        backtest_fig,
        warning,
    )


if __name__ == "__main__":
    app.run(debug=True)
