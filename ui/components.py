"""Reusable Streamlit / Plotly UI pieces."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

from i18n.translations import get_feature_name, t
from ui import charts


def risk_badge(level: str, score: float, lang: str = "fr") -> str:
    pct = f"{score * 100:.0f}%"
    if level == "HIGH":
        return f"🔴 {t('high_risk', lang)} ({pct})"
    if level == "MEDIUM":
        return f"🟡 {t('medium_risk', lang)} ({pct})"
    return f"🟢 {t('low_risk', lang)} ({pct})"


def metric_cards(
    accuracy: float,
    auc: float,
    recall: float,
    precision: float,
    lang: str = "fr",
) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("metric_accuracy", lang), f"{accuracy * 100:.1f}%")
    c2.metric("AUC", f"{auc:.3f}")
    c3.metric(t("metric_recall", lang), f"{recall * 100:.1f}%")
    c4.metric(t("metric_precision", lang), f"{precision * 100:.1f}%")


def model_leaderboard(
    df: pd.DataFrame,
    best_name: Optional[str] = None,
    *,
    lang: str = "fr",
    chart_key: str = "leaderboard_auc_chart",
) -> None:
    fig = charts.leaderboard_table_figure(df, best_name, lang=lang)
    st.plotly_chart(fig, width="stretch", key=chart_key)


def model_comparison_chart(
    df: pd.DataFrame,
    *,
    lang: str = "fr",
    chart_key: str = "model_comparison_chart",
) -> None:
    st.plotly_chart(
        charts.model_comparison_chart(
            df,
            title=t("chart_model_comparison", lang),
            x_label=t("chart_axis_auc", lang),
            y_label=t("chart_axis_model", lang),
        ),
        width="stretch",
        key=chart_key,
    )


def risk_distribution_pie(
    predictions: pd.DataFrame,
    *,
    lang: str = "fr",
    chart_key: str = "risk_distribution_pie",
) -> None:
    label_map = {
        "HIGH": t("high_risk", lang),
        "MEDIUM": t("medium_risk", lang),
        "LOW": t("low_risk", lang),
    }
    st.plotly_chart(
        charts.risk_distribution_pie(
            predictions,
            label_map=label_map,
            title=t("chart_patient_risk_mix", lang),
            empty_text=t("chart_no_risk_levels", lang),
        ),
        width="stretch",
        key=chart_key,
    )


def _rename_patient_table_columns(view: pd.DataFrame, lang: str) -> pd.DataFrame:
    out = view.copy()
    rename: dict[str, str] = {}
    for c in out.columns:
        cs = str(c).lower()
        if cs == "risk_score":
            rename[c] = t("col_risk_score", lang)
        elif cs == "risk_level":
            rename[c] = t("col_risk_level", lang)
        elif cs in ("patient_id", "id"):
            rename[c] = t("col_patient_id", lang)
        elif cs == "alert":
            rename[c] = t("col_alert", lang)
        else:
            rename[c] = get_feature_name(str(c), lang)
    out.columns = [rename.get(c, c) for c in out.columns]
    return out


def patient_risk_table(
    predictions: pd.DataFrame,
    max_rows: int = 200,
    *,
    lang: str = "fr",
) -> None:
    view = predictions.head(max_rows).copy()
    if "risk_level" in view.columns and "risk_score" in view.columns:
        view["alert"] = [
            risk_badge(str(r), float(s), lang=lang) for r, s in zip(view["risk_level"], view["risk_score"])
        ]
    view = _rename_patient_table_columns(view, lang)
    st.dataframe(view, use_container_width=True, hide_index=True)


def shap_explanation_display(fig: Any, lang: str = "fr") -> None:
    if fig is None:
        return
    try:
        st.pyplot(fig, clear_figure=False)
    except Exception:
        try:
            st.write(fig)
        except Exception:
            st.info(t("explanation_display_error", lang))


def feature_importance_chart(
    importance_df: pd.DataFrame,
    *,
    lang: str = "fr",
    chart_key: str = "feature_importance_chart",
) -> None:
    def label_for_factor(name: str) -> str:
        return get_feature_name(str(name), lang)

    st.plotly_chart(
        charts.feature_importance_chart(
            importance_df,
            title=t("chart_top_risk_factors", lang),
            strength_label=t("chart_strength", lang),
            factor_label=t("chart_factor", lang),
            label_for_factor=label_for_factor,
        ),
        width="stretch",
        key=chart_key,
    )
