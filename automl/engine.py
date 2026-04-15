"""PyCaret AutoML wrapper for CardioPredict AI."""

from __future__ import annotations

import io
import json
import logging
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Persisted production model (clinic mode — predict without target)
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_BASENAME = MODEL_DIR / "cardiac_model"
META_PATH = MODEL_DIR / "model_metadata.json"

# Suppress noisy sklearn / PyCaret warnings in the UI
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def _cluster_assignment_column(df: pd.DataFrame) -> Optional[str]:
    for c in df.columns:
        cs = str(c).lower()
        if cs in ("cluster", "clusters") or "cluster" in cs:
            return str(c)
    return None


class AutoMLEngine:
    def __init__(self) -> None:
        self.setup_done = False
        self.best_model: Any = None
        self.leaderboard: Optional[pd.DataFrame] = None
        self.predictions: Optional[pd.DataFrame] = None
        self.target_column: Optional[str] = None
        self.raw_df: Optional[pd.DataFrame] = None
        self.positive_label: Any = None
        self.last_error: Optional[str] = None
        # K-Means phenotyping (PyCaret clustering — separate experiment from classification)
        self.clustered_data: Optional[pd.DataFrame] = None
        self.kmeans_model: Any = None
        self.cluster_metrics: Optional[pd.DataFrame] = None
        # Production / clinic (saved model metadata)
        self.clinical_model_name: Optional[str] = None
        self.clinical_accuracy_pct: Optional[float] = None
        self.clinical_auc: Optional[float] = None
        self.feature_columns: Optional[list[str]] = None
        self.n_training_samples: int = 0

    def initialize(self, data: pd.DataFrame, target_column: str) -> bool:
        """Run PyCaret setup with defaults suited to tabular medical data."""
        self.last_error = None
        try:
            from pycaret.classification import setup

            self.raw_df = data.reset_index(drop=True).copy()
            self.target_column = target_column

            setup(
                data=self.raw_df,
                target=target_column,
                session_id=42,
                verbose=False,
                html=False,
                fix_imbalance=True,
                remove_multicollinearity=True,
                multicollinearity_threshold=0.9,
                normalize=True,
                normalize_method="zscore",
                remove_outliers=False,
            )
            self.setup_done = True
            # Infer "positive" class for risk (higher = worse) when binary
            y = self.raw_df[target_column]
            if y.nunique() == 2:
                vals = sorted(y.dropna().unique(), key=lambda x: str(x))
                self.positive_label = vals[-1]
            else:
                self.positive_label = None
            return True
        except Exception as e:
            logger.exception("PyCaret setup failed")
            self.last_error = self._friendly_error(e)
            self.setup_done = False
            return False

    def compare_all_models(self) -> tuple[Optional[pd.DataFrame], bool]:
        """Train and compare models; keep leaderboard sorted by AUC when present."""
        self.last_error = None
        if not self.setup_done:
            self.last_error = "Setup is not complete yet."
            return None, False
        try:
            from pycaret.classification import compare_models, pull

            kwargs: dict[str, Any] = {
                "sort": "AUC",
                "fold": 5,
                "n_select": 1,
                "verbose": False,
            }
            include = [
                "lr",
                "knn",
                "nb",
                "dt",
                "svm",
                "rf",
                "et",
                "gbc",
                "ada",
                "lightgbm",
                "xgboost",
                "catboost",
                "mlp",
                "qda",
                "lda",
            ]
            try:
                self.best_model = compare_models(**kwargs, include=include, turbo=True)
            except TypeError:
                try:
                    self.best_model = compare_models(**kwargs, include=include)
                except TypeError:
                    try:
                        self.best_model = compare_models(**kwargs, turbo=True)
                    except TypeError:
                        self.best_model = compare_models(**kwargs)

            lb = pull()
            if lb is None or (isinstance(lb, pd.DataFrame) and lb.empty):
                self.last_error = "Model comparison finished but no leaderboard was returned."
                return None, False

            self.leaderboard = lb.copy()
            if "AUC" in self.leaderboard.columns:
                self.leaderboard = self.leaderboard.sort_values(
                    "AUC", ascending=False, na_position="last"
                )
            self.leaderboard = self.leaderboard.head(15)
            return self.leaderboard, True
        except Exception as e:
            logger.exception("compare_models failed")
            self.last_error = self._friendly_error(e)
            return None, False

    def _score_column(self, df: pd.DataFrame) -> Optional[str]:
        for name in ("prediction_score", "Score"):
            if name in df.columns:
                return name
        candidates = [c for c in df.columns if "score" in c.lower()]
        return candidates[0] if candidates else None

    def _risk_from_row(self, score: float) -> str:
        if score > 0.7:
            return "HIGH"
        if score >= 0.4:
            return "MEDIUM"
        return "LOW"

    def predict_risk(self, data: Optional[pd.DataFrame] = None) -> tuple[Optional[pd.DataFrame], bool]:
        """Predict on held data or full training frame; add risk_level."""
        self.last_error = None
        if not self.setup_done or self.best_model is None:
            self.last_error = "Train a model first."
            return None, False
        try:
            from pycaret.classification import predict_model

            src = data if data is not None else self.raw_df
            if src is None:
                return None, False

            out = predict_model(self.best_model, data=src.copy())
            score_col = self._score_column(out)
            if score_col is None:
                # Fallback: use prediction probability columns if present
                prob_cols = [c for c in out.columns if str(c).lower().startswith("p_")]
                if prob_cols:
                    # Use max probability as risk intensity for multi-class
                    out["_risk_score"] = out[prob_cols].max(axis=1)
                    score_col = "_risk_score"
                else:
                    self.last_error = "Could not find probability scores in predictions."
                    return out, False

            scores = pd.to_numeric(out[score_col], errors="coerce").fillna(0.0)
            # PyCaret score is often probability of the *predicted* class; map to P(positive outcome)
            if self.positive_label is not None and "prediction_label" in out.columns:
                pl = out["prediction_label"]
                pos = self.positive_label
                scores = np.where(pl == pos, scores, 1.0 - scores)
                scores = pd.Series(scores, index=out.index).clip(0.0, 1.0)

            out["risk_score"] = scores
            out["risk_level"] = out["risk_score"].apply(self._risk_from_row)
            self.predictions = out
            return out, True
        except Exception as e:
            logger.exception("predict_model failed")
            self.last_error = self._friendly_error(e)
            return None, False

    def explain_patient(self, patient_index: int) -> tuple[Optional[Any], str]:
        """SHAP or reason-style explanation for one row."""
        self.last_error = None
        if self.raw_df is None or self.target_column is None:
            return None, "No dataset loaded."
        if patient_index < 0 or patient_index >= len(self.raw_df):
            return None, "That patient row is not in the current data."

        narrative = ""
        try:
            from pycaret.classification import interpret_model

            try:
                fig = interpret_model(
                    self.best_model,
                    plot="reason",
                    observation=patient_index,
                    save=False,
                    verbose=False,
                )
            except TypeError:
                fig = interpret_model(
                    self.best_model,
                    plot="reason",
                    observation=patient_index,
                    verbose=False,
                )
            return fig, narrative
        except Exception:
            pass

        try:
            row = self.raw_df.drop(columns=[self.target_column]).iloc[patient_index]
            rest = self.raw_df.drop(columns=[self.target_column])
            numeric = rest.select_dtypes(include=[np.number])
            parts: list[str] = []
            for col in numeric.columns:
                v = row[col]
                mu = numeric[col].mean()
                if pd.notna(v) and pd.notna(mu) and mu != 0:
                    diff = float(v) - float(mu)
                    if abs(diff) > 0.5 * float(numeric[col].std() or 1):
                        direction = "higher" if diff > 0 else "lower"
                        parts.append(f"{col} is noticeably {direction} than typical ({v:.2g} vs average ~{mu:.2g})")
            narrative = (
                "Here is a simple comparison to other patients in this file:\n"
                + ("\n".join(parts[:8]) if parts else "Values are close to the group average for key numeric measures.")
            )
            return None, narrative
        except Exception as e:
            self.last_error = self._friendly_error(e)
            return None, str(e)

    def get_feature_importance(self) -> tuple[Optional[pd.DataFrame], bool]:
        """Global importance table when the underlying estimator exposes it."""
        self.last_error = None
        if self.best_model is None:
            return None, False
        imp = self._importance_from_model()
        return imp, imp is not None

    def _importance_from_model(self) -> Optional[pd.DataFrame]:
        try:
            est = getattr(self.best_model, "steps", None)
            m = self.best_model
            if est is not None:
                m = est[-1][1]
            if hasattr(m, "feature_importances_"):
                names = list(self.raw_df.drop(columns=[self.target_column]).columns)  # type: ignore[union-attr]
                imp = np.asarray(m.feature_importances_)
                if len(names) != len(imp):
                    names = [f"f{i}" for i in range(len(imp))]
                df = pd.DataFrame({"factor": names, "importance": imp}).sort_values(
                    "importance", ascending=False
                )
                return df.head(20)
        except Exception:
            return None
        return None

    def what_if_analysis(
        self, patient_index: int, changes: dict[str, Any]
    ) -> tuple[Optional[pd.DataFrame], Optional[str]]:
        if self.raw_df is None or self.target_column is None:
            return None, "No data loaded."
        row = self.raw_df.iloc[[patient_index]].copy()
        for k, v in changes.items():
            if k in row.columns:
                row[k] = v
        ok_df, ok = self.predict_risk(row)
        if not ok or ok_df is None:
            return None, self.last_error
        return ok_df, None

    def predictions_to_csv_bytes(self) -> bytes:
        if self.predictions is None:
            return b""
        buf = io.StringIO()
        self.predictions.to_csv(buf, index=False)
        return buf.getvalue().encode("utf-8")

    def save_trained_model(self) -> bool:
        """Save trained PyCaret model + metadata for clinic / production inference."""
        self.last_error = None
        if self.best_model is None or self.raw_df is None or not self.target_column:
            self.last_error = "No trained model or training data to save."
            return False
        try:
            from pycaret.classification import save_model

            save_model(self.best_model, str(MODEL_BASENAME))

            lb = self.leaderboard
            acc_f: Optional[float] = None
            auc_f: Optional[float] = None
            model_name = self.clinical_model_name
            if lb is not None and len(lb):
                row = lb.iloc[0]
                model_name = model_name or str(row.get("Model", ""))
                if "Accuracy" in row.index:
                    try:
                        a = float(row["Accuracy"])
                        acc_f = a * 100.0 if a <= 1.0 else a
                    except (TypeError, ValueError):
                        acc_f = None
                if "AUC" in row.index:
                    try:
                        auc_f = float(row["AUC"])
                    except (TypeError, ValueError):
                        auc_f = None

            feats = [c for c in self.raw_df.columns if c != self.target_column]
            self.feature_columns = feats
            self.n_training_samples = int(len(self.raw_df))
            self.clinical_model_name = model_name
            self.clinical_accuracy_pct = acc_f
            self.clinical_auc = auc_f

            pos = self.positive_label
            pos_json: Any
            if pos is None or isinstance(pos, (str, int, float, bool)):
                pos_json = pos
            else:
                pos_json = str(pos)

            metadata = {
                "model_name": str(model_name or ""),
                "accuracy": float(acc_f) if acc_f is not None else 0.0,
                "auc": float(auc_f) if auc_f is not None else 0.0,
                "trained_on": datetime.now().isoformat(),
                "n_training_samples": int(self.n_training_samples),
                "feature_columns": list(feats),
                "target_column": str(self.target_column),
                "positive_label": pos_json,
            }
            with open(META_PATH, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            logger.exception("save_trained_model failed")
            self.last_error = self._friendly_error(e)
            return False

    def load_trained_model(self) -> bool:
        """Load a previously saved model from disk (no PyCaret setup required)."""
        self.last_error = None
        pkl_path = Path(str(MODEL_BASENAME) + ".pkl")
        if not pkl_path.exists() or not META_PATH.exists():
            return False
        try:
            from pycaret.classification import load_model

            self.best_model = load_model(str(MODEL_BASENAME))
            if META_PATH.exists():
                with open(META_PATH, encoding="utf-8") as f:
                    meta = json.load(f)
                self.clinical_model_name = str(meta.get("model_name", ""))
                self.clinical_accuracy_pct = float(meta.get("accuracy", 0.0))
                self.clinical_auc = float(meta.get("auc", 0.0))
                self.n_training_samples = int(meta.get("n_training_samples", 0))
                self.feature_columns = list(meta.get("feature_columns", []))
                pl = meta.get("positive_label")
                self.positive_label = pl
                tc = meta.get("target_column")
                if tc:
                    self.target_column = str(tc)
            # Disk-only model: do not mark PyCaret setup complete (no in-memory training frame).
            self.setup_done = False
            self.raw_df = None
            return self.best_model is not None
        except Exception as e:
            logger.exception("load_trained_model failed")
            self.last_error = self._friendly_error(e)
            return False

    def predict_new_patients(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """Score new rows without a target column (production clinic use)."""
        from pycaret.classification import predict_model

        if self.best_model is None:
            raise RuntimeError("No model loaded. Train or load a model first.")

        data = new_data.copy()
        for col in ("target", "Target"):
            if col in data.columns:
                data = data.drop(columns=[col])

        if self.feature_columns:
            missing = [c for c in self.feature_columns if c not in data.columns]
            if missing:
                raise ValueError(f"Missing feature columns: {missing}")
            extra = [c for c in data.columns if c not in self.feature_columns]
            if extra:
                data = data.drop(columns=extra, errors="ignore")
            data = data[self.feature_columns]

        predictions = predict_model(self.best_model, data=data)

        score_col = self._score_column(predictions)
        if score_col is None:
            prob_cols = [c for c in predictions.columns if str(c).lower().startswith("p_")]
            if prob_cols:
                predictions["_risk_score"] = predictions[prob_cols].max(axis=1)
                score_col = "_risk_score"
            else:
                predictions["risk_level"] = "LOW"
                return predictions

        scores = pd.to_numeric(predictions[score_col], errors="coerce").fillna(0.0)
        if self.positive_label is not None and "prediction_label" in predictions.columns:
            pl = predictions["prediction_label"]
            pos = self.positive_label
            scores = np.where(pl == pos, scores, 1.0 - scores)
            scores = pd.Series(scores, index=predictions.index).clip(0.0, 1.0)

        predictions["risk_score"] = scores
        predictions["risk_level"] = predictions["risk_score"].apply(self._risk_from_row)
        return predictions

    def run_clustering(
        self,
        data: pd.DataFrame,
        *,
        target_column: Optional[str] = None,
        n_clusters: int = 4,
    ) -> Tuple[Optional[pd.DataFrame], bool, Optional[str]]:
        """K-Means via PyCaret clustering (unsupervised). Drops outcome column if provided."""
        self.last_error = None
        try:
            from pycaret.clustering import assign_model, create_model, pull, setup as cluster_setup
        except Exception as e:
            return None, False, self._friendly_error(e)

        cluster_data = data.reset_index(drop=True).copy()
        drop_cols = []
        if target_column and target_column in cluster_data.columns:
            drop_cols.append(target_column)
        for legacy in ("target", "Target", "label", "Label"):
            if legacy in cluster_data.columns and legacy not in drop_cols:
                if target_column is None or legacy != target_column:
                    drop_cols.append(legacy)
        if drop_cols:
            cluster_data = cluster_data.drop(columns=list(dict.fromkeys(drop_cols)))

        if cluster_data.shape[1] < 1:
            return None, False, "No feature columns left after removing the outcome column."

        try:
            cluster_setup(
                data=cluster_data,
                session_id=42,
                verbose=False,
                html=False,
                normalize=True,
                normalize_method="zscore",
            )
        except Exception as e:
            logger.exception("clustering setup failed")
            return None, False, self._friendly_error(e)

        km = None
        try:
            km = create_model("kmeans", num_clusters=int(n_clusters), verbose=False)
        except TypeError:
            try:
                km = create_model("kmeans", n_clusters=int(n_clusters), verbose=False)
            except TypeError:
                try:
                    km = create_model("kmeans", verbose=False)
                except Exception as e:
                    return None, False, self._friendly_error(e)

        try:
            metrics = pull()
            if isinstance(metrics, pd.DataFrame):
                self.cluster_metrics = metrics.copy()
        except Exception:
            self.cluster_metrics = None

        try:
            assigned = assign_model(km, verbose=False)
        except TypeError:
            assigned = assign_model(km)

        self.kmeans_model = km
        self.clustered_data = assigned
        return self.clustered_data, True, None

    def get_cluster_profiles(self) -> Optional[pd.DataFrame]:
        """Mean feature values per cluster + patient counts."""
        if self.clustered_data is None:
            return None
        df = self.clustered_data
        col = _cluster_assignment_column(df)
        if col is None:
            return None
        num = df.select_dtypes(include=[np.number]).columns.tolist()
        num = [c for c in num if c != col]
        if not num:
            return df.groupby(col, observed=True).size().to_frame("patient_count")
        profiles = df.groupby(col, observed=True)[num].mean(numeric_only=True).round(2)
        counts = df.groupby(col, observed=True).size()
        profiles["patient_count"] = counts
        return profiles

    def interpret_clusters_medically(self, lang: str = "fr") -> dict[Any, str]:
        """Heuristic phenotype labels from cluster means (decision-support wording)."""
        profiles = self.get_cluster_profiles()
        if profiles is None or len(profiles) == 0:
            return {}

        labels: dict[Any, str] = {}
        for cluster_id, row in profiles.iterrows():
            age = float(row.get("age", row.get("Age", 0)) or 0)
            chol = float(row.get("chol", row.get("cholesterol", 0)) or 0)
            bp = float(row.get("trestbps", row.get("resting_bp", 0)) or 0)
            hr = float(row.get("thalach", row.get("max_heart_rate", 0)) or 0)

            if lang == "fr":
                if age > 60 and bp > 140:
                    label = "Seniors hypertendus"
                elif age < 45 and hr > 150:
                    label = "Jeunes actifs"
                elif chol > 240:
                    label = "Hypercholestérolémie"
                elif bp > 140 and chol > 200:
                    label = "Syndrome métabolique"
                else:
                    label = "Profil intermédiaire"
            elif lang == "ar":
                if age > 60 and bp > 140:
                    label = "كبار السن بضغط مرتفع"
                elif age < 45 and hr > 150:
                    label = "شباب نشطون"
                elif chol > 240:
                    label = "كوليسترول عالي"
                elif bp > 140 and chol > 200:
                    label = "متلازمة الأيض"
                else:
                    label = "ملف متوسط"
            else:
                if age > 60 and bp > 140:
                    label = "Elderly hypertensive"
                elif age < 45 and hr > 150:
                    label = "Young athletes"
                elif chol > 240:
                    label = "Hypercholesterolemia"
                elif bp > 140 and chol > 200:
                    label = "Metabolic syndrome"
                else:
                    label = "Intermediate profile"

            labels[cluster_id] = label

        return labels

    def set_best_model_from_leaderboard(self, model_name: str) -> bool:
        """Train a specific model family by name or alias (best-effort)."""
        self.last_error = None
        if not self.setup_done:
            self.last_error = "Setup is not complete yet."
            return False
        try:
            from pycaret.classification import create_model

            mid = self._resolve_model_id(model_name)
            if not mid:
                self.last_error = "Could not match that model name. Try a name from the leaderboard."
                return False
            self.best_model = create_model(mid, verbose=False)
            return True
        except Exception as e:
            self.last_error = self._friendly_error(e)
            return False

    @staticmethod
    def _resolve_model_id(name: str) -> Optional[str]:
        n = name.strip().lower().replace(" ", "").replace("_", "")
        rules: list[tuple[str, str]] = [
            ("randomforest", "rf"),
            ("rf", "rf"),
            ("xgboost", "xgboost"),
            ("lightgbm", "lightgbm"),
            ("catboost", "catboost"),
            ("logistic", "lr"),
            ("lr", "lr"),
            ("svm", "svm"),
            ("rbfsvm", "rbfsvm"),
            ("knn", "knn"),
            ("naivebayes", "nb"),
            ("nb", "nb"),
            ("decisiontree", "dt"),
            ("dt", "dt"),
            ("ada", "ada"),
            ("adaboost", "ada"),
            ("gradientboosting", "gbc"),
            ("gbc", "gbc"),
            ("extratrees", "et"),
            ("et", "et"),
            ("ridge", "ridge"),
            ("lda", "lda"),
            ("qda", "qda"),
        ]
        for needle, mid in rules:
            if needle in n:
                return mid
        return None

    @staticmethod
    def _friendly_error(exc: Exception) -> str:
        msg = str(exc).lower()
        if "memory" in msg:
            return "Not enough memory to finish training. Try a smaller CSV or close other apps."
        if "missing" in msg or "nan" in msg:
            return "Some values are missing or invalid. Fill empty cells or remove broken rows."
        return "Something went wrong while training or predicting. Check your CSV columns and target choice."
