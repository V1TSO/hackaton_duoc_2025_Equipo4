import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import shap

from .model_loader import load_model_bundle
from .feature_engineering import (
    build_cardiovascular_feature_frame,
    build_feature_frame,
    get_feature_description,
)

logger = logging.getLogger(__name__)

REFERRAL_THRESHOLD = 0.70
TOP_DRIVERS_COUNT = 5

_explainers: Dict[str, Optional[shap.TreeExplainer]] = {}


def get_explainer(model_type: str = "diabetes"):
    """Get or create SHAP explainer for a specific model type."""
    if model_type != "diabetes":
        return None

    if model_type not in _explainers:
        try:
            model, _, _ = load_model_bundle(model_type)
            _explainers[model_type] = shap.TreeExplainer(model)
            logger.info("SHAP explainer initialized for %s", model_type)
        except Exception as e:
            logger.warning("Failed to initialize SHAP explainer for %s: %s", model_type, e)
            _explainers[model_type] = None

    return _explainers[model_type]

def predict_risk(
    age: int,
    sex: str,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    waist_cm: Optional[float] = None,
    sleep_hours: Optional[float] = None,
    smokes_cig_day: Optional[int] = None,
    days_mvpa_week: Optional[int] = None,
    bmi: Optional[float] = None,
    systolic_bp: Optional[float] = None,
    total_cholesterol: Optional[float] = None,
    model_type: str = "diabetes",
    glucosa_mgdl: Optional[float] = None,
    hdl_mgdl: Optional[float] = None,
    trigliceridos_mgdl: Optional[float] = None,
    ldl_mgdl: Optional[float] = None
) -> Dict[str, Any]:
    """Predict cardiometabolic risk using the requested local model."""

    normalized_type = (model_type or "diabetes").lower()

    try:
        logger.info("=" * 80)
        logger.info("🔬 USING LOCAL ML MODEL (%s)", normalized_type.upper())
        logger.info(
            "   Input: age=%s, sex=%s, bmi=%s, height_cm=%s, weight_kg=%s, waist_cm=%s, sleep_hours=%s, cig_day=%s, mvpa_days=%s, sys_bp=%s, chol=%s",
            age,
            sex,
            bmi,
            height_cm,
            weight_kg,
            waist_cm,
            sleep_hours,
            smokes_cig_day,
            days_mvpa_week,
            systolic_bp,
            total_cholesterol,
        )
        logger.info("=" * 80)

        model, imputer, feature_names = load_model_bundle(normalized_type)
        logger.info("✓ Model loaded: %s", type(model).__name__)

        if normalized_type == "cardiovascular":
            features_df = build_cardiovascular_feature_frame(
                edad=age,
                genero=sex,
                imc=bmi,
                altura_cm=height_cm,
                peso_kg=weight_kg,
                circunferencia_cintura=waist_cm,
                glucosa_mgdl=glucosa_mgdl,
                hdl_mgdl=hdl_mgdl,
                trigliceridos_mgdl=trigliceridos_mgdl,
                ldl_mgdl=ldl_mgdl,
                feature_names=feature_names,
            )

            risk_score = float(model.predict_proba(features_df)[0, 1])
            drivers = _get_cardiovascular_drivers(model, features_df, feature_names)
        else:
            X = build_feature_frame(
                age=age,
                sex=sex,
                height_cm=height_cm,
                weight_kg=weight_kg,
                waist_cm=waist_cm,
                sleep_hours=sleep_hours,
                smokes_cig_day=smokes_cig_day,
                days_mvpa_week=days_mvpa_week,
                bmi=bmi,
                systolic_bp=systolic_bp,
                total_cholesterol=total_cholesterol,
                feature_names=feature_names,
            )

            if imputer is None:
                raise RuntimeError("Imputer is required for diabetes model but was not loaded.")

            X_imp = imputer.transform(X)
            features_df = pd.DataFrame(X_imp, columns=feature_names)
            risk_score = float(model.predict_proba(X_imp)[0, 1])
            drivers = _get_diabetes_drivers(model, features_df, feature_names)

        risk_level, recommendation = _interpret_risk(risk_score)

        logger.info("✓ Prediction complete: score=%.3f, level=%s", risk_score, risk_level)
        logger.info("=" * 80)

        return {
            "score": risk_score,
            "risk_level": risk_level,
            "drivers": drivers,
            "recommendation": recommendation,
            "model_used": normalized_type,
        }

    except Exception as exc:
        logger.error("Error in prediction: %s", exc, exc_info=True)
        raise


def _interpret_risk(score: float) -> tuple[str, str]:
    """
    Returns (risk_level, recommendation) where risk_level is in English for DB storage.
    """
    if score < 0.3:
        return "low", "Mantener hábitos saludables"
    if score < 0.6:
        return "moderate", "Mejorar estilo de vida con coaching personalizado"

    recommendation = "Consultar con profesional de salud urgentemente"
    if score >= REFERRAL_THRESHOLD:
        recommendation += " y coordinar evaluación médica profesional"
    return "high", recommendation


def _get_diabetes_drivers(model, features_df: pd.DataFrame, feature_names: List[str]) -> List[Dict[str, Any]]:
    drivers: List[Dict[str, Any]] = []
    feature_index_map = {name: idx for idx, name in enumerate(feature_names)}

    explainer = get_explainer("diabetes")
    if explainer is not None:
        try:
            shap_values = explainer.shap_values(features_df)

            if isinstance(shap_values, list):
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]

            row_shap = shap_values[0]
            shap_importance = [
                (feat, abs(row_shap[idx])) for feat, idx in feature_index_map.items()
            ]
            shap_importance.sort(key=lambda x: x[1], reverse=True)

            for feature, _ in shap_importance[:TOP_DRIVERS_COUNT]:
                idx = feature_index_map[feature]
                shap_val = float(row_shap[idx])
                raw_value = float(features_df.iloc[0, idx])
                drivers.append(
                    {
                        "feature": feature,
                        "description": get_feature_description(feature),
                        "value": raw_value,
                        "shap_value": shap_val,
                        "impact": "aumenta" if shap_val > 0 else "reduce",
                    }
                )
        except Exception as exc:
            logger.warning("SHAP calculation failed for diabetes model: %s", exc)
            drivers.clear()

    if drivers:
        return drivers

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        importance_tuples = [
            (feat, importances[idx]) for feat, idx in feature_index_map.items()
        ]
        importance_tuples.sort(key=lambda x: x[1], reverse=True)

        for feature, importance in importance_tuples[:TOP_DRIVERS_COUNT]:
            idx = feature_index_map[feature]
            value = float(features_df.iloc[0, idx])
            drivers.append(
                {
                    "feature": feature,
                    "description": get_feature_description(feature),
                    "value": value,
                    "shap_value": float(importance),
                    "impact": "aumenta" if importance > 0 else "reduce",
                }
            )
    else:
        key_features = ['bmi', 'age', 'waist_height_ratio', 'lifestyle_risk_score', 'central_obesity']
        for feature in key_features[:TOP_DRIVERS_COUNT]:
            if feature in feature_index_map:
                idx = feature_index_map[feature]
                drivers.append(
                    {
                        "feature": feature,
                        "description": get_feature_description(feature),
                        "value": float(features_df.iloc[0, idx]),
                        "shap_value": 0.0,
                        "impact": "aumenta",
                    }
                )

    return drivers


def _get_cardiovascular_drivers(model, features_df: pd.DataFrame, feature_names: List[str]) -> List[Dict[str, Any]]:
    drivers: List[Dict[str, Any]] = []

    try:
        pipeline = None
        if hasattr(model, "calibrated_classifiers_") and model.calibrated_classifiers_:
            pipeline = model.calibrated_classifiers_[0].estimator
        elif hasattr(model, "estimator"):
            pipeline = model.estimator

        if pipeline is None or not hasattr(pipeline, "named_steps"):
            raise AttributeError("Cardiovascular pipeline does not expose named_steps")

        preprocessor = pipeline.named_steps.get("pre")
        classifier = pipeline.named_steps.get("clf")
        if preprocessor is None or classifier is None:
            raise AttributeError("Cardiovascular pipeline is missing expected steps")

        scaled = preprocessor.transform(features_df)

        try:
            transformed_names = [
                str(name).split("__", 1)[-1] for name in preprocessor.get_feature_names_out()
            ]
        except Exception:
            transformed_names = feature_names or list(features_df.columns)

        contributions = scaled[0] * classifier.coef_[0]
        pairs = list(zip(transformed_names, contributions))
        pairs.sort(key=lambda x: abs(x[1]), reverse=True)

        for feature, contrib in pairs[:TOP_DRIVERS_COUNT]:
            raw_value = features_df.iloc[0].get(feature, np.nan)
            drivers.append(
                {
                    "feature": feature,
                    "description": get_feature_description(feature),
                    "value": float(raw_value) if not pd.isna(raw_value) else None,
                    "shap_value": float(contrib),
                    "impact": "aumenta" if contrib > 0 else "reduce",
                }
            )

    except Exception as exc:
        logger.warning("Unable to compute cardiovascular drivers precisely: %s", exc)
        ordered_features = feature_names or list(features_df.columns)
        for feature in ordered_features[:TOP_DRIVERS_COUNT]:
            raw_value = features_df.iloc[0].get(feature, np.nan)
            drivers.append(
                {
                    "feature": feature,
                    "description": get_feature_description(feature),
                    "value": float(raw_value) if not pd.isna(raw_value) else None,
                    "shap_value": 0.0,
                    "impact": "aumenta",
                }
            )
            if len(drivers) >= TOP_DRIVERS_COUNT:
                break

    return drivers

