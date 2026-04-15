"""CardioPredict AI — patient cards, hero metrics, sidebar model card."""

from __future__ import annotations

import hashlib
import html
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from i18n.translations import t


def _stable_hash_int(seed: str, mod: int) -> int:
    h = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % mod


def vitals_for_row(idx: int, risk: float, df_row: Optional[pd.Series]) -> Dict[str, Any]:
    """Deterministic pseudo wearable vitals for demo (UCI heart has no SpO2/HRV)."""
    seed = f"{idx}-{risk:.4f}"
    hr = 58 + _stable_hash_int(seed + "hr", 55)
    sys_bp = 105 + _stable_hash_int(seed + "sys", 45)
    dia = 65 + _stable_hash_int(seed + "dia", 20)
    spo2 = 94 + _stable_hash_int(seed + "spo2", 5)
    hrv = 18 + _stable_hash_int(seed + "hrv", 45)
    age = 55
    sex = "—"
    device = "Apple Watch"
    if df_row is not None:
        for a_col in ("age", "Age"):
            if a_col in df_row.index and pd.notna(df_row[a_col]):
                try:
                    age = int(float(df_row[a_col]))
                except (TypeError, ValueError):
                    pass
                break
        for s_col in ("sex", "Sex"):
            if s_col in df_row.index and pd.notna(df_row[s_col]):
                v = df_row[s_col]
                sex = "M" if str(v).strip() in ("1", "1.0", "male", "M", "m") else "F"
                break
    devs = ("Apple Watch", "Fitbit Sense", "Galaxy Watch", "Withings", "Fitbit Charge")
    device = devs[_stable_hash_int(seed + "d", len(devs))]
    return {
        "hr": hr,
        "bp_sys": sys_bp,
        "bp_dia": dia,
        "spo2": spo2,
        "hrv": hrv,
        "age": age,
        "sex": sex,
        "device": device,
    }


def render_patient_card(
    patient: Dict[str, Any],
    lang: str,
    *,
    high_thr: float = 0.7,
    med_thr: float = 0.4,
) -> None:
    risk = float(patient.get("risk", 0))
    risk_class = "high" if risk > high_thr else "medium" if risk > med_thr else "low"
    risk_emoji = "🔴" if risk_class == "high" else "🟡" if risk_class == "medium" else "🟢"
    meta = html.escape(str(patient.get("meta", "")))
    last_u = html.escape(str(patient.get("last_update", "—")))
    pid = html.escape(str(patient.get("id", "?")))

    st.markdown(
        f"""
    <div class="patient-card {risk_class}">
        <div class="patient-header">
            <span class="patient-id">👤 Patient #{pid}</span>
            <span class="risk-badge-{risk_class}">{risk_emoji} {int(risk * 100)}%</span>
        </div>
        <div class="patient-meta">{meta}</div>
        <div class="patient-vitals">
            <div class="vital">
                <span class="vital-icon">❤️</span>
                <span class="vital-value">{patient['hr']} bpm</span>
                <span class="vital-label">HR</span>
            </div>
            <div class="vital">
                <span class="vital-icon">🩸</span>
                <span class="vital-value">{patient['bp_sys']}/{patient['bp_dia']}</span>
                <span class="vital-label">BP</span>
            </div>
            <div class="vital">
                <span class="vital-icon">💨</span>
                <span class="vital-value">{patient['spo2']}%</span>
                <span class="vital-label">SpO₂</span>
            </div>
            <div class="vital">
                <span class="vital-icon">📊</span>
                <span class="vital-value">{patient['hrv']} ms</span>
                <span class="vital-label">HRV</span>
            </div>
        </div>
        <div class="patient-footer">
            <span>🕐 {last_u}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_hero_metrics_bar(
    *,
    n_patients: int,
    n_critical: int,
    n_watch: int,
    accuracy_display: str,
    lang: str,
) -> None:
    acc = accuracy_display if accuracy_display.strip() else "—"
    c1, c2, c3, c4 = st.columns(4)
    blocks = [
        (c1, "", "👥", str(n_patients), t("hero_bar_patients", lang)),
        (c2, "critical", "🔴", str(n_critical), t("hero_bar_critical", lang)),
        (c3, "warning", "🟡", str(n_watch), t("hero_bar_watch", lang)),
        (c4, "success", "🤖", acc, t("hero_bar_automl", lang)),
    ]
    for col, cls, icon, val, lbl in blocks:
        cls_html = f" {cls}" if cls else ""
        with col:
            st.markdown(
                f"""
            <div class="metric-hero{cls_html}">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{html.escape(val)}</div>
                <div class="metric-label">{html.escape(lbl)}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def render_sidebar_patient_panel_dynamic(metrics: Dict[str, Any], *, lang: str) -> None:
    """Patient panel from `compute_live_metrics()` — no hardcoded demo numbers or fake deltas."""
    st.markdown(f"### {t('patient_panel', lang)}")
    if not metrics.get("has_data"):
        st.info(t("no_data_loaded_sidebar", lang))
        return
    if not metrics.get("has_predictions"):
        st.warning(t("data_not_analyzed", lang))
        st.caption(f"📊 {metrics['n_patients']} {t('patients_loaded', lang)}")
        return

    np_ = int(metrics["n_patients"])
    nc = int(metrics["n_critical"])
    nw = int(metrics["n_warning"])
    ns = int(metrics["n_safe"])
    st.markdown(
        f"""
    <div class="sidebar-patient-summary">
        <div class="summary-row">
            <span class="summary-label">{html.escape(t("total", lang))}</span>
            <span class="summary-value">{np_}</span>
        </div>
        <div class="summary-row critical">
            <span class="summary-label">🔴 {html.escape(t("dashboard_critical", lang))}</span>
            <span class="summary-value">{nc}</span>
        </div>
        <div class="summary-row warning">
            <span class="summary-label">🟡 {html.escape(t("dashboard_surveillance", lang))}</span>
            <span class="summary-value">{nw}</span>
        </div>
        <div class="summary-row safe">
            <span class="summary-label">🟢 {html.escape(t("dashboard_safe", lang))}</span>
            <span class="summary-value">{ns}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar_model_status_card(
    *,
    best_model_name: str,
    accuracy: Optional[float],
    auc: Optional[float],
    n_patients: int,
    lang: str,
) -> None:
    acc_s = f"{accuracy * 100:.1f}%" if accuracy is not None else "—"
    auc_s = f"{auc:.3f}" if auc is not None else "—"
    st.markdown(
        f"""
    <div class="model-status-card">
        <div class="status-label">{html.escape(t("winning_model", lang))}</div>
        <div class="model-name">{html.escape(best_model_name)}</div>
        <div class="model-metrics">
            <span>{html.escape(t("col_accuracy", lang))}: {html.escape(acc_s)}</span>
            <span>AUC: {html.escape(auc_s)}</span>
        </div>
        <div class="trained-info">✓ {html.escape(t("trained_on_n", lang, n=n_patients))}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def build_patient_rows(
    predictions: pd.DataFrame,
    raw_df: Optional[pd.DataFrame],
    lang: str,
    sim_tick: int,
) -> List[Dict[str, Any]]:
    """Sorted rows for patient cards (HIGH risk first); preserves row index into raw data."""
    if predictions is None or len(predictions) == 0:
        return []
    df = predictions.copy()
    if "risk_score" not in df.columns:
        return []
    df["_orig_idx"] = df.index.astype(int)
    df = df.sort_values("risk_score", ascending=False)
    rows: List[Dict[str, Any]] = []
    for _, pr in df.iterrows():
        oi = int(pr["_orig_idx"])
        rs = float(pr.get("risk_score", 0) or 0)
        row_raw = raw_df.iloc[oi] if raw_df is not None and oi < len(raw_df) else None
        vit = vitals_for_row(oi + sim_tick, rs, row_raw)
        pid = oi
        if raw_df is not None and oi < len(raw_df):
            rr = raw_df.iloc[oi]
            if "patient_id" in raw_df.columns:
                pid = rr.get("patient_id", oi)
            elif "id" in raw_df.columns:
                pid = rr.get("id", oi)
        meta = f"{vit['age']} {t('years_short', lang)} • {vit['sex']} • ⌚ {vit['device']}"
        rows.append(
            {
                "id": pid,
                "risk": rs,
                "hr": vit["hr"],
                "bp_sys": vit["bp_sys"],
                "bp_dia": vit["bp_dia"],
                "spo2": vit["spo2"],
                "hrv": vit["hrv"],
                "meta": meta,
                "last_update": t("live_now_sim", lang) if sim_tick else t("just_now", lang),
                "row_index": oi,
            }
        )
    return rows


def render_alert_settings(lang: str) -> None:
    st.markdown(f"### {t('sidebar_alerts', lang)}")
    st.session_state.high_risk_threshold = st.slider(
        t("slider_high_risk", lang),
        min_value=0.5,
        max_value=0.95,
        value=float(st.session_state.get("high_risk_threshold", 0.7)),
        step=0.05,
        key="slider_thr",
    )
    interval = st.selectbox(
        t("select_refresh", lang),
        options=[10, 30, 60],
        format_func=lambda x: t(f"refresh_{x}s", lang),
        index=[10, 30, 60].index(st.session_state.get("refresh_sec", 30))
        if st.session_state.get("refresh_sec", 30) in (10, 30, 60)
        else 1,
        key="refresh_interval_sel",
    )
    st.session_state.refresh_sec = interval
    st.session_state.audio_alerts = st.toggle(
        t("toggle_audio", lang),
        value=bool(st.session_state.get("audio_alerts", False)),
        key="audio_alerts_toggle",
    )
