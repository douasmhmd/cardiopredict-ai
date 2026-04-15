"""Clinic / production mode: score new patients from a saved model (no target)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st

from automl.engine import AutoMLEngine
from chatbot.medical_interpreter import suggested_action_for_patient
from i18n.translations import t
from reports.report_builder import build_single_patient_report

BASE_DIR = Path(__file__).resolve().parent.parent
NEW_PATIENTS_DEMO = BASE_DIR / "data" / "new_patients_demo.csv"
WEARABLE_DEMO = BASE_DIR / "data" / "wearable_stream_demo.csv"


def get_clinical_action(level: str, lang: str) -> str:
    score = 0.85 if level == "HIGH" else 0.55 if level == "MEDIUM" else 0.2
    return suggested_action_for_patient(score, lang=lang)


def _ensure_clinic_engine() -> tuple[Optional[AutoMLEngine], bool]:
    """Return (engine, True) if the model was just loaded from disk this call."""
    eng = st.session_state.get("automl_engine")
    if eng is not None and getattr(eng, "best_model", None) is not None:
        return eng, False
    eng = AutoMLEngine()
    if eng.load_trained_model():
        st.session_state.automl_engine = eng
        st.session_state.model_trained = True
        if eng.clinical_model_name:
            st.session_state.best_model_name = eng.clinical_model_name
        return eng, True
    return None, False


def render_clinic_tab(lang: str) -> None:
    st.markdown(f"### {t('clinic_mode_title', lang)}")

    engine, loaded_from_disk = _ensure_clinic_engine()
    if engine is None:
        st.error(t("no_model_train_first", lang))
        st.info(t("clinic_no_model_hint", lang))
        return

    if loaded_from_disk:
        st.success(t("model_loaded", lang))

    acc = engine.clinical_accuracy_pct
    if acc is None and st.session_state.leaderboard is not None and len(st.session_state.leaderboard):
        try:
            a = float(st.session_state.leaderboard.iloc[0]["Accuracy"])
            acc = a * 100.0 if a <= 1.0 else a
        except (KeyError, TypeError, ValueError):
            acc = None
    acc_display = float(acc) if acc is not None else 0.0
    model_lbl = (
        st.session_state.get("best_model_name")
        or engine.clinical_model_name
        or "—"
    )

    st.markdown(
        f"""
        <div class="model-info-card">
            <strong>{t("active_model", lang)}:</strong> {model_lbl}<br/>
            <strong>{t("reliability", lang)}:</strong> {acc_display:.1f}%
        </div>
        """,
        unsafe_allow_html=True,
    )

    opts = [
        f"👤 {t('single_patient', lang)}",
        f"👥 {t('batch_patients', lang)}",
        f"⌚ {t('wearable_stream', lang)}",
    ]
    if st.session_state.pop("clinic_nav_single", False):
        st.session_state["clinic_prediction_mode_radio"] = opts[0]
    if st.session_state.pop("clinic_nav_wearable", False):
        st.session_state["clinic_prediction_mode_radio"] = opts[2]

    mode = st.radio(
        t("prediction_mode", lang),
        options=opts,
        horizontal=True,
        key="clinic_prediction_mode_radio",
    )

    st.markdown("---")

    if "👤" in mode or "single" in mode.lower():
        _render_single_patient(lang, engine)
    elif "👥" in mode or "batch" in mode.lower():
        _render_batch(lang, engine)
    else:
        _render_wearable(lang, engine)


def _render_single_patient(lang: str, engine: AutoMLEngine) -> None:
    st.markdown(f"#### {t('enter_patient_data', lang)}")

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Âge", 20, 100, 55, key="clinic_age")
        sex = st.selectbox(
            "Sexe",
            [("Homme", 1), ("Femme", 0)],
            format_func=lambda x: x[0],
            key="clinic_sex",
        )[1]
        cp = st.selectbox("Type de douleur thoracique", [0, 1, 2, 3], key="clinic_cp")
        trestbps = st.number_input("Tension repos (mmHg)", 80, 220, 130, key="clinic_bp")
    with col2:
        chol = st.number_input("Cholestérol (mg/dL)", 100, 600, 240, key="clinic_chol")
        fbs = st.selectbox(
            "Glycémie >120 (à jeun)",
            [("Non", 0), ("Oui", 1)],
            format_func=lambda x: x[0],
            key="clinic_fbs",
        )[1]
        restecg = st.selectbox("ECG repos", [0, 1, 2], key="clinic_restecg")
        thalach = st.number_input("FC max (bpm)", 60, 220, 150, key="clinic_thalach")
    with col3:
        exang = st.selectbox(
            "Angor d'effort",
            [("Non", 0), ("Oui", 1)],
            format_func=lambda x: x[0],
            key="clinic_exang",
        )[1]
        oldpeak = st.number_input("Dépression ST", 0.0, 7.0, 1.0, step=0.1, key="clinic_oldpeak")
        slope = st.selectbox("Pente ST", [0, 1, 2], key="clinic_slope")
        ca = st.selectbox("Vaisseaux principaux", [0, 1, 2, 3, 4], key="clinic_ca")
        thal = st.selectbox("Thalassémie", [0, 1, 2, 3], key="clinic_thal")

    if st.button(f"🔬 {t('predict_risk', lang)}", use_container_width=True, key="clinic_predict_single"):
        patient = pd.DataFrame(
            [
                {
                    "age": age,
                    "sex": sex,
                    "cp": cp,
                    "trestbps": trestbps,
                    "chol": chol,
                    "fbs": fbs,
                    "restecg": restecg,
                    "thalach": thalach,
                    "exang": exang,
                    "oldpeak": oldpeak,
                    "slope": slope,
                    "ca": ca,
                    "thal": thal,
                }
            ]
        )
        try:
            result = engine.predict_new_patients(patient)
        except Exception as exc:
            st.error(str(exc))
            return

        row = result.iloc[0]
        score = float(row.get("risk_score", row.get("prediction_score", row.get("Score", 0)) or 0))
        level = str(row.get("risk_level", "HIGH" if score > 0.7 else "MEDIUM" if score > 0.4 else "LOW"))
        color = "#DC2626" if level == "HIGH" else "#F59E0B" if level == "MEDIUM" else "#16A34A"
        risk_lbl_key = "high_risk" if level == "HIGH" else "medium_risk" if level == "MEDIUM" else "low_risk"

        st.markdown(
            f"""
            <div class="prediction-result-card" style="border-color: {color};">
                <div class="result-score" style="color: {color};">{int(score * 100)}%</div>
                <div class="result-label">{t(risk_lbl_key, lang)}</div>
                <div class="result-recommendation">{get_clinical_action(level, lang)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.session_state.last_single_prediction = {
            "patient": row.to_dict(),
            "score": score,
            "level": level,
        }
        st.session_state.single_patient_pdf_bytes = None

    if st.session_state.get("last_single_prediction"):
        if st.button(
            f"📄 {t('generate_patient_report', lang)}",
            use_container_width=True,
            key="clinic_gen_single_pdf",
        ):
            snap = st.session_state.last_single_prediction
            doctor = str(st.session_state.get("report_doctor", "") or "Dr.")
            pdf_bytes = build_single_patient_report(
                patient_data=snap["patient"],
                risk_score=float(snap["score"]),
                risk_level=str(snap["level"]),
                doctor_name=doctor,
                lang=lang,
                best_model_name=st.session_state.get("best_model_name"),
                accuracy_pct=st.session_state.get("automl_engine")
                and st.session_state.automl_engine.clinical_accuracy_pct,
            )
            st.session_state.single_patient_pdf_bytes = pdf_bytes

    pdf_b = st.session_state.get("single_patient_pdf_bytes")
    if pdf_b:
        st.download_button(
            "⬇️ " + t("download_single_patient_pdf", lang),
            data=pdf_b,
            file_name=f"rapport_patient_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="clinic_dl_single_pdf",
        )


def _render_batch(lang: str, engine: AutoMLEngine) -> None:
    st.markdown(f"#### {t('upload_new_patients_csv', lang)}")
    st.caption(t("csv_no_target_required", lang))

    if "batch_predictions_df" not in st.session_state:
        st.session_state.batch_predictions_df = None
    if "batch_results" not in st.session_state:
        st.session_state.batch_results = None

    uploaded = st.file_uploader(t("upload_csv", lang), type=["csv"], key="batch_upload_clinic")

    if st.button(t("use_demo_new_patients", lang), key="clinic_demo_batch"):
        try:
            new_df = pd.read_csv(NEW_PATIENTS_DEMO)
            st.session_state.batch_predictions_df = new_df
            st.session_state.batch_results = None
            st.success(f"✅ {len(new_df)} {t('new_patients_loaded', lang)}")
        except FileNotFoundError:
            st.error(str(NEW_PATIENTS_DEMO) + " " + t("file_not_found_short", lang))

    if uploaded is not None:
        new_df = pd.read_csv(uploaded)
        st.session_state.batch_predictions_df = new_df
        st.session_state.batch_results = None

    bdf = st.session_state.batch_predictions_df
    if bdf is not None:
        st.dataframe(bdf.head(), use_container_width=True)

        if st.button(f"🔬 {t('predict_all_patients', lang)}", use_container_width=True, key="clinic_predict_batch"):
            with st.spinner(t("predicting", lang)):
                try:
                    st.session_state.batch_results = engine.predict_new_patients(bdf)
                    st.session_state.batch_target_pdf_bytes = None
                except Exception as exc:
                    st.error(str(exc))

        res = st.session_state.batch_results
        if res is not None:
            score_col = "risk_score" if "risk_score" in res.columns else (
                "prediction_score" if "prediction_score" in res.columns else "Score"
            )
            s = pd.to_numeric(res[score_col], errors="coerce").fillna(0.0)
            n_high = int((s > 0.7).sum())
            n_med = int(((s > 0.4) & (s <= 0.7)).sum())
            n_low = int((s <= 0.4).sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 " + t("dashboard_critical", lang), n_high)
            c2.metric("🟡 " + t("dashboard_surveillance", lang), n_med)
            c3.metric("🟢 " + t("dashboard_safe", lang), n_low)

            results_display = res.sort_values(score_col, ascending=False)
            st.dataframe(results_display, use_container_width=True)

            st.markdown(f"#### 🎯 {t('select_target_patient', lang)}")
            patient_indices = results_display.index.tolist()
            selected_idx = st.selectbox(
                t("choose_patient_for_report", lang),
                patient_indices,
                format_func=lambda x: f"Patient #{x + 1} — {t('col_risk_score', lang)}: {int(float(results_display.loc[x, score_col]) * 100)}%",
                key="clinic_batch_select_patient",
            )

            if st.button(
                f"📄 {t('generate_targeted_report', lang)}",
                use_container_width=True,
                key="clinic_gen_batch_pdf",
            ):
                patient_row = results_display.loc[selected_idx]
                sc = float(patient_row[score_col])
                level = "HIGH" if sc > 0.7 else "MEDIUM" if sc > 0.4 else "LOW"
                doctor = str(st.session_state.get("report_doctor", "") or "Dr.")
                st.session_state.batch_target_pdf_bytes = build_single_patient_report(
                    patient_data=patient_row.to_dict(),
                    risk_score=sc,
                    risk_level=level,
                    doctor_name=doctor,
                    lang=lang,
                    best_model_name=st.session_state.get("best_model_name"),
                    accuracy_pct=engine.clinical_accuracy_pct,
                )

            tgt_pdf = st.session_state.get("batch_target_pdf_bytes")
            if tgt_pdf:
                st.download_button(
                    f"⬇️ Patient #{selected_idx + 1} — PDF",
                    data=tgt_pdf,
                    file_name=f"patient_{selected_idx + 1}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="clinic_dl_batch_pdf",
                )


def _render_wearable(lang: str, engine: AutoMLEngine) -> None:
    st.markdown(f"#### ⌚ {t('wearable_monitoring', lang)}")
    st.caption(t("wearable_description", lang))

    if "wearable_results" not in st.session_state:
        st.session_state.wearable_results = None

    if st.button(f"▶️ {t('start_simulation', lang)}", use_container_width=True, key="clinic_wearable_start"):
        try:
            wearable_df = pd.read_csv(WEARABLE_DEMO)
            with st.spinner(t("processing_stream", lang)):
                st.session_state.wearable_results = engine.predict_new_patients(wearable_df)
        except FileNotFoundError:
            st.error(str(WEARABLE_DEMO) + " " + t("file_not_found_short", lang))
        except Exception as exc:
            st.error(str(exc))

    wr = st.session_state.wearable_results
    if wr is None:
        return

    score_col = "risk_score" if "risk_score" in wr.columns else (
        "prediction_score" if "prediction_score" in wr.columns else "Score"
    )
    s = pd.to_numeric(wr[score_col], errors="coerce").fillna(0.0)
    critical = wr.loc[s > 0.7].sort_values(score_col, ascending=False)

    if len(critical) > 0:
        st.markdown(f"### 🚨 {t('critical_alerts', lang)} ({len(critical)})")
        for idx, row in critical.iterrows():
            sc = float(row[score_col])
            st.markdown(
                f"""
                <div class="wearable-alert critical">
                    <div class="alert-header">
                        <span class="patient-id">⌚ Patient #{int(idx) + 1}</span>
                        <span class="alert-score">{int(sc * 100)}%</span>
                    </div>
                    <div class="alert-vitals">
                        HR: {row.get("thalach", "N/A")} bpm |
                        BP: {row.get("trestbps", "N/A")} mmHg |
                        Chol: {row.get("chol", "N/A")}
                    </div>
                    <p class="wearable-notify-hint">🔔 {t("notify_doctor", lang)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(f"#### 👥 {t('all_wearable_patients', lang)}")
    st.dataframe(wr.sort_values(score_col, ascending=False), use_container_width=True)
