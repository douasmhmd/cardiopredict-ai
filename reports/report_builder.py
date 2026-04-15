"""Assemble PDF report payload from app session state."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from xml.sax.saxutils import escape as xml_escape

import numpy as np
import pandas as pd

from automl.engine import AutoMLEngine
from chatbot import medical_interpreter as mi
from i18n.translations import get_feature_name, t
from reports.pdf_generator import MedicalReportGenerator


def _top_accuracy_pct(leaderboard: Optional[pd.DataFrame]) -> float:
    if leaderboard is None or len(leaderboard) == 0:
        return 0.0
    row = leaderboard.iloc[0]
    for key in ("Accuracy",):
        if key in row.index:
            try:
                v = float(row[key])
                return v * 100 if v <= 1 else v
            except (TypeError, ValueError):
                break
    return 0.0


def _enrich_predictions(predictions: pd.DataFrame, raw: Optional[pd.DataFrame], target: Optional[str]) -> pd.DataFrame:
    """Align raw clinical columns onto prediction rows by index."""
    out = predictions.copy()
    if raw is None:
        return out
    for col in raw.columns:
        if target and col == target:
            continue
        if col not in out.columns and col in raw.columns:
            try:
                out[col] = raw[col].values[: len(out)]
            except Exception:
                pass
    return out


def _score_series(df: pd.DataFrame) -> pd.Series:
    if "risk_score" in df.columns:
        return pd.to_numeric(df["risk_score"], errors="coerce").fillna(0.0)
    if "prediction_score" in df.columns:
        return pd.to_numeric(df["prediction_score"], errors="coerce").fillna(0.0)
    return pd.Series(0.0, index=df.index)


def build_report_pdf_bytes(
    *,
    lang: str,
    doctor_name: str,
    uploaded_df: Optional[pd.DataFrame],
    target_column: Optional[str],
    predictions: Optional[pd.DataFrame],
    leaderboard: Optional[pd.DataFrame],
    best_model_name: Optional[str],
    automl_engine: Optional[AutoMLEngine],
    cluster_profiles: Optional[pd.DataFrame],
    cluster_labels: Optional[Dict[Any, str]],
    app_version: str = "1.0.0",
) -> Optional[bytes]:
    if predictions is None or len(predictions) == 0:
        return None

    preds = _enrich_predictions(predictions, uploaded_df, target_column)
    score = _score_series(preds)

    n_total = len(preds)
    if "risk_level" in preds.columns:
        n_critical = int((preds["risk_level"] == "HIGH").sum())
        n_warning = int((preds["risk_level"] == "MEDIUM").sum())
        n_safe = int((preds["risk_level"] == "LOW").sum())
    else:
        n_critical = int((score > 0.7).sum())
        n_warning = int(((score > 0.4) & (score <= 0.7)).sum())
        n_safe = int((score <= 0.4).sum())

    n_features = 0
    if uploaded_df is not None and target_column and target_column in uploaded_df.columns:
        n_features = max(0, len(uploaded_df.columns) - 1)
    elif uploaded_df is not None:
        n_features = len(uploaded_df.columns)

    reliability = _top_accuracy_pct(leaderboard)
    n_models = len(leaderboard) if leaderboard is not None else 0
    best = best_model_name or "—"
    best_esc = xml_escape(str(best))

    llm_summary = mi.interpret_risk_distribution(n_critical, n_warning, n_safe, n_total, lang=lang)
    llm_methodology = mi.interpret_methodology(n_models, best, reliability, n_features, lang=lang)
    llm_critical_analysis = mi.interpret_critical_cohort(n_critical, lang=lang)
    llm_watch = mi.interpret_watch_cohort(n_warning, lang=lang)
    llm_phenotypes = mi.interpret_clusters(cluster_profiles, cluster_labels, lang=lang)
    llm_risk_factors = mi.interpret_feature_importance_context(lang=lang)

    fi_df: Optional[pd.DataFrame] = None
    if automl_engine is not None:
        fi_df, ok = automl_engine.get_feature_importance()
        if ok and fi_df is not None and len(fi_df):
            fi_df = fi_df.copy()
            fi_df["label"] = fi_df["factor"].map(lambda x: get_feature_name(str(x), lang))

    strings = _report_strings(
        lang,
        reliability,
        n_features,
        n_models,
        app_version,
        n_critical,
        n_warning,
        best_esc,
        n_total,
    )

    data: Dict[str, Any] = {
        "lang": lang,
        "strings": strings,
        "doctor_name": doctor_name or "—",
        "n_patients": n_total,
        "n_critical": n_critical,
        "n_warning": n_warning,
        "n_safe": n_safe,
        "best_model": best,
        "reliability_pct": reliability,
        "n_features": n_features,
        "n_models": n_models,
        "leaderboard_df": leaderboard,
        "predictions_df": preds,
        "score_series": score,
        "cluster_profiles": cluster_profiles,
        "cluster_labels": cluster_labels,
        "feature_importance": fi_df,
        "llm_summary": llm_summary,
        "llm_methodology": llm_methodology,
        "llm_critical_analysis": llm_critical_analysis,
        "llm_watch": llm_watch,
        "llm_phenotypes": llm_phenotypes,
        "llm_risk_factors": llm_risk_factors,
        "generated_at": datetime.now(),
        "app_version": app_version,
    }

    gen = MedicalReportGenerator(lang=lang)
    return gen.generate_report(data)


def build_single_patient_report(
    patient_data: Dict[str, Any],
    risk_score: float,
    risk_level: str,
    doctor_name: str,
    lang: str = "fr",
    *,
    best_model_name: Optional[str] = None,
    accuracy_pct: Optional[float] = None,
) -> bytes:
    """Generate a focused single-patient PDF (cover, vitals + score, recommendations)."""
    acc = float(accuracy_pct) if accuracy_pct is not None else 94.0
    report_data: Dict[str, Any] = {
        "doctor_name": doctor_name or "—",
        "patient_data": patient_data,
        "risk_score": float(risk_score),
        "risk_level": str(risk_level),
        "n_patients": 1,
        "n_critical": 1 if risk_level == "HIGH" else 0,
        "n_warning": 1 if risk_level == "MEDIUM" else 0,
        "n_safe": 1 if risk_level == "LOW" else 0,
        "best_model": best_model_name or "CardioPredict ML",
        "accuracy": acc,
    }
    gen = MedicalReportGenerator(lang=lang)
    return gen.generate_single_patient_report(report_data)


def _report_strings(
    lang: str,
    reliability: float,
    n_features: int,
    n_models: int,
    app_version: str,
    n_critical: int,
    n_warning: int,
    best_esc: str,
    n_total: int,
) -> Dict[str, str]:
    """Static labels for PDF layout."""
    return {
        "cover_title": t("pdf_cover_title", lang),
        "cover_subtitle": t("pdf_cover_subtitle", lang),
        "cover_disclaimer_short": t("pdf_cover_disclaimer_short", lang),
        "cover_warning_box": t("pdf_cover_warning_box", lang),
        "cover_disclaimer_title": t("pdf_cover_disclaimer_title", lang),
        "label_doctor": t("pdf_label_doctor", lang),
        "label_date": t("pdf_label_date", lang),
        "label_time": t("pdf_label_time", lang),
        "label_patients": t("pdf_label_patients", lang),
        "label_model": t("pdf_label_model", lang),
        "label_reliability": t("pdf_label_reliability", lang),
        "exec_intro_para": t(
            "pdf_exec_intro_para",
            lang,
            n=str(n_total),
            model=best_esc,
            acc=f"{reliability:.1f}",
        ),
        "exec_interpretation_title": t("pdf_exec_interpretation_title", lang),
        "stat_label_critical": t("pdf_stat_label_critical", lang),
        "stat_label_watch": t("pdf_stat_label_watch", lang),
        "stat_label_safe": t("pdf_stat_label_safe", lang),
        "exec_title": t("pdf_exec_title", lang),
        "exec_risk_header": t("pdf_exec_risk_header", lang),
        "exec_count_header": t("pdf_exec_count_header", lang),
        "exec_pct_header": t("pdf_exec_pct_header", lang),
        "exec_critical_row": t("pdf_exec_critical_row", lang),
        "exec_warning_row": t("pdf_exec_warning_row", lang),
        "exec_safe_row": t("pdf_exec_safe_row", lang),
        "exec_total_row": t("pdf_exec_total_row", lang),
        "exec_clinical_ai": t("pdf_exec_clinical_ai", lang),
        "exec_model_line": t("pdf_exec_model_line", lang, model=best_esc),
        "exec_reliability_line": t("pdf_exec_reliability_line", lang, pct=f"{reliability:.1f}"),
        "exec_features_line": t("pdf_exec_features_line", lang, n=n_features),
        "meth_title": t("pdf_meth_title", lang),
        "meth_question": t("pdf_meth_question", lang),
        "meth_steps_title": t("pdf_meth_steps_title", lang),
        "meth_step1": t("pdf_meth_step1", lang),
        "meth_step2": t("pdf_meth_step2", lang, n=n_models),
        "meth_step3": t("pdf_meth_step3", lang),
        "meth_step4": t("pdf_meth_step4", lang),
        "meth_step5": t("pdf_meth_step5", lang),
        "crit_title": t("pdf_crit_title", lang, n=n_critical),
        "crit_intro": t("pdf_crit_intro", lang),
        "crit_global": t("pdf_crit_global", lang),
        "watch_title": t("pdf_watch_title", lang, n=n_warning),
        "watch_intro": t("pdf_watch_intro", lang),
        "pheno_title": t("pdf_pheno_title", lang),
        "pheno_intro": t("pdf_pheno_intro", lang),
        "risk_title": t("pdf_risk_title", lang),
        "appendix_title": t("pdf_appendix_title", lang),
        "appendix_limits": t("pdf_appendix_limits", lang),
        "table_id": t("pdf_table_id", lang),
        "table_age": t("pdf_table_age", lang),
        "table_sex": t("pdf_table_sex", lang),
        "table_hr": t("pdf_table_hr", lang),
        "table_bp": t("pdf_table_bp", lang),
        "table_chol": t("pdf_table_chol", lang),
        "table_risk": t("pdf_table_risk", lang),
        "header_brand": t("pdf_header_brand", lang),
        "footer_disclaimer": t("pdf_footer_disclaimer", lang),
        "footer_page": t("pdf_footer_page", lang),
        "chart_importance_title": t("pdf_chart_importance_title", lang),
        "chart_xlabel": t("pdf_chart_xlabel", lang),
        "appendix_label_tool": t("pdf_appendix_label_tool", lang),
        "appendix_label_automl": t("pdf_appendix_label_automl", lang),
        "appendix_label_llm": t("pdf_appendix_label_llm", lang),
        "appendix_label_npat": t("pdf_appendix_label_npat", lang),
        "appendix_label_nfeat": t("pdf_appendix_label_nfeat", lang),
        "appendix_label_ncompared": t("pdf_appendix_label_ncompared", lang),
        "appendix_label_time": t("pdf_appendix_label_time", lang),
    }
