"""Medical PDF report (ReportLab) for CardioPredict AI."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from chatbot.medical_interpreter import clinical_reasoning_placeholder, suggested_action_for_patient
from i18n.translations import get_feature_name, t

# Palette
COLOR_TEAL_DARK = colors.HexColor("#0F766E")
COLOR_TEAL = colors.HexColor("#14B8A6")
COLOR_TEAL_LIGHT = colors.HexColor("#CCFBF1")
COLOR_RED = colors.HexColor("#DC2626")
COLOR_RED_LIGHT = colors.HexColor("#FEE2E2")
COLOR_YELLOW = colors.HexColor("#F59E0B")
COLOR_YELLOW_LIGHT = colors.HexColor("#FEF3C7")
COLOR_GREEN = colors.HexColor("#16A34A")
COLOR_GREEN_LIGHT = colors.HexColor("#DCFCE7")
COLOR_DARK = colors.HexColor("#0F172A")
COLOR_MUTED = colors.HexColor("#64748B")
COLOR_BG = colors.HexColor("#F0FDFA")


def safe_paragraph_text(text: Optional[str], *, allow_tags: bool = True) -> str:
    """Prepare free-form text for ReportLab Paragraph (escape + optional simple tags)."""
    if text is None:
        return ""
    s = str(text).strip()
    if not s:
        return "—"
    safe = escape(s)
    safe = safe.replace("\r\n", "\n").replace("\r", "\n")
    safe = safe.replace("\n\n", "<br/><br/>").replace("\n", "<br/>")
    if not allow_tags:
        return safe
    for enc, dec in (
        ("&lt;br/&gt;", "<br/>"),
        ("&lt;br /&gt;", "<br/>"),
        ("&lt;br&gt;", "<br/>"),
        ("&lt;/b&gt;", "</b>"),
        ("&lt;b&gt;", "<b>"),
        ("&lt;/i&gt;", "</i>"),
        ("&lt;i&gt;", "<i>"),
    ):
        safe = safe.replace(enc, dec)
    return safe


def _pt(text: str, style: ParagraphStyle) -> Paragraph:
    """Plain text → Paragraph (XML-escaped)."""
    if not text:
        text = "—"
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def _ph(html: str, style: ParagraphStyle) -> Paragraph:
    """Trusted mini-HTML for ReportLab (i18n templates with <b>, <br/>, etc.)."""
    if not html:
        html = "—"
    return Paragraph(str(html).replace("\n", "<br/>"), style)


def _llm(text: Optional[str], style: ParagraphStyle) -> Paragraph:
    """LLM / interpreter text that may contain simple markup."""
    return Paragraph(safe_paragraph_text(text, allow_tags=True), style)


class MedicalReportGenerator:
    def __init__(self, lang: str = "fr") -> None:
        self.lang = lang
        self.styles = self._build_styles()
        self.elements: List[Any] = []

    def _build_styles(self) -> Dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        styles: Dict[str, ParagraphStyle] = {
            "Normal": base["Normal"],
            "ReportTitle": ParagraphStyle(
                name="ReportTitle",
                parent=base["Title"],
                fontSize=22,
                textColor=COLOR_TEAL_DARK,
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            ),
            "ReportSubtitle": ParagraphStyle(
                name="ReportSubtitle",
                parent=base["Normal"],
                fontSize=12,
                textColor=COLOR_MUTED,
                spaceAfter=18,
                alignment=TA_CENTER,
            ),
            "SectionHeader": ParagraphStyle(
                name="SectionHeader",
                parent=base["Heading1"],
                fontSize=16,
                textColor=COLOR_TEAL_DARK,
                spaceBefore=14,
                spaceAfter=10,
                fontName="Helvetica-Bold",
            ),
            "SubSection": ParagraphStyle(
                name="SubSection",
                parent=base["Heading2"],
                fontSize=12,
                textColor=COLOR_DARK,
                spaceBefore=8,
                spaceAfter=6,
                fontName="Helvetica-Bold",
            ),
            "BodyJustified": ParagraphStyle(
                name="BodyJustified",
                parent=base["Normal"],
                fontSize=10,
                textColor=COLOR_DARK,
                alignment=TA_JUSTIFY,
                leading=13,
                spaceAfter=8,
            ),
            "LLMBox": ParagraphStyle(
                name="LLMBox",
                parent=base["Normal"],
                fontSize=10,
                textColor=COLOR_DARK,
                alignment=TA_JUSTIFY,
                leading=13,
                leftIndent=8,
                rightIndent=8,
                spaceAfter=10,
                backColor=COLOR_TEAL_LIGHT,
                borderPadding=8,
            ),
            "Disclaimer": ParagraphStyle(
                name="Disclaimer",
                parent=base["Normal"],
                fontSize=8,
                textColor=COLOR_MUTED,
                alignment=TA_CENTER,
                fontName="Helvetica-Oblique",
            ),
            "Small": ParagraphStyle(
                name="Small",
                parent=base["Normal"],
                fontSize=9,
                textColor=COLOR_DARK,
                leading=11,
            ),
            "BodyProfessional": ParagraphStyle(
                name="BodyProfessional",
                parent=base["Normal"],
                fontSize=10.5,
                textColor=colors.HexColor("#1E293B"),
                alignment=TA_JUSTIFY,
                leading=15,
                spaceAfter=8,
                spaceBefore=4,
                fontName="Helvetica",
            ),
            "SectionIntro": ParagraphStyle(
                name="SectionIntro",
                parent=base["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#475569"),
                alignment=TA_JUSTIFY,
                leading=16,
                spaceAfter=14,
                spaceBefore=8,
                fontName="Helvetica-Oblique",
                leftIndent=12,
                rightIndent=12,
            ),
        }
        return styles

    def generate_report(self, data: Dict[str, Any]) -> bytes:
        self.elements = []
        S = data["strings"]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.2 * cm,
            bottomMargin=2 * cm,
        )

        self._build_cover_page(data, S)
        self._build_executive_summary(data, S)
        self._build_methodology_page(data, S)
        self._build_critical_patients_page(data, S)
        self._build_watch_list_page(data, S)
        if data.get("cluster_profiles") is not None and data.get("cluster_labels"):
            self._build_phenotypes_page(data, S)
        self._build_risk_factors_page(data, S)
        self._build_appendix_page(data, S)

        doc.build(
            self.elements,
            onFirstPage=self._make_decorate(S),
            onLaterPages=self._make_decorate(S),
        )
        buffer.seek(0)
        return buffer.getvalue()

    def generate_single_patient_report(self, data: Dict[str, Any]) -> bytes:
        """Three-page PDF: cover, patient vitals + score, clinical recommendations."""
        self.elements = []
        lang = self.lang
        S = {
            "footer_disclaimer": t("pdf_footer_disclaimer", lang),
            "footer_page": t("pdf_footer_page", lang),
        }
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.2 * cm,
            bottomMargin=2 * cm,
        )

        gen_time = datetime.now()
        doctor = escape(str(data.get("doctor_name") or "—"))
        risk = float(data.get("risk_score", 0) or 0)
        level = str(data.get("risk_level", "LOW"))
        patient = data.get("patient_data") or {}
        if hasattr(patient, "to_dict"):
            patient = patient.to_dict()  # type: ignore[assignment]
        best_m = escape(str(data.get("best_model", "—")))
        acc = float(data.get("accuracy", 0) or 0)

        skip_cols = {
            "prediction_label",
            "prediction_score",
            "Score",
            "risk_score",
            "risk_level",
            "Label",
        }

        # —— Page 1: cover ——
        self.elements.append(Spacer(1, 2 * cm))
        self.elements.append(
            Paragraph(
                f'<para alignment="center"><font size="20" color="#0F766E"><b>{escape(t("pdf_single_title", lang))}</b></font></para>',
                self.styles["Normal"],
            )
        )
        self.elements.append(Spacer(1, 0.6 * cm))
        self.elements.append(
            Paragraph(
                f'<para alignment="center"><font size="11" color="#64748B">{escape(t("pdf_single_subtitle", lang))}</font></para>',
                self.styles["Normal"],
            )
        )
        self.elements.append(Spacer(1, 1.2 * cm))

        cover_rows = [
            [t("pdf_label_doctor", lang), doctor],
            [t("pdf_label_date", lang), gen_time.strftime("%d/%m/%Y")],
            [t("pdf_label_time", lang), gen_time.strftime("%H:%M")],
            [t("pdf_label_model", lang), best_m],
            [t("pdf_label_reliability", lang), f"{acc:.1f}%"],
            [t("pdf_single_risk_label", lang), f"{risk * 100:.0f}% ({level})"],
        ]
        ct = Table(cover_rows, colWidths=[6 * cm, 10 * cm])
        ct.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0FDFA")),
                    ("BACKGROUND", (1, 0), (1, -1), colors.white),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0F766E")),
                    ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#0F172A")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#14B8A6")),
                ]
            )
        )
        self.elements.append(ct)
        self.elements.append(Spacer(1, 1.5 * cm))
        self.elements.append(
            Paragraph(
                f'<para alignment="center"><font size="9" color="#64748B">{escape(t("pdf_cover_warning_box", lang))}</font></para>',
                self.styles["Normal"],
            )
        )
        self.elements.append(PageBreak())

        # —— Page 2: patient data ——
        self.elements.append(_pt(t("pdf_single_data_title", lang), self.styles["SectionHeader"]))
        rows: List[List[str]] = [[t("pdf_single_col_feature", lang), t("pdf_single_col_value", lang)]]
        for k, v in sorted(patient.items(), key=lambda x: str(x[0])):
            ks = str(k)
            if ks in skip_cols or "prediction" in ks.lower():
                continue
            label = get_feature_name(ks.lower(), lang)
            rows.append([label, "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)])
        if len(rows) < 2:
            rows.append(["—", "—"])
        pt = Table(rows, colWidths=[7 * cm, 8 * cm])
        pt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_TEAL_DARK),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_BG]),
                ]
            )
        )
        self.elements.append(pt)
        self.elements.append(Spacer(1, 0.8 * cm))
        age = patient.get("age", patient.get("Age"))
        sex_lbl = self._sex_label(pd.Series(patient))
        hr = patient.get("thalach", patient.get("max_heart_rate", "—"))
        bp = patient.get("trestbps", patient.get("resting_bp", "—"))
        chol = patient.get("chol", patient.get("cholesterol", "—"))
        self.elements.append(
            _pt(clinical_reasoning_placeholder(age, sex_lbl, hr, bp, chol, lang=lang), self.styles["Small"])
        )
        self.elements.append(PageBreak())

        # —— Page 3: recommendations ——
        self.elements.append(_pt(t("pdf_single_reco_title", lang), self.styles["SectionHeader"]))
        action = suggested_action_for_patient(risk, lang=lang)
        self.elements.append(_ph(f"<b>{escape(t('pdf_single_action_label', lang))}</b> {escape(str(action))}", self.styles["BodyProfessional"]))
        self.elements.append(Spacer(1, 0.5 * cm))
        self.elements.append(_pt(t("pdf_appendix_limits", lang), self.styles["BodyJustified"]))

        doc.build(
            self.elements,
            onFirstPage=self._make_decorate(S),
            onLaterPages=self._make_decorate(S),
        )
        buffer.seek(0)
        return buffer.getvalue()

    def _make_decorate(self, S: Dict[str, str]) -> Callable[..., None]:
        def _decorate(canvas: Any, doc: Any) -> None:
            canvas.saveState()
            w, h = A4
            canvas.setFillColor(COLOR_TEAL_DARK)
            canvas.rect(0, h - 0.9 * cm, w, 0.9 * cm, fill=1, stroke=0)
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawString(2 * cm, h - 0.62 * cm, "CardioPredict AI")
            ts = datetime.now().strftime("%d/%m/%Y %H:%M")
            canvas.setFont("Helvetica", 9)
            canvas.drawRightString(w - 2 * cm, h - 0.6 * cm, ts)
            canvas.setFillColor(COLOR_MUTED)
            canvas.setFont("Helvetica-Oblique", 7)
            canvas.drawCentredString(w / 2, 0.8 * cm, S.get("footer_disclaimer", ""))
            pn = canvas.getPageNumber()
            canvas.drawRightString(w - 2 * cm, 0.8 * cm, f"{S.get('footer_page', 'Page')} {pn}")
            canvas.restoreState()

        return _decorate

    def _build_cover_page(self, data: Dict[str, Any], S: Dict[str, str]) -> None:
        gen = data.get("generated_at") or datetime.now()
        doctor = escape(str(data.get("doctor_name") or "—"))
        rel = float(data.get("reliability_pct", 0) or 0)
        best_m = escape(str(data.get("best_model", "—")))

        self.elements.append(Spacer(1, 2 * cm))
        logo_table = Table(
            [
                [
                    Paragraph(
                        '<font size="22" color="#0F766E"><b>CardioPredict AI</b></font>',
                        self.styles["Normal"],
                    )
                ]
            ],
            colWidths=[16 * cm],
        )
        logo_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        self.elements.append(logo_table)
        self.elements.append(Spacer(1, 0.5 * cm))
        self.elements.append(
            Paragraph(
                f'<para alignment="center"><font size="12" color="#64748B">{escape(S["cover_title"])}</font></para>',
                self.styles["Normal"],
            )
        )
        self.elements.append(
            Paragraph(
                f'<para alignment="center"><font size="11" color="#64748B">{escape(S["cover_subtitle"])}</font></para>',
                self.styles["Normal"],
            )
        )
        self.elements.append(Spacer(1, 1.2 * cm))

        cover_data = [
            [S["label_doctor"], doctor],
            [S["label_date"], gen.strftime("%d/%m/%Y")],
            [S["label_time"], gen.strftime("%H:%M")],
            [S["label_patients"], str(data.get("n_patients", 0))],
            [S["label_model"], best_m],
            [S["label_reliability"], f"{rel:.1f}%"],
        ]
        cover_table = Table(cover_data, colWidths=[6 * cm, 10 * cm])
        cover_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0FDFA")),
                    ("BACKGROUND", (1, 0), (1, -1), colors.white),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0F766E")),
                    ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#0F172A")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                    ("LEFTPADDING", (0, 0), (-1, -1), 18),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#14B8A6")),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#CCFBF1")),
                ]
            )
        )
        self.elements.append(cover_table)
        self.elements.append(Spacer(1, 2.2 * cm))

        disclaimer_body = escape(S["cover_warning_box"])
        disclaimer_title = escape(S["cover_disclaimer_title"])
        disclaimer_text = (
            f'<para alignment="center"><font size="9" color="#64748B">'
            f"<b>{disclaimer_title}</b><br/><br/>{disclaimer_body}</font></para>"
        )
        self.elements.append(Paragraph(disclaimer_text, self.styles["Normal"]))
        self.elements.append(PageBreak())

    def _build_executive_summary(self, data: Dict[str, Any], S: Dict[str, str]) -> None:
        self.elements.append(_pt(S["exec_title"], self.styles["SectionHeader"]))
        self.elements.append(_ph(S["exec_intro_para"], self.styles["BodyProfessional"]))
        self.elements.append(Spacer(1, 0.4 * cm))

        nc, nw, ns = int(data["n_critical"]), int(data["n_warning"]), int(data["n_safe"])
        stats_data = [
            [
                Paragraph(
                    f'<font color="#DC2626" size="28"><b>{nc}</b></font>',
                    self.styles["Normal"],
                ),
                Paragraph(
                    f'<font color="#F59E0B" size="28"><b>{nw}</b></font>',
                    self.styles["Normal"],
                ),
                Paragraph(
                    f'<font color="#16A34A" size="28"><b>{ns}</b></font>',
                    self.styles["Normal"],
                ),
            ],
            [
                Paragraph(
                    f'<font color="#991B1B" size="9"><b>{escape(S["stat_label_critical"])}</b></font>',
                    self.styles["Normal"],
                ),
                Paragraph(
                    f'<font color="#92400E" size="9"><b>{escape(S["stat_label_watch"])}</b></font>',
                    self.styles["Normal"],
                ),
                Paragraph(
                    f'<font color="#166534" size="9"><b>{escape(S["stat_label_safe"])}</b></font>',
                    self.styles["Normal"],
                ),
            ],
        ]
        stats_table = Table(stats_data, colWidths=[5.3 * cm, 5.3 * cm, 5.3 * cm])
        stats_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#FEE2E2")),
                    ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#FEF3C7")),
                    ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#DCFCE7")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                    ("ROUNDEDCORNERS", [8, 8, 8, 8]),
                ]
            )
        )
        self.elements.append(stats_table)
        self.elements.append(Spacer(1, 0.8 * cm))

        self.elements.append(_pt(S["exec_interpretation_title"], self.styles["SubSection"]))
        self.elements.append(_llm(data.get("llm_summary"), self.styles["BodyProfessional"]))
        self.elements.append(Spacer(1, 0.3 * cm))
        self.elements.append(_ph(S["exec_model_line"], self.styles["BodyJustified"]))
        self.elements.append(_ph(S["exec_reliability_line"], self.styles["BodyJustified"]))
        self.elements.append(_ph(S["exec_features_line"], self.styles["BodyJustified"]))
        self.elements.append(PageBreak())

    def _build_methodology_page(self, data: Dict[str, Any], S: Dict[str, str]) -> None:
        self.elements.append(_pt(S["meth_title"], self.styles["SectionHeader"]))
        self.elements.append(_pt(S["meth_question"], self.styles["SubSection"]))
        self.elements.append(_llm(data.get("llm_methodology"), self.styles["LLMBox"]))
        self.elements.append(Spacer(1, 0.3 * cm))
        self.elements.append(_pt(S["meth_steps_title"], self.styles["SubSection"]))
        steps = [
            ["1", S["meth_step1"]],
            ["2", S["meth_step2"]],
            ["3", S["meth_step3"]],
            ["4", S["meth_step4"]],
            ["5", S["meth_step5"]],
        ]
        st = Table(steps, colWidths=[1 * cm, 15 * cm])
        st.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TEXTCOLOR", (0, 0), (0, -1), COLOR_TEAL_DARK),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.25, COLOR_TEAL_LIGHT),
                ]
            )
        )
        self.elements.append(st)
        self.elements.append(PageBreak())

    def _critical_mask(self, df: pd.DataFrame, score: pd.Series) -> pd.Series:
        if "risk_level" in df.columns:
            return df["risk_level"] == "HIGH"
        return score > 0.7

    def _watch_mask(self, df: pd.DataFrame, score: pd.Series) -> pd.Series:
        if "risk_level" in df.columns:
            return df["risk_level"] == "MEDIUM"
        return (score > 0.4) & (score <= 0.7)

    def _sex_label(self, row: pd.Series) -> str:
        v = row.get("sex", row.get("Sex"))
        if v is None or pd.isna(v):
            return "—"
        s = str(v).strip().lower()
        if s in ("1", "1.0", "m", "male"):
            return "M"
        if s in ("0", "0.0", "f", "female"):
            return "F"
        return str(v)

    def _build_critical_patients_page(self, data: Dict[str, Any], S: Dict[str, str]) -> None:
        self.elements.append(_pt(S["crit_title"], self.styles["SectionHeader"]))
        self.elements.append(_pt(S["crit_intro"], self.styles["BodyJustified"]))

        preds: pd.DataFrame = data["predictions_df"]
        score: pd.Series = data["score_series"]
        mask = self._critical_mask(preds, score)
        critical = preds.loc[mask].head(12)
        lang = self.lang

        for i, (idx, patient) in enumerate(critical.iterrows()):
            rs = float(score.loc[idx]) if idx in score.index else float(patient.get("risk_score", 0) or 0)
            age = patient.get("age", patient.get("Age", "—"))
            sex_lbl = self._sex_label(patient)
            hr = patient.get("thalach", patient.get("max_heart_rate", "—"))
            bp = patient.get("trestbps", patient.get("resting_bp", "—"))
            chol = patient.get("chol", patient.get("cholesterol", "—"))
            pid = f"#{int(idx)}"
            reasoning = clinical_reasoning_placeholder(age, sex_lbl, hr, bp, chol, lang=lang)
            action = suggested_action_for_patient(rs, lang=lang)

            block = [
                [f"Patient {pid}", f"{S['table_risk']}: {rs*100:.0f}%"],
                [f"{S['table_age']}: {age}", f"{S['table_sex']}: {sex_lbl}"],
                [f"{S['table_hr']}: {hr}", f"{S['table_bp']}: {bp}"],
                [f"{S['table_chol']}: {chol}", ""],
            ]
            pt_table = Table(block, colWidths=[7.5 * cm, 7.5 * cm])
            pt_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), COLOR_RED_LIGHT),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_RED),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_RED),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            self.elements.append(pt_table)
            self.elements.append(_pt(reasoning, self.styles["Small"]))
            self.elements.append(
                _ph(f"<b>Action:</b> {escape(str(action))}", self.styles["Small"])
            )
            self.elements.append(Spacer(1, 0.25 * cm))

        if data.get("llm_critical_analysis"):
            self.elements.append(_pt(S["crit_global"], self.styles["SubSection"]))
            self.elements.append(_llm(data["llm_critical_analysis"], self.styles["LLMBox"]))
        self.elements.append(PageBreak())

    def _build_watch_list_page(self, data: Dict[str, Any], S: Dict[str, str]) -> None:
        self.elements.append(_pt(S["watch_title"], self.styles["SectionHeader"]))
        self.elements.append(
            _llm(data.get("llm_watch") or S["watch_intro"], self.styles["BodyJustified"])
        )

        preds: pd.DataFrame = data["predictions_df"]
        score: pd.Series = data["score_series"]
        mask = self._watch_mask(preds, score)
        watch = preds.loc[mask].head(25)

        table_data: List[List[str]] = [
            [
                S["table_id"],
                S["table_age"],
                S["table_sex"],
                S["table_hr"],
                S["table_bp"],
                S["table_chol"],
                S["table_risk"],
            ]
        ]
        for idx, patient in watch.iterrows():
            rs = float(score.loc[idx]) if idx in score.index else float(patient.get("risk_score", 0) or 0)
            table_data.append(
                [
                    str(int(idx)),
                    str(patient.get("age", patient.get("Age", "—"))),
                    self._sex_label(patient),
                    str(patient.get("thalach", "—")),
                    str(patient.get("trestbps", "—")),
                    str(patient.get("chol", "—")),
                    f"{rs*100:.0f}%",
                ]
            )

        if len(table_data) > 1:
            wt = Table(table_data, colWidths=[1.8 * cm, 1.5 * cm, 1.5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm])
            wt.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TEAL_DARK),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_BG]),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            self.elements.append(wt)
        self.elements.append(PageBreak())

    def _build_phenotypes_page(self, data: Dict[str, Any], S: Dict[str, str]) -> None:
        self.elements.append(_pt(S["pheno_title"], self.styles["SectionHeader"]))
        self.elements.append(_pt(S["pheno_intro"], self.styles["BodyJustified"]))
        if data.get("llm_phenotypes"):
            self.elements.append(_llm(data["llm_phenotypes"], self.styles["LLMBox"]))

        profiles = data.get("cluster_profiles")
        labels = data.get("cluster_labels") or {}
        if profiles is not None and len(profiles):
            for cid, lbl in sorted(labels.items(), key=lambda x: str(x[0])):
                try:
                    row = profiles.loc[cid]
                    cnt = int(row.get("patient_count", 0))
                except Exception:
                    continue
                line = (
                    f"<b>{escape(str(lbl))}</b> — {cnt} patients "
                    f"(mean profile in analytics table)."
                )
                self.elements.append(_ph(line, self.styles["Small"]))
        self.elements.append(PageBreak())

    def _build_risk_factors_page(self, data: Dict[str, Any], S: Dict[str, str]) -> None:
        self.elements.append(_pt(S["risk_title"], self.styles["SectionHeader"]))
        fi = data.get("feature_importance")
        if fi is not None and len(fi):
            sub = fi.head(8).copy()
            label_col = "label" if "label" in sub.columns else "factor"
            fig, ax = plt.subplots(figsize=(7.5, 4.5))
            y_labels = [str(x) for x in sub[label_col].tolist()]
            ax.barh(y_labels[::-1], sub["importance"].values[::-1], color="#0F766E")
            ax.set_xlabel(S["chart_xlabel"])
            ax.set_title(S["chart_importance_title"])
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            plt.tight_layout()
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format="png", dpi=120, bbox_inches="tight")
            plt.close(fig)
            img_buf.seek(0)
            self.elements.append(Image(img_buf, width=16 * cm, height=9 * cm))

        if data.get("llm_risk_factors"):
            self.elements.append(Spacer(1, 0.3 * cm))
            self.elements.append(_llm(data["llm_risk_factors"], self.styles["LLMBox"]))
        self.elements.append(PageBreak())

    def _build_appendix_page(self, data: Dict[str, Any], S: Dict[str, str]) -> None:
        self.elements.append(_pt(S["appendix_title"], self.styles["SectionHeader"]))
        av = str(data.get("app_version", "1.0"))
        appendix_data = [
            [S["appendix_label_tool"], f"CardioPredict AI v{av}"],
            [S["appendix_label_automl"], "PyCaret 3.x"],
            [S["appendix_label_llm"], "OpenAI API (optional)"],
            [S["appendix_label_npat"], str(data.get("n_patients", 0))],
            [S["appendix_label_nfeat"], str(data.get("n_features", "—"))],
            [S["appendix_label_ncompared"], str(data.get("n_models", 0))],
            [S["appendix_label_time"], data["generated_at"].strftime("%d/%m/%Y %H:%M:%S")],
        ]

        at = Table(appendix_data, colWidths=[6.5 * cm, 9 * cm])
        at.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), COLOR_TEAL_LIGHT),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.25, COLOR_TEAL_LIGHT),
                ]
            )
        )
        self.elements.append(at)
        self.elements.append(Spacer(1, 0.6 * cm))
        self.elements.append(_pt(S["appendix_limits"], self.styles["BodyJustified"]))

        preds: pd.DataFrame = data["predictions_df"]
        preview = preds.head(35)
        rows: List[List[str]] = [list(preview.columns.astype(str))]
        for _, r in preview.iterrows():
            rows.append([str(x)[:40] for x in r.tolist()])
        pt = Table(rows, repeatRows=1)
        pt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_TEAL_DARK),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.2, colors.lightgrey),
                ]
            )
        )
        self.elements.append(Spacer(1, 0.4 * cm))
        self.elements.append(pt)
