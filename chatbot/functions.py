"""OpenAI tool definitions for CardioPredict AI."""

from typing import Any, List

# OpenAI Chat Completions tool schema
TOOLS: List[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "run_automl",
            "description": "Start cardiac AutoML after patient CSV is loaded and the outcome column is confirmed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_column": {
                        "type": "string",
                        "description": "Exact column name in the CSV that should be predicted.",
                    }
                },
                "required": ["target_column"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_patient",
            "description": "Explain why a specific patient row has their risk level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "integer",
                        "description": "0-based row index in the uploaded table (first data row is 0).",
                    }
                },
                "required": ["patient_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_patients",
            "description": "Filter patients by risk bucket after predictions exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_level": {
                        "type": "string",
                        "enum": ["high", "medium", "low", "all"],
                        "description": "Risk group to show.",
                    }
                },
                "required": ["risk_level"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_feature_importance",
            "description": "Show which risk factors the model relied on most.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "what_if_analysis",
            "description": "Change one or more values for a patient row and estimate a new risk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {"type": "integer"},
                    "changes": {
                        "type": "object",
                        "description": "Map of column name to new value (numbers as JSON numbers, text as strings).",
                        "additionalProperties": True,
                    },
                },
                "required": ["patient_id", "changes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "download_results",
            "description": "Prepare prediction results so the user can download a CSV.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "switch_model",
            "description": "Train a different model family (e.g. Random Forest, XGBoost) using the same data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Model name or keyword from the leaderboard (e.g. Random Forest, xgboost).",
                    }
                },
                "required": ["model_name"],
            },
        },
    },
]
