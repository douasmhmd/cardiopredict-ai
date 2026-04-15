"""
CardioPredict AI — Streamlit entry (cardiac monitoring + PyCaret AutoML).
Run from this folder: streamlit run app.py
"""

from __future__ import annotations

import html
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from automl.engine import AutoMLEngine
from automl.preprocessor import prepare_for_automl, suggest_target_column, validate_dataframe
from chatbot import agent as agent_mod
from chatbot.prompts import build_system_message
from chatbot.voice import transcribe_audio_with_whisper
from i18n.translations import t
from ui import cardiac_ui
from ui import clinic_mode
from ui import components
from ui import phenotyping
from ui.theme import CHAT_SCROLL_SCRIPT, CSS_STRING, RTL_SUPPLEMENT_CSS, TYPING_INDICATOR_HTML
from reports.report_builder import build_report_pdf_bytes

APP_VERSION = "1.0.0"

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None  # type: ignore[misc, assignment]

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_CSV = BASE_DIR / "data" / "sample_heart.csv"

# Sidebar navigation: one full-page interface per id (replaces a single row of st.tabs).
NAV_PAGE_ORDER: tuple[str, ...] = (
    "home",
    "clinic",
    "surveillance",
    "automl",
    "phenotyping",
    "assistant",
    "risk",
)


def _nav_option_label(page_id: str, lang: str) -> str:
    if page_id == "home":
        return t("nav_home", lang)
    key = {
        "clinic": "tab_clinic",
        "surveillance": "tab_live",
        "automl": "tab_leaderboard",
        "phenotyping": "tab_phenotyping",
        "assistant": "tab_chat",
        "risk": "tab_risk",
    }[page_id]
    return t(key, lang)


def _init_session() -> None:
    defaults: Dict[str, Any] = {
        "chat_messages": [],
        "openai_messages": [],
        "uploaded_df": None,
        "target_column": None,
        "current_step": "greeting",
        "model_status": "not trained",
        "automl_engine": None,
        "automl_pending": False,
        "leaderboard": None,
        "predictions": None,
        "best_model_name": None,
        "filter_level": None,
        "explain_idx": None,
        "show_importance": False,
        "whatif": None,
        "training_error": None,
        "greeted": False,
        "lang": "fr",
        "sim_tick": 0,
        "high_risk_threshold": 0.7,
        "refresh_sec": 30,
        "audio_alerts": False,
        "clustered_df": None,
        "cluster_labels": None,
        "cluster_profiles": None,
        "phenotype_n_clusters": 4,
        "report_pdf_bytes": None,
        "report_pdf_name": "",
        "model_trained": False,
        "batch_predictions_df": None,
        "batch_results": None,
        "wearable_results": None,
        "last_single_prediction": None,
        "single_patient_pdf_bytes": None,
        "batch_target_pdf_bytes": None,
        "data_loaded_at": None,
        "last_train_at": None,
        # (name, size) of last processed CSV from st.file_uploader — avoid re-import + reset every rerun
        "csv_upload_fingerprint": None,
        "nav_page": "home",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _msg_text(m: Dict[str, Any], lang: str) -> str:
    if m.get("i18n_key"):
        return t(m["i18n_key"], lang, **m.get("i18n_kwargs", {}))
    return str(m.get("content", ""))


def _data_summary(df: Optional[pd.DataFrame], lang: str) -> str:
    if df is None:
        return t("data_summary_none", lang)
    sug = suggest_target_column(df)
    ncol = min(12, len(df.columns))
    names = ", ".join(map(str, df.columns[:ncol]))
    if len(df.columns) > ncol:
        names += " …"
    suggest = ""
    if sug:
        suggest = t("data_summary_suggest", lang, sug=sug)
    return t(
        "data_summary_loaded",
        lang,
        rows=len(df),
        cols=len(df.columns),
        names=names,
        suggest=suggest,
    )


def _top_metrics_row(lb: pd.DataFrame) -> Dict[str, float]:
    row = lb.iloc[0]
    out: Dict[str, float] = {}
    for key in ("Accuracy", "AUC", "Recall", "Prec.", "Precision", "F1"):
        if key in row.index:
            v = row[key]
            try:
                out[key] = float(v)
            except (TypeError, ValueError):
                continue
    if "Prec." in out and "Precision" not in out:
        out["Precision"] = out["Prec."]
    return out


def _reset_automl_on_new_data() -> None:
    """Clear trained model outputs when the user loads a new CSV (metrics must reflect new state)."""
    st.session_state.predictions = None
    st.session_state.leaderboard = None
    st.session_state.best_model_name = None
    st.session_state.automl_engine = None
    st.session_state.model_status = "not trained"
    st.session_state.automl_pending = False
    st.session_state.model_trained = False
    st.session_state.batch_predictions_df = None
    st.session_state.batch_results = None
    st.session_state.wearable_results = None
    st.session_state.last_single_prediction = None
    st.session_state.single_patient_pdf_bytes = None
    st.session_state.batch_target_pdf_bytes = None
    st.session_state.data_loaded_at = None
    st.session_state.last_train_at = None


def _human_relative(dt: Optional[datetime], lang: str) -> str:
    if dt is None:
        return t("activity_just_now", lang)
    delta = datetime.now() - dt
    sec = int(max(0, delta.total_seconds()))
    if sec < 60:
        return t("activity_just_now", lang)
    if sec < 3600:
        return t("activity_minutes_ago", lang, n=max(1, sec // 60))
    if sec < 86400:
        return t("activity_hours_ago", lang, n=max(1, sec // 3600))
    return t("activity_days_ago", lang, n=max(1, sec // 86400))


def _load_sample_heart_dataset(lang: str) -> bool:
    if not SAMPLE_CSV.exists():
        return False
    _clear_clustering_results()
    _clear_report_artifacts()
    _reset_automl_on_new_data()
    st.session_state.csv_upload_fingerprint = None
    st.session_state.uploaded_df = pd.read_csv(SAMPLE_CSV)
    st.session_state.target_column = suggest_target_column(st.session_state.uploaded_df)
    st.session_state.current_step = "upload"
    st.session_state.data_loaded_at = datetime.now()
    tgt = st.session_state.target_column or ""
    _append_assistant(i18n_key="demo_loaded_assistant", i18n_kwargs={"target": tgt})
    return True


def _render_premium_home_dashboard(lang: str, metrics: Dict[str, Any]) -> None:
    """Premium hero (empty state), refined metrics bar, quick actions, activity timeline."""
    has_data = metrics["has_data"]
    has_predictions = metrics["has_predictions"]
    ms = str(st.session_state.get("model_status") or "not trained")
    n_pat = int(metrics["n_patients"])
    n_crit = int(metrics["n_critical"])
    n_watch = int(metrics["n_warning"])
    acc_disp = html.escape(str(metrics.get("accuracy_display") or "—").strip() or "—")

    if not has_data:
        badge = html.escape(t("hero_platform_badge", lang))
        title = html.escape(t("hero_main_title", lang))
        desc = html.escape(t("hero_main_desc", lang))
        hv_m = html.escape(t("hero_stat_models_value", lang))
        lb_m = html.escape(t("hero_stat_models", lang))
        hv_a = html.escape(t("hero_stat_accuracy_value", lang))
        lb_a = html.escape(t("hero_stat_accuracy_label", lang))
        hv_l = html.escape(t("hero_stat_langs_value", lang))
        lb_l = html.escape(t("hero_stat_langs", lang))
        hv_t = html.escape(t("hero_stat_time_value", lang))
        lb_t = html.escape(t("hero_stat_time_label", lang))
        st.markdown(
            f"""
            <div class="hero-premium">
                <div class="hero-premium-content">
                    <span class="hero-badge">{badge}</span>
                    <h1>{title}</h1>
                    <p>{desc}</p>
                    <div class="hero-stats-row">
                        <div class="hero-stat-item">
                            <div class="hero-stat-number">{hv_m}</div>
                            <div class="hero-stat-label">{lb_m}</div>
                        </div>
                        <div class="hero-stat-item">
                            <div class="hero-stat-number">{hv_a}</div>
                            <div class="hero-stat-label">{lb_a}</div>
                        </div>
                        <div class="hero-stat-item">
                            <div class="hero-stat-number">{hv_l}</div>
                            <div class="hero-stat-label">{lb_l}</div>
                        </div>
                        <div class="hero-stat-item">
                            <div class="hero-stat-number">{hv_t}</div>
                            <div class="hero-stat-label">{lb_t}</div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    trend_pat = t("metric_trend_active", lang, n=n_pat) if has_data else t("metric_trend_waiting", lang)
    trend_pat_e = html.escape(trend_pat)
    if n_crit > 0:
        trend_crit = html.escape(t("metric_trend_action", lang))
        crit_style = "background: #FEE2E2; color: #DC2626;"
    else:
        trend_crit = html.escape(t("metric_trend_ok", lang))
        crit_style = "background: #F0FDF4; color: #16A34A;"
    trend_watch = html.escape(t("metric_trend_follow", lang))
    if ms == "training":
        trend_acc = html.escape(t("metric_trend_training", lang))
    elif has_predictions:
        trend_acc = html.escape(t("metric_trend_automl_active", lang))
    else:
        trend_acc = html.escape(t("metric_trend_waiting", lang))

    lbl_pat = html.escape(t("patients_monitored", lang))
    lbl_crit = html.escape(t("critical_action", lang))
    lbl_watch = html.escape(t("watch_list", lang))
    lbl_acc = html.escape(t("automl_accuracy", lang))

    st.markdown(
        f"""
        <div class="metrics-bar-refined">
            <div class="metric-card-refined primary">
                <div class="metric-top">
                    <div class="metric-icon-small">👥</div>
                    <span class="metric-trend">{trend_pat_e}</span>
                </div>
                <div class="metric-big">{n_pat}</div>
                <div class="metric-label-small">{lbl_pat}</div>
            </div>
            <div class="metric-card-refined danger">
                <div class="metric-top">
                    <div class="metric-icon-small">🔴</div>
                    <span class="metric-trend" style="{crit_style}">{trend_crit}</span>
                </div>
                <div class="metric-big">{n_crit}</div>
                <div class="metric-label-small">{lbl_crit}</div>
            </div>
            <div class="metric-card-refined warning">
                <div class="metric-top">
                    <div class="metric-icon-small">🟡</div>
                    <span class="metric-trend" style="background: #FEF3C7; color: #D97706;">{trend_watch}</span>
                </div>
                <div class="metric-big">{n_watch}</div>
                <div class="metric-label-small">{lbl_watch}</div>
            </div>
            <div class="metric-card-refined success">
                <div class="metric-top">
                    <div class="metric-icon-small">🤖</div>
                    <span class="metric-trend">{trend_acc}</span>
                </div>
                <div class="metric-big">{acc_disp}</div>
                <div class="metric-label-small">{lbl_acc}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not has_data:
        st.markdown(
            f"""
            <div class="quick-actions-section">
                <div class="section-title">⚡ {html.escape(t("quick_start", lang))}</div>
                <div class="section-subtitle">{html.escape(t("quick_start_desc", lang))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f"""
                <div class="qa-col-inner">
                    <div class="quick-action-icon">📂</div>
                    <div class="quick-action-title">{html.escape(t("qa_demo_title", lang))}</div>
                    <div class="quick-action-desc">{html.escape(t("qa_demo_desc", lang))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(t("qa_demo_cta", lang), key="home_qa_demo", use_container_width=True):
                if _load_sample_heart_dataset(lang):
                    st.rerun()
                else:
                    st.error(t("sample_missing_error", lang))
        with c2:
            st.markdown(
                f"""
                <div class="qa-col-inner">
                    <div class="quick-action-icon">👤</div>
                    <div class="quick-action-title">{html.escape(t("qa_new_title", lang))}</div>
                    <div class="quick-action-desc">{html.escape(t("qa_new_desc", lang))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(t("qa_new_cta", lang), key="home_qa_new_patient", use_container_width=True):
                st.session_state.clinic_nav_single = True
                st.session_state.nav_page = "clinic"
                st.info(t("open_clinic_tab_hint", lang))
        with c3:
            st.markdown(
                f"""
                <div class="qa-col-inner">
                    <div class="quick-action-icon">📤</div>
                    <div class="quick-action-title">{html.escape(t("qa_import_title", lang))}</div>
                    <div class="quick-action-desc">{html.escape(t("qa_import_desc", lang))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(t("qa_import_cta", lang), key="home_qa_import", use_container_width=True):
                st.info(t("qa_import_hint", lang))
        with c4:
            st.markdown(
                f"""
                <div class="qa-col-inner">
                    <div class="quick-action-icon">⌚</div>
                    <div class="quick-action-title">{html.escape(t("qa_wearable_title", lang))}</div>
                    <div class="quick-action-desc">{html.escape(t("qa_wearable_desc", lang))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(t("qa_wearable_cta", lang), key="home_qa_wearable", use_container_width=True):
                st.session_state.clinic_nav_wearable = True
                st.session_state.nav_page = "clinic"
                st.info(t("open_clinic_tab_hint", lang))

    if has_data:
        when_load = _human_relative(st.session_state.get("data_loaded_at"), lang)
        line1_title = html.escape(t("activity_patients_loaded", lang, n=n_pat))
        line1_time = html.escape(when_load)
        block2 = ""
        if has_predictions:
            bm_raw = str(st.session_state.get("best_model_name") or "AutoML")
            line2_title = html.escape(t("activity_model_active", lang, model=bm_raw))
            line2_time = html.escape(_human_relative(st.session_state.get("last_train_at"), lang))
            block2 = f"""
            <div class="activity-item">
                <div class="activity-dot success"></div>
                <div class="activity-content">
                    <div class="activity-title">{line2_title}</div>
                    <div class="activity-time">{line2_time}</div>
                </div>
            </div>
            """
        else:
            line2_title = html.escape(t("activity_model_pending", lang))
            block2 = f"""
            <div class="activity-item">
                <div class="activity-dot"></div>
                <div class="activity-content">
                    <div class="activity-title">{line2_title}</div>
                    <div class="activity-time">{line1_time}</div>
                </div>
            </div>
            """
        st.markdown(
            f"""
            <div class="activity-timeline">
                <div class="section-title" style="margin-bottom:12px;">📋 {html.escape(t("recent_activity", lang))}</div>
                <div class="activity-item">
                    <div class="activity-dot success"></div>
                    <div class="activity-content">
                        <div class="activity-title">{line1_title}</div>
                        <div class="activity-time">{line1_time}</div>
                    </div>
                </div>
                {block2}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not has_predictions and ms != "ready":
            if st.button(
                t("home_launch_automl", lang),
                key="home_launch_automl_btn",
                type="primary",
                use_container_width=False,
            ):
                if st.session_state.uploaded_df is None:
                    st.warning(t("please_load_data", lang))
                elif not st.session_state.target_column:
                    st.warning(t("home_launch_need_target", lang))
                else:
                    st.session_state.automl_pending = True
                    _append_assistant(i18n_key="analyzing")
                    st.rerun()


def compute_live_metrics() -> Dict[str, Any]:
    """Dashboard metrics from session state only — no demo/hardcoded counts."""
    result: Dict[str, Any] = {
        "n_patients": 0,
        "n_critical": 0,
        "n_warning": 0,
        "n_safe": 0,
        "accuracy_display": "—",
        "accuracy_pct": None,
        "has_data": False,
        "has_predictions": False,
    }
    raw = st.session_state.get("uploaded_df")
    preds = st.session_state.get("predictions")
    lb = st.session_state.get("leaderboard")

    if raw is not None:
        result["has_data"] = True
        result["n_patients"] = int(len(raw))

    if preds is not None and len(preds) > 0:
        result["has_predictions"] = True
        result["n_patients"] = int(len(preds))

        if "risk_level" in preds.columns:
            result["n_critical"] = int((preds["risk_level"] == "HIGH").sum())
            result["n_warning"] = int((preds["risk_level"] == "MEDIUM").sum())
            result["n_safe"] = int((preds["risk_level"] == "LOW").sum())
        else:
            score_col = None
            for c in ("risk_score", "prediction_score", "Score", "Score_1"):
                if c in preds.columns:
                    score_col = c
                    break
            if score_col is not None:
                s = pd.to_numeric(preds[score_col], errors="coerce").fillna(0.0)
                result["n_critical"] = int((s > 0.7).sum())
                result["n_warning"] = int(((s > 0.4) & (s <= 0.7)).sum())
                result["n_safe"] = int((s <= 0.4).sum())

    if (
        result["has_predictions"]
        and st.session_state.get("model_status") == "ready"
        and lb is not None
        and len(lb) > 0
    ):
        tr = _top_metrics_row(lb)
        a = tr.get("Accuracy")
        if a is not None:
            ap = float(a)
            if ap <= 1:
                ap *= 100
            result["accuracy_pct"] = ap
            result["accuracy_display"] = f"{ap:.0f}%"

    return result


def _stats_for_prompt(lang: str) -> Dict[str, Any]:
    lb = st.session_state.leaderboard
    m = compute_live_metrics()
    n_models = len(lb) if lb is not None else 0
    mn = st.session_state.best_model_name or "—"
    acc = float(m.get("accuracy_pct") or 0.0)
    return {
        "n_patients": int(m["n_patients"]),
        "n_critical": int(m["n_critical"]),
        "model_name": mn,
        "accuracy": acc,
        "n_models": n_models,
    }


def _run_training_blocking() -> None:
    st.session_state.training_error = None
    st.session_state.model_status = "training"
    df = st.session_state.uploaded_df
    target = st.session_state.target_column
    if df is None or not target:
        st.session_state.training_error = t("missing_data_target", st.session_state.lang)
        st.session_state.model_status = "not trained"
        return

    clean, issues = prepare_for_automl(df, target)
    if issues:
        st.session_state.training_error = " ".join(issues)
        st.session_state.model_status = "not trained"
        return

    engine = AutoMLEngine()

    def work() -> AutoMLEngine:
        ok = engine.initialize(clean, target)
        if not ok:
            raise RuntimeError(engine.last_error or "Setup failed")
        lb, ok_c = engine.compare_all_models()
        if not ok_c or lb is None:
            raise RuntimeError(engine.last_error or "Model comparison failed")
        preds, ok_p = engine.predict_risk()
        if not ok_p or preds is None:
            raise RuntimeError(engine.last_error or "Predictions failed")
        return engine

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(work)
            engine = fut.result(timeout=600)
    except FuturesTimeout:
        st.session_state.training_error = t("training_timeout", st.session_state.lang)
        st.session_state.model_status = "not trained"
        return
    except Exception as exc:
        st.session_state.training_error = str(exc)
        st.session_state.model_status = "not trained"
        return

    st.session_state.automl_engine = engine
    st.session_state.leaderboard = engine.leaderboard
    st.session_state.predictions = engine.predictions
    st.session_state.model_status = "ready"
    st.session_state.training_error = None
    st.session_state.current_step = "results"
    _clear_report_artifacts()
    if engine.leaderboard is not None and len(engine.leaderboard):
        st.session_state.best_model_name = str(engine.leaderboard.iloc[0].get("Model", ""))
    engine.save_trained_model()
    st.session_state.model_trained = True
    st.session_state.last_train_at = datetime.now()


def run_automl_training() -> None:
    """Compare models, train best, and refresh predictions (chat + home CTA)."""
    _run_training_blocking()


def _append_assistant(text: Optional[str] = None, **extras: Any) -> None:
    msg: Dict[str, Any] = {"role": "assistant"}
    if extras.get("i18n_key"):
        msg["i18n_key"] = extras.pop("i18n_key")
        msg["i18n_kwargs"] = extras.pop("i18n_kwargs", {})
    if text is not None:
        msg["content"] = text
    elif "i18n_key" not in msg:
        msg["content"] = ""
    for k, v in extras.items():
        msg[k] = v
    st.session_state.chat_messages.append(msg)


def _user_wants_analysis(prompt: str) -> bool:
    p = prompt.lower()
    en_fr = (
        "start analysis",
        "run analysis",
        "train",
        "compare models",
        "go ahead",
        "lancer l'analyse",
        "lancer l'analyse",
        "lancer analyse",
        "lance l'analyse",
        "lancer l'entraînement",
        "lancer l'entrainement",
        "commencer l'analyse",
        "run automl",
    )
    if any(x in p for x in en_fr):
        return True
    if any(x in p for x in ("lancer", "lance", "entraîn", "entrain")) and (
        "analys" in p or "analyse" in p
    ):
        return True
    ar_phrases = ("بدا التحليل", "ابدأ التحليل", "تحليل", "درّب", "قارن الموديلات")
    for phrase in ar_phrases:
        if phrase in prompt:
            return True
    return False


def _user_wants_clustering(prompt: str) -> bool:
    p = prompt.lower()
    keywords = (
        "cluster",
        "clustering",
        "phénotyp",
        "phenotyp",
        "phenotype",
        "groupe",
        "segment",
        "k-means",
        "kmeans",
        "fiatyp",
    )
    if any(w in p for w in keywords):
        return True
    ar_kw = ("تصنيف", "مجموعة", "فينوتيب", "كلاستر")
    return any(w in prompt for w in ar_kw)


def _clear_clustering_results() -> None:
    st.session_state.clustered_df = None
    st.session_state.cluster_labels = None
    st.session_state.cluster_profiles = None


def _clear_report_artifacts() -> None:
    st.session_state.report_pdf_bytes = None
    st.session_state.report_pdf_name = ""


def main() -> None:
    st.set_page_config(
        page_title="CardioPredict AI",
        page_icon="🫀",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _init_session()
    st.markdown(CSS_STRING, unsafe_allow_html=True)

    if st.session_state.automl_engine is None:
        _disk = AutoMLEngine()
        if _disk.load_trained_model():
            st.session_state.automl_engine = _disk
            st.session_state.model_trained = True
            if _disk.clinical_model_name:
                st.session_state.best_model_name = _disk.clinical_model_name

    lang_options = {"🇫🇷 Français": "fr", "🇲🇦 الدارجة": "ar", "🇬🇧 English": "en"}
    label_by_lang = {v: k for k, v in lang_options.items()}
    current_label = label_by_lang.get(st.session_state.lang, "🇫🇷 Français")

    if not st.session_state.greeted:
        st.session_state.greeted = True
        st.session_state.chat_messages = [{"role": "assistant", "i18n_key": "welcome_message"}]
        st.session_state.current_step = "greeting"

    api_key = ""
    try:
        api_key = (st.secrets.get("OPENAI_API_KEY") or "").strip()
    except Exception:
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    def _handle_tool(name: str, args: Dict[str, Any]) -> str:
        if name == "run_automl":
            if st.session_state.uploaded_df is None:
                return "No CSV loaded. Ask the user to upload data or load the sample."
            tgt = args.get("target_column")
            if not tgt or tgt not in st.session_state.uploaded_df.columns:
                return f"Column '{tgt}' not found. Available: {list(st.session_state.uploaded_df.columns)}"
            st.session_state.target_column = tgt
            st.session_state.automl_pending = True
            return "Training queued. The app will run AutoML immediately after this reply."
        if name == "explain_patient":
            st.session_state.explain_idx = int(args.get("patient_id", 0))
            return "Showing explanation for that patient in the chat."
        if name == "filter_patients":
            st.session_state.filter_level = str(args.get("risk_level", "all")).lower()
            return "Filtered patient table updated below."
        if name == "show_feature_importance":
            st.session_state.show_importance = True
            return "Displaying risk-factor importance chart."
        if name == "what_if_analysis":
            st.session_state.whatif = {
                "patient_id": int(args["patient_id"]),
                "changes": dict(args.get("changes") or {}),
            }
            return "Computed what-if prediction."
        if name == "download_results":
            return "Use the sidebar 'Download predictions CSV' button after training completes."
        if name == "switch_model":
            eng = st.session_state.automl_engine
            if not eng:
                return "Train a model first."
            ok = eng.set_best_model_from_leaderboard(str(args.get("model_name", "")))
            if not ok:
                return eng.last_error or "Could not switch model."
            preds, okp = eng.predict_risk()
            if okp and preds is not None:
                st.session_state.predictions = preds
            return "Switched model and refreshed predictions."
        return f"Unknown tool {name}"

    def _process_chat_submitted(submitted_raw: str) -> None:
        submitted = (submitted_raw or "").strip()
        if not submitted:
            return
        skip_llm = False
        st.session_state.chat_messages.append({"role": "user", "content": submitted})
        if _user_wants_clustering(submitted):
            skip_llm = True
            if st.session_state.uploaded_df is None:
                _append_assistant(i18n_key="please_load_data")
                st.rerun()
            else:
                eng = st.session_state.automl_engine
                if eng is None:
                    eng = AutoMLEngine()
                    st.session_state.automl_engine = eng
                n_cl = int(st.session_state.get("phenotype_n_clusters", 4))
                with st.spinner(t("clustering", lang)):
                    clustered, ok, err = eng.run_clustering(
                        st.session_state.uploaded_df,
                        target_column=st.session_state.target_column,
                        n_clusters=n_cl,
                    )
                if ok and clustered is not None:
                    st.session_state.clustered_df = clustered
                    st.session_state.cluster_labels = eng.interpret_clusters_medically(lang)
                    st.session_state.cluster_profiles = eng.get_cluster_profiles()
                    n_lab = len(st.session_state.cluster_labels or {})
                    _append_assistant(
                        i18n_key="clustering_complete",
                        i18n_kwargs={"n": n_lab},
                    )
                else:
                    _append_assistant(content=(err or t("clustering_failed", lang)))
                st.rerun()
        elif (
            st.session_state.uploaded_df is not None
            and _user_wants_analysis(submitted)
            and st.session_state.target_column
        ):
            skip_llm = True
            st.session_state.automl_pending = True
            _append_assistant(i18n_key="analyzing")
            st.rerun()

        if not skip_llm:
            client = agent_mod.openai_client(api_key)
            if client is None:
                _append_assistant(i18n_key="set_api_key_msg")
            else:
                pc = _stats_for_prompt(lang)
                sys_msg = build_system_message(
                    current_step=st.session_state.current_step,
                    data_summary=_data_summary(st.session_state.uploaded_df, lang),
                    model_status=st.session_state.model_status,
                    target_column=st.session_state.target_column or "",
                    lang=lang,
                    n_patients=pc["n_patients"],
                    n_critical=pc["n_critical"],
                    model_name=pc["model_name"],
                    accuracy=pc["accuracy"],
                    n_models=pc["n_models"],
                )
                user_msgs2: List[Dict[str, Any]] = [{"role": "system", "content": sys_msg}]
                for m in st.session_state.chat_messages:
                    user_msgs2.append({"role": m["role"], "content": _msg_text(m, lang)})

                with st.container(border=True):
                    st.markdown("**🫀 Assistant**")
                    ph = st.empty()
                    ph.markdown(TYPING_INDICATOR_HTML, unsafe_allow_html=True)
                    try:
                        final_text, _ = agent_mod.run_agent_turn(client, user_msgs2, _handle_tool)
                    except Exception as exc:
                        err_msg = t("chat_error_prefix", lang, exc=str(exc))
                        ph.markdown(err_msg)
                        _append_assistant(i18n_key="chat_error_prefix", i18n_kwargs={"exc": str(exc)})
                    else:
                        if final_text:
                            ph.markdown(final_text)
                            _append_assistant(content=final_text)
                        else:
                            fb = t("generic_assistant_fallback", lang)
                            ph.markdown(fb)
                            _append_assistant(i18n_key="generic_assistant_fallback")

            if st.session_state.automl_pending:
                st.rerun()

    with st.sidebar:
        selected = st.radio(
            t("lang_radio_label", st.session_state.lang),
            list(lang_options.keys()),
            index=list(lang_options.keys()).index(current_label)
            if current_label in lang_options
            else 0,
            key="cardiopredict_lang_radio",
        )
        lang = lang_options[selected]
        st.session_state.lang = lang

        st.markdown(
            """
            <div class="logo-container">
                <div class="logo-icon">🫀</div>
                <div class="logo-text">CardioPredict AI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(t("app_tagline", lang))
        st.markdown(
            f"<p style='margin:0 0 12px 0;font-size:13px;opacity:0.9;'>{html.escape(t('sidebar_logo_sub', lang))}</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        st.markdown(f"#### {t('nav_section_title', lang)}")
        _cur_nav = st.session_state.get("nav_page", "home")
        if _cur_nav not in NAV_PAGE_ORDER:
            _cur_nav = "home"
            st.session_state.nav_page = _cur_nav
        for _pid in NAV_PAGE_ORDER:
            _lbl = _nav_option_label(_pid, lang)
            _is_cur = st.session_state.nav_page == _pid
            if st.button(
                _lbl,
                key=f"sidebar_nav_{_pid}",
                use_container_width=True,
                type="primary" if _is_cur else "secondary",
            ):
                st.session_state.nav_page = _pid
                st.rerun()
        st.divider()

        _live = compute_live_metrics()
        cardiac_ui.render_sidebar_patient_panel_dynamic(_live, lang=lang)
        st.divider()

        st.markdown(f"#### {t('data_source', lang)}")
        if st.button(t("load_demo", lang), use_container_width=True):
            if _load_sample_heart_dataset(lang):
                st.rerun()
            else:
                st.error(t("sample_missing_error", lang))

        st.toggle(
            t("simulate_stream", lang),
            key="stream_simulation",
        )

        up = st.file_uploader(t("upload_csv", lang), type=["csv"])
        if up is not None:
            # Streamlit keeps the chosen file across reruns; re-reading every run cleared automl_pending
            # and wiped training state, so "Launch analysis" in Assistant Cardio appeared to do nothing.
            _fp = (str(up.name), int(getattr(up, "size", 0) or 0))
            if st.session_state.get("csv_upload_fingerprint") != _fp:
                try:
                    raw = pd.read_csv(up)
                    raw, issues = validate_dataframe(raw)
                    if issues:
                        for msg in issues:
                            st.warning(msg)
                    _clear_clustering_results()
                    _clear_report_artifacts()
                    _reset_automl_on_new_data()
                    st.session_state.uploaded_df = raw
                    st.session_state.target_column = suggest_target_column(raw)
                    st.session_state.current_step = "upload"
                    st.session_state.data_loaded_at = datetime.now()
                    st.session_state.csv_upload_fingerprint = _fp
                except Exception:
                    st.error(t("csv_read_error", lang))

        st.divider()
        st.markdown(f"#### {t('sidebar_automl', lang)}")
        status = st.session_state.model_status
        if status == "ready":
            st.markdown(
                f'<div class="status-badge ready"><span class="status-dot ready"></span> '
                f"{html.escape(t('ready', lang))}</div>",
                unsafe_allow_html=True,
            )
            eng = st.session_state.automl_engine
            lb = st.session_state.leaderboard
            if eng and lb is not None and len(lb):
                tr = _top_metrics_row(lb)
                acc_v = tr.get("Accuracy")
                auc_v = tr.get("AUC")
                if acc_v is not None and acc_v <= 1:
                    acc_f = float(acc_v)
                elif acc_v is not None:
                    acc_f = float(acc_v) / 100.0
                else:
                    acc_f = None
                np_train = len(eng.raw_df) if eng.raw_df is not None else 0
                cardiac_ui.render_sidebar_model_status_card(
                    best_model_name=st.session_state.best_model_name or "—",
                    accuracy=acc_f,
                    auc=auc_v,
                    n_patients=np_train,
                    lang=lang,
                )
        elif status == "training":
            st.markdown(
                f'<div class="status-badge training"><span class="status-dot training"></span> '
                f"{html.escape(t('training', lang))}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="status-badge not-ready"><span class="status-dot not-ready"></span> '
                f"{html.escape(t('not_trained', lang))}</div>",
                unsafe_allow_html=True,
            )

        if st.session_state.predictions is not None:
            csv_bytes = (
                st.session_state.automl_engine.predictions_to_csv_bytes()
                if st.session_state.automl_engine
                else b""
            )
            if csv_bytes:
                st.download_button(
                    t("download_csv", lang),
                    data=csv_bytes,
                    file_name="cardiopredict_predictions.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        st.divider()
        cardiac_ui.render_alert_settings(lang)

        st.divider()
        st.markdown(f"### {t('generate_report', lang)}")
        st.text_input(
            t("doctor_name", lang),
            key="report_doctor",
            placeholder="Dr. …",
        )
        gen_pdf = st.button(
            t("generate_pdf_report", lang),
            use_container_width=True,
            key="generate_pdf_report_btn",
        )
        if gen_pdf:
            st.session_state.report_pdf_bytes = None
            if st.session_state.predictions is None:
                st.error(t("run_analysis_first", lang))
            else:
                with st.spinner(t("generating_report", lang)):
                    pdf = build_report_pdf_bytes(
                        lang=lang,
                        doctor_name=str(st.session_state.get("report_doctor", "") or ""),
                        uploaded_df=st.session_state.uploaded_df,
                        target_column=st.session_state.target_column,
                        predictions=st.session_state.predictions,
                        leaderboard=st.session_state.leaderboard,
                        best_model_name=st.session_state.best_model_name,
                        automl_engine=st.session_state.automl_engine,
                        cluster_profiles=st.session_state.cluster_profiles,
                        cluster_labels=st.session_state.cluster_labels,
                        app_version=APP_VERSION,
                    )
                if pdf:
                    st.session_state.report_pdf_bytes = pdf
                    st.session_state.report_pdf_name = (
                        f"CardioPredict_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    )
                else:
                    st.error(t("run_analysis_first", lang))
        if st.session_state.get("report_pdf_bytes"):
            st.download_button(
                label=f"⬇️ {t('download_report', lang)}",
                data=st.session_state.report_pdf_bytes,
                file_name=st.session_state.get("report_pdf_name") or "CardioPredict_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf_report_btn",
            )

    _pending_dock = st.session_state.pop("pending_dock_chat", None)
    if _pending_dock:
        _process_chat_submitted(str(_pending_dock).strip())

    if st.session_state.get("automl_pending"):
        st.session_state.automl_pending = False
        with st.spinner(t("spinner_comparing", lang)):
            run_automl_training()
        if st.session_state.model_status == "ready":
            _append_assistant(
                i18n_key="results_ready_assistant",
                leaderboard=True,
                predictions=True,
            )
        elif st.session_state.training_error:
            _append_assistant(i18n_key="training_failed_assistant")
        st.rerun()

    if st_autorefresh and st.session_state.get("stream_simulation"):
        tick = st_autorefresh(
            interval=int(st.session_state.get("refresh_sec", 30)) * 1000,
            key="cardio_stream_autorefresh",
        )
        st.session_state.sim_tick = int(tick) if tick is not None else 0
    elif not st.session_state.get("stream_simulation"):
        st.session_state.sim_tick = 0

    if lang == "ar":
        st.markdown(RTL_SUPPLEMENT_CSS, unsafe_allow_html=True)

    if st.session_state.training_error:
        st.error(st.session_state.training_error)
        st.session_state.training_error = None

    nav = st.session_state.get("nav_page", "home")
    if nav not in NAV_PAGE_ORDER:
        nav = "home"
        st.session_state.nav_page = nav

    high_thr = float(st.session_state.get("high_risk_threshold", 0.7))

    if nav == "home":
        _m = compute_live_metrics()
        if _m["has_data"]:
            st.title(t("app_title", lang))

        _render_premium_home_dashboard(lang, _m)

        st.caption(t("not_diagnosis", lang))

        if st.session_state.uploaded_df is not None:
            with st.expander(t("data_preview", lang), expanded=False):
                st.dataframe(st.session_state.uploaded_df.head(), use_container_width=True)
                tc = st.session_state.target_column
                if tc:
                    st.caption(t("suggested_outcome_caption", lang, tc=tc))

    elif nav == "clinic":
        st.header(_nav_option_label("clinic", lang))
        st.caption(t("not_diagnosis", lang))
        clinic_mode.render_clinic_tab(lang)

    elif nav == "surveillance":
        st.header(_nav_option_label("surveillance", lang))
        st.caption(t("not_diagnosis", lang))
        pred = st.session_state.predictions
        raw_df = st.session_state.uploaded_df
        rows = cardiac_ui.build_patient_rows(
            pred if pred is not None else pd.DataFrame(),
            raw_df,
            lang,
            int(st.session_state.get("sim_tick", 0)),
        )
        if not rows:
            st.info(t("monitor_empty", lang))
        else:
            for i in range(0, len(rows), 2):
                c1, c2 = st.columns(2)
                with c1:
                    cardiac_ui.render_patient_card(rows[i], lang, high_thr=high_thr)
                if i + 1 < len(rows):
                    with c2:
                        cardiac_ui.render_patient_card(rows[i + 1], lang, high_thr=high_thr)
            labels = [f"#{r['id']}" for r in rows]
            ix = st.selectbox(
                t("tab_patient_detail", lang),
                list(range(len(rows))),
                format_func=lambda j: labels[j],
                key="live_detail_idx",
            )
            eng = st.session_state.automl_engine
            if eng:
                with st.expander(t("insights_for_row", lang, idx=rows[ix]["row_index"]), expanded=False):
                    fig, narrative = eng.explain_patient(int(rows[ix]["row_index"]))
                    if narrative:
                        st.markdown(narrative)
                    if fig is not None:
                        components.shap_explanation_display(fig, lang=lang)

    elif nav == "automl":
        st.header(_nav_option_label("automl", lang))
        st.caption(t("not_diagnosis", lang))
        _lb_visible = st.session_state.leaderboard
        if (
            _lb_visible is not None
            and len(_lb_visible) > 0
            and str(st.session_state.get("model_status") or "") == "ready"
        ):
            with st.expander(t("main_automl_results_expander", lang), expanded=True):
                st.markdown(t("leaderboard_subtitle_cardiac", lang))
                _best_m = st.session_state.best_model_name or ""
                _n_m = len(_lb_visible)
                st.markdown(t("analysis_complete", lang, n=_n_m))
                st.markdown(t("leaderboard_caption", lang))
                _metrics_m = _top_metrics_row(_lb_visible)
                if _metrics_m:
                    _acc_m = _metrics_m.get("Accuracy", 0) or 0
                    _auc_m = _metrics_m.get("AUC", 0) or 0
                    if _acc_m <= 1:
                        _acc_m *= 100
                    st.markdown(
                        t(
                            "best_model_detail",
                            lang,
                            model=_best_m or t("top_model_fallback", lang),
                            accuracy=f"{_acc_m:.1f}",
                            auc=f"{_auc_m:.3f}",
                        )
                    )
                components.model_leaderboard(
                    _lb_visible, _best_m, lang=lang, chart_key="dashboard_leaderboard_table"
                )
                components.model_comparison_chart(
                    _lb_visible, lang=lang, chart_key="dashboard_model_comparison"
                )

        st.markdown(f"### {t('leaderboard_title_cardiac', lang)}")
        st.caption(t("leaderboard_subtitle_cardiac", lang))
        st.markdown(t("leaderboard_edu", lang))
        if st.session_state.leaderboard is not None:
            lb = st.session_state.leaderboard
            n = len(lb)
            st.markdown(t("analysis_complete", lang, n=n))
            st.markdown(t("leaderboard_caption", lang))
            best = st.session_state.best_model_name or ""
            metrics = _top_metrics_row(lb)
            if metrics:
                acc = metrics.get("Accuracy", 0) or 0
                auc = metrics.get("AUC", 0) or 0
                if acc <= 1:
                    acc *= 100
                st.markdown(
                    t(
                        "best_model_detail",
                        lang,
                        model=best or t("top_model_fallback", lang),
                        accuracy=f"{acc:.1f}",
                        auc=f"{auc:.3f}",
                    )
                )
                st.markdown(
                    f"""
                    <div class="winner-card">
                        <div class="trophy">🏆</div>
                        <div class="model-name">{html.escape(best or t("top_model_fallback", lang))}</div>
                        <div class="accuracy">{acc:.1f}%</div>
                        <div class="accuracy-label">{html.escape(t("col_accuracy", lang))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            components.model_leaderboard(
                lb, best, lang=lang, chart_key="leaderboard_tab_table"
            )
            components.model_comparison_chart(lb, lang=lang, chart_key="model_comparison_tab")
        else:
            st.info(t("leaderboard_empty", lang))

    elif nav == "phenotyping":
        st.header(_nav_option_label("phenotyping", lang))
        st.caption(t("not_diagnosis", lang))
        phenotyping.render_phenotyping_tab(lang)

    elif nav == "assistant":
        st.header(_nav_option_label("assistant", lang))
        st.caption(t("not_diagnosis", lang))
        st.subheader(t("tab_chat", lang))

        if st.session_state.explain_idx is not None and st.session_state.automl_engine:
            idx = st.session_state.explain_idx
            eng = st.session_state.automl_engine
            with st.container(border=True):
                st.markdown("**🫀 Assistant**")
                st.markdown(t("insights_for_row", lang, idx=idx))
                fig, narrative = eng.explain_patient(int(idx))
                if narrative:
                    st.markdown(narrative)
                if fig is not None:
                    components.shap_explanation_display(fig, lang=lang)
            st.session_state.explain_idx = None

        if st.session_state.whatif and st.session_state.automl_engine:
            wf = st.session_state.whatif
            eng = st.session_state.automl_engine
            with st.container(border=True):
                st.markdown("**🫀 Assistant**")
                st.markdown(t("what_if_result", lang))
                df2, err = eng.what_if_analysis(int(wf["patient_id"]), wf["changes"])
                if err:
                    st.warning(err)
                elif df2 is not None:
                    st.dataframe(df2, use_container_width=True)
            st.session_state.whatif = None

        st.info(t("chat_tab_where_launch", lang))
        _ms_chat = str(st.session_state.get("model_status") or "not trained")
        _has_pred_chat = st.session_state.predictions is not None
        if (
            st.session_state.uploaded_df is not None
            and st.session_state.target_column
            and _ms_chat != "ready"
            and not _has_pred_chat
        ):
            if st.button(
                t("home_launch_automl", lang),
                key="tab_chat_launch_automl_btn",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.automl_pending = True
                _append_assistant(i18n_key="analyzing")
                st.rerun()
        st.caption(t("chat_dock_bottom_hint", lang))

        chat_box = st.container()
        with chat_box:
            for _mi, m in enumerate(st.session_state.chat_messages):
                _who = "🫀 Assistant" if m["role"] == "assistant" else "👨‍⚕️ Vous"
                with st.container(border=True):
                    st.markdown(f"**{_who}**")
                    st.markdown(_msg_text(m, lang))
                    if m.get("leaderboard") and st.session_state.leaderboard is not None:
                        lb = st.session_state.leaderboard
                        n = len(lb)
                        st.markdown(t("analysis_complete", lang, n=n))
                        st.markdown(t("leaderboard_caption", lang))
                        best = st.session_state.best_model_name or ""
                        metrics = _top_metrics_row(lb)
                        if metrics:
                            acc = metrics.get("Accuracy", 0) or 0
                            auc = metrics.get("AUC", 0) or 0
                            if acc <= 1:
                                acc *= 100
                            st.markdown(
                                t(
                                    "best_model_detail",
                                    lang,
                                    model=best or t("top_model_fallback", lang),
                                    accuracy=f"{acc:.1f}",
                                    auc=f"{auc:.3f}",
                                )
                            )
                            st.markdown(
                                f"""
                                <div class="winner-card">
                                    <div class="trophy">🏆</div>
                                    <div class="model-name">{html.escape(best or t("top_model_fallback", lang))}</div>
                                    <div class="accuracy">{acc:.1f}%</div>
                                    <div class="accuracy-label">{html.escape(t("col_accuracy", lang))}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        components.model_leaderboard(
                            lb, best, lang=lang, chart_key=f"chat_leaderboard_table_{_mi}"
                        )
                        components.model_comparison_chart(
                            lb, lang=lang, chart_key=f"chat_model_comparison_{_mi}"
                        )
                    if m.get("predictions") and st.session_state.predictions is not None:
                        pred = st.session_state.predictions
                        st.markdown(t("patient_risk_overview_md", lang))
                        high = int((pred["risk_level"] == "HIGH").sum()) if "risk_level" in pred.columns else 0
                        med = int((pred["risk_level"] == "MEDIUM").sum()) if "risk_level" in pred.columns else 0
                        low = int((pred["risk_level"] == "LOW").sum()) if "risk_level" in pred.columns else 0
                        st.markdown(
                            f"""
                            <div class="risk-summary">
                                <div class="risk-summary-card high">
                                    <div class="count">{high}</div>
                                    <div class="risk-label">🔴 {html.escape(t("high_risk", lang))}</div>
                                </div>
                                <div class="risk-summary-card medium">
                                    <div class="count">{med}</div>
                                    <div class="risk-label">🟡 {html.escape(t("medium_risk", lang))}</div>
                                </div>
                                <div class="risk-summary-card low">
                                    <div class="count">{low}</div>
                                    <div class="risk-label">🟢 {html.escape(t("low_risk", lang))}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.markdown(t("predictions_ready", lang))
                        components.risk_distribution_pie(
                            pred, lang=lang, chart_key=f"chat_risk_distribution_pie_{_mi}"
                        )
                        show = pred
                        fl = st.session_state.filter_level
                        if fl and fl != "all" and "risk_level" in pred.columns:
                            lvl = fl.upper()
                            if lvl == "HIGH":
                                show = pred[pred["risk_level"] == "HIGH"]
                            elif lvl == "MEDIUM":
                                show = pred[pred["risk_level"] == "MEDIUM"]
                            elif lvl == "LOW":
                                show = pred[pred["risk_level"] == "LOW"]
                        components.patient_risk_table(show, lang=lang)
                        if fl and fl != "all":
                            st.session_state.filter_level = None

        voice_prompt: Optional[str] = None
        audio = None
        try:
            from streamlit_mic_recorder import mic_recorder

            with st.expander("🎤 " + t("voice_start", lang) + " / " + t("voice_stop", lang), expanded=False):
                _vc1, _vc2 = st.columns([1, 5])
                with _vc1:
                    audio = mic_recorder(
                        start_prompt="🎤 " + t("voice_start", lang),
                        stop_prompt="⏹️ " + t("voice_stop", lang),
                        just_once=True,
                        use_container_width=True,
                        key="cardiopredict_mic_rec",
                    )
                with _vc2:
                    st.markdown(
                        '<p style="color:#64748B;font-size:14px;padding-top:10px;margin:0;">🎙️</p>',
                        unsafe_allow_html=True,
                    )
        except ImportError:
            st.caption(t("voice_unavailable", lang))

        if audio and isinstance(audio, dict) and audio.get("bytes"):
            if api_key.strip():
                with st.spinner(t("voice_transcribing", lang)):
                    voice_prompt = transcribe_audio_with_whisper(
                        audio["bytes"], lang=lang, api_key=api_key
                    )
                if voice_prompt:
                    st.success(
                        f"{t('voice_heard', lang)} {html.escape(voice_prompt[:400])}"
                    )
                else:
                    st.warning(t("voice_error", lang))
            else:
                st.warning(t("set_api_key_msg", lang))

        st.markdown(
            f'<div class="voice-hint">{html.escape(t("voice_hint", lang))}</div>',
            unsafe_allow_html=True,
        )
        _ic1, _ic2 = st.columns([4, 1])
        with _ic1:
            _inline_text = st.text_input(
                "inline",
                placeholder=t("chat_inline_placeholder", lang),
                key="cardio_chat_inline_text",
                label_visibility="collapsed",
            )
        with _ic2:
            _inline_send = st.button(
                t("chat_inline_send", lang),
                key="cardio_chat_inline_send",
                use_container_width=True,
            )

        _spoken = (voice_prompt or "").strip() if voice_prompt else ""
        _inline_sub = (_inline_text or "").strip() if _inline_send else ""
        submitted_tab = _spoken or _inline_sub
        if submitted_tab:
            if _inline_send and "cardio_chat_inline_text" in st.session_state:
                st.session_state.cardio_chat_inline_text = ""
            _process_chat_submitted(submitted_tab)

    elif nav == "risk":
        st.header(_nav_option_label("risk", lang))
        st.caption(t("not_diagnosis", lang))
        st.markdown(t("risk_tab_hint", lang))
        eng = st.session_state.automl_engine
        if st.session_state.show_importance and eng:
            imp, ok = eng.get_feature_importance()
            st.markdown(t("risk_factors_weighted", lang))
            if ok and imp is not None:
                components.feature_importance_chart(
                    imp, lang=lang, chart_key="feature_importance_after_tool"
                )
            else:
                st.info(t("importance_unavailable", lang))
            st.session_state.show_importance = False
        elif eng and st.session_state.model_status == "ready":
            imp, ok = eng.get_feature_importance()
            if ok and imp is not None:
                components.feature_importance_chart(
                    imp, lang=lang, chart_key="feature_importance_tab_risk"
                )
            else:
                st.info(t("importance_unavailable", lang))
        else:
            st.info(t("leaderboard_empty", lang))

    _dock_chat = st.chat_input(
        placeholder=t("chat_placeholder", lang),
        key="cardiopredict_chat_dock_global",
    )
    if _dock_chat and str(_dock_chat).strip():
        st.session_state.pending_dock_chat = str(_dock_chat).strip()
        st.rerun()

    st.markdown(CHAT_SCROLL_SCRIPT, unsafe_allow_html=True)

    st.divider()
    st.caption(t("footer_note", lang))


if __name__ == "__main__":
    main()
