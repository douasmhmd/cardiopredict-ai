"""Template-based clinical narrative blocks for PDF reports (decision-support wording)."""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


def interpret_risk_distribution(
    n_critical: int,
    n_warning: int,
    n_safe: int,
    n_total: int,
    *,
    lang: str = "fr",
) -> str:
    if lang == "ar":
        return (
            f"تم تحليل {n_total} مريضاً. المرضى الحرجون ({n_critical}) يستوجبون تقييماً سريرياً عاجلاً. "
            f"مرضى المراقبة ({n_warning}) يستفيدون من متابعة منتظمة. المرضى منخفضو الخطر ({n_safe}) يبقون تحت "
            "متابعة وقائية حسب البروتوكول المحلي."
        )
    if lang == "en":
        return (
            f"This cohort contains {n_total} patients. Critical cases ({n_critical}) warrant prompt clinical "
            f"review. Watch-list patients ({n_warning}) benefit from structured follow-up. Lower-risk patients "
            f"({n_safe}) may continue preventive care per local guidelines."
        )
    return (
        f"Sur {n_total} patients analysés, les profils critiques ({n_critical}) appellent une évaluation clinique "
        f"rapide. Les profils en surveillance ({n_warning}) justifient un suivi renforcé structuré. Les profils à "
        f"risque plus faible ({n_safe}) peuvent relever d'un suivi de prévention selon les recommandations locales."
    )


def interpret_methodology(
    n_models: int,
    best_model: str,
    reliability_pct: float,
    n_features: int,
    *,
    lang: str = "fr",
) -> str:
    if lang == "ar":
        return (
            f"تمت مقارنة عدة نماذج تعلم آلي (حوالي {n_models}) باستخدام التحقق المتقاطع. تم اختيار النموذج "
            f"«{best_model}» لأدائه النسبي. تقدير الثقة التقريبي للتمييز: {reliability_pct:.1f}%. تم استخدام "
            f"{n_features} متغيرات سريرية/شكلية بعد المعالجة المسبقة."
        )
    if lang == "en":
        return (
            f"Several machine-learning models (about {n_models}) were compared using cross-validation. "
            f"The selected estimator is «{best_model}» based on ranking metrics. Approximate discrimination "
            f"reliability: {reliability_pct:.1f}%. {n_features} input variables were used after preprocessing."
        )
    return (
        f"Plusieurs algorithmes (environ {n_models}) ont été comparés par validation croisée. Le modèle retenu "
        f"est «{best_model}» selon les métriques de classement. La fiabilité de discrimination affichée est d'environ "
        f"{reliability_pct:.1f}%. {n_features} variables cliniques/tabulaires ont été utilisées après préparation des données."
    )


def interpret_critical_cohort(n_critical: int, *, lang: str = "fr") -> str:
    if n_critical <= 0:
        if lang == "ar":
            return "لم يتم تصنيف أي مريض كحرج في هذا التشغيل."
        if lang == "en":
            return "No patients were flagged as critical in this run."
        return "Aucun patient n'est classé critique dans cette exécution."

    if lang == "ar":
        return (
            f"تم تحديد {n_critical} مريضاً ضمن الخطر المرتفع. يُنصح بمراجعة السجل السريري، وتكرار القياسات "
            "ذات الصلة، واتخاذ القرار وفق البروتوكول المحلي."
        )
    if lang == "en":
        return (
            f"{n_critical} patients show high predicted risk. Consider chart review, repeat relevant measures, "
            "and disposition per local pathways."
        )
    return (
        f"{n_critical} patients présentent un risque prédit élevé. Une relecture clinique, le contrôle des mesures "
        "pertinentes et une décision selon le réseau de soins local sont recommandés."
    )


def interpret_watch_cohort(n_warning: int, *, lang: str = "fr") -> str:
    if lang == "ar":
        return (
            f"قائمة المراقبة تضم {n_warning} مريضاً تقريباً؛ يُفضّل جدولة متابعة وتثقيف صحي حسب الحالة."
        )
    if lang == "en":
        return (
            f"The watch list includes about {n_warning} patients; scheduled follow-up and risk-factor counselling "
            "are appropriate."
        )
    return (
        f"Environ {n_warning} patients relèvent d'une surveillance renforcée ; planifier un suivi et l'éducation "
        "thérapeutique selon le contexte."
    )


def interpret_clusters(
    profiles: Optional[pd.DataFrame],
    labels: Optional[Dict[Any, str]],
    *,
    lang: str = "fr",
) -> str:
    if profiles is None or labels is None or len(labels) == 0:
        if lang == "ar":
            return "لم يتم تشغيل التصنيف غير الموجه أو لا توجد ملفات مجموعات."
        if lang == "en":
            return "Clustering was not run or phenotype summaries are unavailable."
        return "Le clustering n'a pas été exécuté ou les profils de phénotypes ne sont pas disponibles."

    parts = []
    for cid, lbl in sorted(labels.items(), key=lambda x: str(x[0])):
        try:
            n = int(profiles.loc[cid, "patient_count"])
        except Exception:
            n = 0
        parts.append(f"• {lbl} (~{n} patients)")

    body = "\n".join(parts)
    if lang == "ar":
        return "مجموعات فينوتيبية تقريبية:\n" + body
    if lang == "en":
        return "Approximate phenotype groups:\n" + body
    return "Groupes phénotypiques (approximatifs) :\n" + body


def interpret_feature_importance_context(*, lang: str = "fr") -> str:
    if lang == "ar":
        return (
            "تمثل الأهمية النسبية للمتغيرات مساهمة تقريبية في التنبؤ؛ يجب تفسيرها مع السياق السريري والقياسات."
        )
    if lang == "en":
        return (
            "Relative importance reflects approximate contribution to the model score; interpret alongside clinical "
            "context and measurement quality."
        )
    return (
        "L'importance relative des variables est indicative au sein du modèle ; elle doit être interprétée avec le "
        "contexte clinique et la qualité des mesures."
    )


def suggested_action_for_patient(risk_score: float, *, lang: str = "fr") -> str:
    if lang == "ar":
        return "مراجعة سريرية وفق البروتوكول؛ لا تأخير إذا كانت الأعراض حادة."
    if lang == "en":
        return "Clinical review per protocol; escalate if symptoms warrant."
    return "Réévaluation clinique selon le protocole ; ne pas retarder si symptômes évocateurs."


def clinical_reasoning_placeholder(age: Any, sex_lbl: str, hr: Any, bp: Any, chol: Any, *, lang: str = "fr") -> str:
    if lang == "ar":
        return (
            f"ملف عمر {age}، {sex_lbl}. مؤشرات: FCmax {hr}، ضغط {bp}، كوليسترول {chol}. "
            "النتيجة تعكس احتمالاً إحصائياً وليست تشخيصاً؛ قرار الطبيب هو المرجع."
        )
    if lang == "en":
        return (
            f"Profile: age {age}, {sex_lbl}. Vitals/context: max HR {hr}, BP {bp}, cholesterol {chol}. "
            "Scores reflect statistical risk, not a diagnosis; clinical judgment prevails."
        )
    return (
        f"Profil : âge {age}, {sex_lbl}. Éléments : FC max {hr}, TA {bp}, cholestérol {chol}. "
        "Le score est une probabilité modélisée, pas un diagnostic ; le jugement clinique reste central."
    )
