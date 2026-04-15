"""Patient phenotyping tab: K-Means profiles and medical visualizations."""

from __future__ import annotations

import html
from typing import Any, Dict, Optional

import pandas as pd
import pandas.api.types as ptypes
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.decomposition import PCA

from i18n.translations import get_feature_name, t
from ui import charts


CLUSTER_COLORS = ["#0F766E", "#14B8A6", "#F59E0B", "#DC2626", "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16"]

_CLUSTER_HOVER = dict(
    bgcolor="rgba(255,255,255,0.97)",
    bordercolor="#0F766E",
    font=dict(color="#000000", family="Inter, sans-serif", size=12),
)


def _finalize_cluster_figure(fig: go.Figure, *, height: int, legend: Optional[dict] = None) -> go.Figure:
    """Thème clair + texte noir lisible (évite le thème Streamlit qui blanchit les libellés)."""
    fig.update_layout(template="plotly_white")
    fig = charts.apply_chart_theme(fig)
    extra: dict = {"height": height}
    if legend is not None:
        extra["legend"] = legend
    fig.update_layout(**extra)
    fig.update_traces(hoverlabel=_CLUSTER_HOVER)
    return fig


def get_clinical_recommendation(cluster_label: str, lang: str) -> str:
    """Short clinical-style follow-up text by phenotype label (decision-support only)."""
    recommendations: Dict[str, Dict[str, str]] = {
        "fr": {
            "Seniors hypertendus": (
                "Surveillance étroite de la TA. Réévaluation thérapeutique si besoin. Suivi selon protocole local."
            ),
            "Jeunes actifs": (
                "Encourager l'activité physique adaptée. Bilan de routine selon les recommandations."
            ),
            "Hypercholestérolémie": (
                "Discussion sur mode de vie et stratégie lipidique selon les guidelines. Suivi biologique planifié."
            ),
            "Syndrome métabolique": (
                "Approche globale : nutrition, activité, sommeil et traitements si indiqués — coordination des soins."
            ),
            "Profil intermédiaire": ("Suivi standard individualisé selon les facteurs de risque présents."),
            "كبار السن بضغط مرتفع": (
                "مراقبة دقيقة للضغط وتعديل العلاج حسب البروتوكول المحلي."
            ),
            "شباب نشطون": ("تشجيع النشاط البدني المنتظم ومتابعة دورية."),
            "كوليسترول عالي": ("مناقشة النظام الغذائي والعلاج حسب التوصيات."),
            "متلازمة الأيض": ("تدخل متعدد العوامل: حمية، نشاط، ومتابعة سريرية."),
            "ملف متوسط": ("متابعة عادية حسب العوامل الفردية."),
        },
        "ar": {
            "Seniors hypertendus": "مراقبة دقيقة للضغط وتعديل العلاج حسب البروتوكول المحلي.",
            "Jeunes actifs": "تشجيع النشاط البدني ومتابعة دورية.",
            "Hypercholestérolémie": "مناقشة النظام والعلاج حسب التوصيات.",
            "Syndrome métabolique": "علاج متعدد: حمية، نشاط، ومتابعة.",
            "Profil intermédiaire": "متابعة حسب العوامل الفردية.",
            "كبار السن بضغط مرتفع": "مراقبة دقيقة للضغط وتعديل العلاج حسب البروتوكول المحلي.",
            "شباب نشطون": "تشجيع النشاط البدني المنتظم ومتابعة دورية.",
            "كوليسترول عالي": "مناقشة النظام الغذائي والعلاج حسب التوصيات.",
            "متلازمة الأيض": "تدخل متعدد العوامل: حمية، نشاط، ومتابعة سريرية.",
            "ملف متوسط": "متابعة عادية حسب العوامل الفردية.",
        },
        "en": {
            "Elderly hypertensive": (
                "Close BP follow-up. Adjust therapy per local protocol when indicated."
            ),
            "Young athletes": ("Encourage appropriate exercise. Routine follow-up per guidelines."),
            "Hypercholesterolemia": ("Discuss lifestyle and lipid management per guidelines."),
            "Metabolic syndrome": ("Multifactorial care: diet, activity, sleep, medications as indicated."),
            "Intermediate profile": ("Individualized routine follow-up based on risk factors."),
            "Seniors hypertendus": "Close BP follow-up per local protocol.",
            "Jeunes actifs": "Encourage appropriate exercise and routine checks.",
            "Hypercholestérolémie": "Discuss lifestyle and lipid strategy per guidelines.",
            "Syndrome métabolique": "Multifactorial management and coordinated care.",
            "Profil intermédiaire": "Standard individualized follow-up.",
        },
    }
    lang_map = recommendations.get(lang) or recommendations["en"]
    return lang_map.get(cluster_label) or t("clinical_fallback", lang)


def _feature_label_short(col: str, lang: str) -> str:
    return get_feature_name(str(col), lang)


def render_phenotyping_tab(lang: str) -> None:
    """Phenotyping UI driven by `st.session_state.clustered_df` and related keys."""
    st.markdown(f"### 🔬 {t('phenotyping_title', lang)}")
    st.caption(t("phenotyping_subtitle", lang))

    if st.session_state.get("clustered_df") is None:
        st.info(t("phenotyping_explanation", lang))
        col_a, col_b = st.columns([1, 3])
        with col_a:
            n_clusters = st.number_input(
                t("n_clusters_label", lang),
                min_value=2,
                max_value=8,
                value=int(st.session_state.get("phenotype_n_clusters", 4)),
                key="phenotype_n_clusters_input",
            )
        with col_b:
            if st.button(t("run_clustering_button", lang), use_container_width=True, key="run_clustering_btn"):
                if st.session_state.uploaded_df is None:
                    st.error(t("please_load_data", lang))
                else:
                    from automl.engine import AutoMLEngine

                    eng = st.session_state.automl_engine
                    if eng is None:
                        eng = AutoMLEngine()
                        st.session_state.automl_engine = eng
                    tgt = st.session_state.target_column
                    with st.spinner(t("clustering", lang)):
                        clustered, ok, err = eng.run_clustering(
                            st.session_state.uploaded_df,
                            target_column=tgt,
                            n_clusters=int(n_clusters),
                        )
                    if ok and clustered is not None:
                        st.session_state.clustered_df = clustered
                        st.session_state.cluster_labels = eng.interpret_clusters_medically(lang)
                        st.session_state.cluster_profiles = eng.get_cluster_profiles()
                        st.session_state.phenotype_n_clusters = int(n_clusters)
                        st.rerun()
                    else:
                        st.error(err or t("clustering_failed", lang))
        return

    clustered = st.session_state.clustered_df
    labels: Dict[Any, str] = dict(st.session_state.get("cluster_labels") or {})
    profiles = st.session_state.get("cluster_profiles")

    if profiles is None or not len(profiles):
        st.warning(t("cluster_profiles_missing", lang))
        return

    st.markdown(f"#### 👥 {t('cluster_groups', lang)}")
    sorted_items = sorted(labels.items(), key=lambda x: (str(x[0])))
    n_cards = len(sorted_items)
    batch_size = 4
    for batch_start in range(0, n_cards, batch_size):
        batch = sorted_items[batch_start : batch_start + batch_size]
        cols = st.columns(len(batch))
        for j, (cluster_id, label) in enumerate(batch):
            i = batch_start + j
            try:
                cnt = int(profiles.loc[cluster_id, "patient_count"])
            except Exception:
                cnt = 0
            color = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
            with cols[j]:
                st.markdown(
                    f"""
                <div class="cluster-card" style="border-top-color: {color};">
                    <div class="cluster-number">{html.escape(str(cluster_id))}</div>
                    <div class="cluster-label">{html.escape(str(label))}</div>
                    <div class="cluster-count">{cnt} {html.escape(t("patients_word", lang))}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown(f"#### 📊 {t('cluster_map', lang)}")
    st.caption(t("cluster_map_help", lang))

    cluster_col = _find_cluster_column(clustered)
    if cluster_col is None:
        st.warning(t("cluster_column_missing", lang))
        return

    numeric_cols = clustered.select_dtypes(include=["float64", "int64", "float32", "int32"]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != cluster_col]
    if len(numeric_cols) < 2:
        st.info(t("cluster_pca_need_features", lang))
    else:
        X = clustered[numeric_cols].fillna(0).values
        pca = PCA(n_components=2)
        X_2d = pca.fit_transform(X)
        plot_df = clustered.copy()
        plot_df["PC1"] = X_2d[:, 0]
        plot_df["PC2"] = X_2d[:, 1]
        plot_df["Phénotype"] = plot_df[cluster_col].map(lambda x: labels.get(x, str(x)))

        hover_cols = [c for c in ("age", "Age") if c in plot_df.columns]
        fig_scatter = px.scatter(
            plot_df,
            x="PC1",
            y="PC2",
            color="Phénotype",
            hover_data=hover_cols if hover_cols else None,
            color_discrete_sequence=CLUSTER_COLORS,
            title=t("cluster_map_title", lang),
        )
        fig_scatter.update_traces(marker=dict(size=12, line=dict(width=1, color="white")))
        fig_scatter = _finalize_cluster_figure(
            fig_scatter,
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="#000000", size=11, family="Inter, sans-serif"),
            ),
        )
        st.plotly_chart(fig_scatter, width="stretch", key="cluster_scatter_2d")

    key_features = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    available_features = [f for f in key_features if f in profiles.columns]
    if not available_features:
        available_features = [
            c
            for c in profiles.columns
            if c != "patient_count" and ptypes.is_numeric_dtype(profiles[c])
        ][:8]

    st.markdown(f"#### 🕸️ {t('cluster_profiles_radar', lang)}")
    st.caption(t("radar_help", lang))

    if available_features:
        radar_df = profiles[available_features].copy()
        rmin = radar_df.min()
        rmax = radar_df.max()
        radar_df_norm = (radar_df - rmin) / (rmax - rmin + 1e-9)
        labels_display = [_feature_label_short(f, lang) for f in available_features]

        fig_radar = go.Figure()
        for i, cluster_id in enumerate(radar_df_norm.index):
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=radar_df_norm.loc[cluster_id].values.tolist(),
                    theta=labels_display,
                    fill="toself",
                    name=str(labels.get(cluster_id, f"Cluster {cluster_id}")),
                    line=dict(color=CLUSTER_COLORS[i % len(CLUSTER_COLORS)], width=2),
                    opacity=0.6,
                )
            )
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor="#E2E8F0",
                    tickfont=dict(color="#000000", size=11),
                ),
                angularaxis=dict(
                    gridcolor="#E2E8F0",
                    tickfont=dict(color="#000000", size=11),
                ),
                bgcolor="white",
            ),
            showlegend=True,
            paper_bgcolor="white",
        )
        fig_radar = _finalize_cluster_figure(fig_radar, height=520)
        fig_radar.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color="#000000", size=11, family="Inter, sans-serif"),
            ),
        )
        st.plotly_chart(fig_radar, width="stretch", key="cluster_radar_profiles")
    else:
        st.info(t("cluster_no_numeric_profile", lang))

    st.markdown(f"#### 📊 {t('feature_comparison', lang)}")
    if available_features:
        bar_df = profiles[available_features].reset_index()
        id_col = bar_df.columns[0]
        if id_col != "Cluster":
            bar_df = bar_df.rename(columns={id_col: "Cluster"})
            id_col = "Cluster"
        bar_df_melted = bar_df.melt(id_vars=id_col, var_name="Feature", value_name="Value")
        bar_df_melted["Phénotype"] = bar_df_melted[id_col].map(lambda x: labels.get(x, str(x)))
        bar_df_melted["FeatureLabel"] = bar_df_melted["Feature"].map(
            lambda x: _feature_label_short(str(x), lang)
        )

        fig_bar = px.bar(
            bar_df_melted,
            x="FeatureLabel",
            y="Value",
            color="Phénotype",
            barmode="group",
            color_discrete_sequence=CLUSTER_COLORS,
            title=t("feature_comparison_title", lang),
        )
        fig_bar.update_layout(xaxis_title="", yaxis_title=t("avg_value", lang))
        fig_bar = _finalize_cluster_figure(fig_bar, height=450)
        st.plotly_chart(fig_bar, width="stretch", key="cluster_feature_bars")

    st.markdown(f"#### 📋 {t('cluster_details_table', lang)}")
    display_profiles = profiles.copy()
    try:
        display_profiles.insert(0, "Phénotype", display_profiles.index.map(lambda x: labels.get(x, str(x))))
    except Exception:
        display_profiles["Phénotype"] = display_profiles.index.astype(str)

    try:
        if available_features:
            styler = display_profiles.style.background_gradient(cmap="Blues", subset=available_features)
            st.dataframe(styler, use_container_width=True)
        else:
            st.dataframe(display_profiles, use_container_width=True)
    except Exception:
        st.dataframe(display_profiles, use_container_width=True)

    st.markdown(f"#### 💡 {t('medical_interpretation', lang)}")
    for cluster_id, label in sorted_items:
        try:
            cnt = int(profiles.loc[cluster_id, "patient_count"])
        except Exception:
            cnt = 0
        row = profiles.loc[cluster_id]
        with st.expander(f"🔬 {label} — {cnt} {t('patients_word', lang)}"):
            rec = get_clinical_recommendation(str(label), lang)
            age_v = row.get("age", row.get("Age"))
            bp_v = row.get("trestbps", row.get("resting_bp"))
            chol_v = row.get("chol", row.get("cholesterol"))
            hr_v = row.get("thalach", row.get("max_heart_rate"))
            st.markdown(
                f"""
**{t("avg_profile", lang)}:**
- {t("feature_age", lang)}: {_fmt_num(age_v)}
- {t("feature_bp", lang)}: {_fmt_num(bp_v)} mmHg
- {t("feature_chol", lang)}: {_fmt_num(chol_v)} mg/dL
- {t("feature_hr", lang)}: {_fmt_num(hr_v)} bpm

**{t("clinical_recommendation", lang)}:**  
{rec}
                """
            )

    if st.button(t("clear_clustering_button", lang), key="clear_clustering"):
        st.session_state.clustered_df = None
        st.session_state.cluster_labels = None
        st.session_state.cluster_profiles = None
        st.rerun()


def _fmt_num(v: Any) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "N/A"
    try:
        return f"{float(v):.0f}"
    except (TypeError, ValueError):
        return str(v)


def _find_cluster_column(df: pd.DataFrame) -> Optional[str]:
    for c in df.columns:
        cs = str(c).lower()
        if cs in ("cluster", "clusters") or "cluster" in cs:
            return str(c)
    return None
