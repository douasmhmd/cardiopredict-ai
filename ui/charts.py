"""Plotly chart builders for MedPredict AI."""

from __future__ import annotations

from typing import Callable, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from i18n.translations import leaderboard_column_label

CHART_TEXT = "#000000"
CHART_TEMPLATE = dict(
    font=dict(family="Inter, system-ui, sans-serif", color=CHART_TEXT, size=13),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=20, r=20, t=50, b=20),
    colorway=["#0F766E", "#14B8A6", "#5EEAD4", "#99F6E4", "#F59E0B", "#DC2626"],
)


def apply_chart_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        font=CHART_TEMPLATE["font"],
        plot_bgcolor=CHART_TEMPLATE["plot_bgcolor"],
        paper_bgcolor=CHART_TEMPLATE["paper_bgcolor"],
        margin=CHART_TEMPLATE["margin"],
        colorway=CHART_TEMPLATE["colorway"],
        title_font=dict(size=18, color=CHART_TEXT, family="Inter, system-ui, sans-serif"),
        legend=dict(font=dict(color=CHART_TEXT, size=12, family="Inter, system-ui, sans-serif")),
    )
    try:
        fig.update_xaxes(
            gridcolor="#E2E8F0",
            gridwidth=0.5,
            tickfont=dict(color=CHART_TEXT),
            title_font=dict(color=CHART_TEXT),
            linecolor="#94A3B8",
            color=CHART_TEXT,
        )
        fig.update_yaxes(
            gridcolor="#E2E8F0",
            gridwidth=0.5,
            tickfont=dict(color=CHART_TEXT),
            title_font=dict(color=CHART_TEXT),
            linecolor="#94A3B8",
            color=CHART_TEXT,
        )
    except Exception:
        pass
    try:
        fig.update_traces(
            textfont=dict(color=CHART_TEXT, family="Inter, system-ui, sans-serif", size=12),
            selector=dict(type="bar"),
        )
    except Exception:
        pass
    return fig


def model_comparison_chart(
    leaderboard: pd.DataFrame,
    auc_col: str = "AUC",
    *,
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
) -> go.Figure:
    df = leaderboard.copy()
    if auc_col not in df.columns:
        auc_col = df.select_dtypes(include=["float", "int"]).columns[0] if len(df.columns) else "AUC"
    df["_model"] = df["Model"].astype(str) if "Model" in df.columns else df.index.astype(str)
    df = df.sort_values(auc_col, ascending=True)
    fig = px.bar(
        df,
        x=auc_col,
        y="_model",
        orientation="h",
        title=title or "Model comparison (AUC)",
        labels={
            auc_col: x_label or "AUC",
            "_model": y_label or "Model",
        },
    )
    fig.update_layout(height=max(320, 28 * len(df)))
    return apply_chart_theme(fig)


def risk_distribution_pie(
    predictions: pd.DataFrame,
    level_col: str = "risk_level",
    *,
    label_map: Optional[dict[str, str]] = None,
    title: Optional[str] = None,
    empty_text: Optional[str] = None,
) -> go.Figure:
    if level_col not in predictions.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=empty_text or "No risk levels yet",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(family="Inter, system-ui, sans-serif", color="#64748B", size=14),
        )
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", margin=dict(l=20, r=20, t=40, b=20))
        return apply_chart_theme(fig)
    counts = predictions[level_col].value_counts().reindex(["HIGH", "MEDIUM", "LOW"]).fillna(0)
    labels = [label_map.get(str(i), str(i)) if label_map else str(i) for i in counts.index]
    colors = {"HIGH": "#DC2626", "MEDIUM": "#F59E0B", "LOW": "#16A34A"}
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=counts.values.tolist(),
                marker=dict(colors=[colors.get(str(i), "#888") for i in counts.index]),
                hole=0.35,
                textfont=dict(color=CHART_TEXT, family="Inter, system-ui, sans-serif", size=13),
                insidetextfont=dict(color=CHART_TEXT),
                outsidetextfont=dict(color=CHART_TEXT),
            )
        ]
    )
    fig.update_layout(title=title or "Patient risk mix", height=360, margin=dict(t=50, b=20, l=20, r=20))
    return apply_chart_theme(fig)


def feature_importance_chart(
    importance_df: pd.DataFrame,
    *,
    title: Optional[str] = None,
    strength_label: Optional[str] = None,
    factor_label: Optional[str] = None,
    label_for_factor: Optional[Callable[[str], str]] = None,
) -> go.Figure:
    df = importance_df.head(15).iloc[::-1].copy()
    if label_for_factor is not None and "factor" in df.columns:
        df["factor"] = df["factor"].astype(str).map(lambda x: label_for_factor(x) or x)
    fig = px.bar(
        df,
        x="importance",
        y="factor",
        orientation="h",
        title=title or "Top risk factors (model importance)",
        labels={
            "importance": strength_label or "Strength",
            "factor": factor_label or "Factor",
        },
    )
    fig.update_layout(height=max(300, 22 * len(df)))
    return apply_chart_theme(fig)


def leaderboard_table_figure(
    leaderboard: pd.DataFrame,
    best_model_name: Optional[str] = None,
    *,
    lang: str = "fr",
) -> go.Figure:
    show = leaderboard.copy()
    if "Model" not in show.columns:
        show.insert(0, "Model", show.index.astype(str))
    cols = [c for c in show.columns if c != "Model"][:8]
    display_cols = ["Model"] + cols
    show = show[display_cols].head(15)
    header_labels = [leaderboard_column_label(c, lang) for c in show.columns]
    header = dict(
        values=header_labels,
        fill_color="#CCFBF1",
        font=dict(color=CHART_TEXT, size=12, family="Inter, system-ui, sans-serif"),
        align="left",
        line=dict(color="#94A3B8", width=1),
    )
    row_colors: list[list[str]] = []
    for m in show["Model"].astype(str):
        if best_model_name and m.lower().strip() == str(best_model_name).lower().strip():
            row_colors.append(["#CCFBF1"] * len(show.columns))
        else:
            row_colors.append(["#ffffff"] * len(show.columns))
    fill_by_col = [[row_colors[r][c] for r in range(len(show))] for c in range(len(show.columns))]
    cells = dict(
        values=[show[c] for c in show.columns],
        fill=dict(color=fill_by_col),
        align="left",
        font=dict(color=CHART_TEXT, size=12, family="Inter, system-ui, sans-serif"),
    )
    fig = go.Figure(data=[go.Table(header=header, cells=cells)])
    fig.update_layout(
        height=min(520, 40 + 28 * len(show)),
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="white",
        font=dict(family="Inter, system-ui, sans-serif", color=CHART_TEXT, size=13),
    )
    return fig
