import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib

logger = logging.getLogger(__name__)

_MODEL_TYPES = {"diabetes", "cardiovascular"}


def get_models_dir() -> Path:
    """Get the path to the models directory."""
    return Path(__file__).parent / "models"


def _normalize_model_type(model_type: str) -> str:
    model_type_normalized = (model_type or "diabetes").lower()
    if model_type_normalized not in _MODEL_TYPES:
        raise ValueError(f"Unknown model_type: {model_type}")
    return model_type_normalized


@lru_cache(maxsize=len(_MODEL_TYPES))
def load_model_bundle(model_type: str = "diabetes") -> Tuple[Any, Optional[Any], List[str]]:
    """
    Load the model bundle (model, optional imputer, feature_names) for the requested type.

    Args:
        model_type: Either "diabetes" or "cardiovascular".

    Returns:
        Tuple of (model, imputer_or_none, feature_names).
    """

    normalized_type = _normalize_model_type(model_type)
    models_dir = get_models_dir()

    try:
        if normalized_type == "diabetes":
            model_path = models_dir / "old_model_xgb_calibrated.pkl"
            imputer_path = models_dir / "imputer.pkl"
            feature_names_path = models_dir / "feature_names.pkl"

            logger.info("Loading diabetes model artifacts (old version)...")

            loaded_model = joblib.load(model_path)

            if isinstance(loaded_model, dict):
                model = loaded_model["model"]
                if "imputer" in loaded_model and "feature_names" in loaded_model:
                    imputer = loaded_model["imputer"]
                    feature_names = loaded_model["feature_names"]
                    logger.info("Loaded diabetes bundle with %s features", len(feature_names))
                else:
                    imputer = joblib.load(imputer_path)
                    feature_names = joblib.load(feature_names_path)
                    logger.info("Loaded diabetes model + separate imputer/feature names")
            else:
                model = loaded_model
                imputer = joblib.load(imputer_path)
                feature_names = joblib.load(feature_names_path)
                logger.info("Diabetes model loaded successfully with %s features", len(feature_names))

            return model, imputer, feature_names

        # Cardiovascular model: pipeline already embeds preprocessing and imputation
        cardio_model_path = models_dir / "old_model_cardiovascular.pkl"
        logger.info("Loading cardiovascular model artifact (old version)...")
        cardio_model = joblib.load(cardio_model_path)

        feature_names: List[str] = []
        try:
            pipeline = getattr(cardio_model, "estimator", None) or getattr(cardio_model, "base_estimator", None)
            if pipeline is not None and hasattr(pipeline, "named_steps"):
                preprocessor = pipeline.named_steps.get("pre")
                if preprocessor is not None:
                    try:
                        feature_names_out = preprocessor.get_feature_names_out()
                        feature_names = [str(name).split("__", 1)[-1] for name in feature_names_out]
                    except Exception:
                        transformers = getattr(preprocessor, "transformers_", [])
                        if transformers:
                            feature_names = list(transformers[0][2])
        except Exception as exc:
            logger.warning("Could not infer cardiovascular feature names automatically: %s", exc)

        logger.info("Cardiovascular model loaded with %s derived features", len(feature_names))
        return cardio_model, None, feature_names

    except FileNotFoundError as e:
        logger.error("Model file not found: %s", e)
        raise
    except Exception as e:
        logger.error("Error loading %s model: %s", normalized_type, e)
        raise


def get_model(model_type: str = "diabetes"):
    """Get the loaded model (loads if necessary)."""
    model, _, _ = load_model_bundle(model_type)
    return model


def get_imputer(model_type: str = "diabetes"):
    """Get the loaded imputer (loads if necessary)."""
    _, imputer, _ = load_model_bundle(model_type)
    return imputer


def get_feature_names(model_type: str = "diabetes"):
    """Get the feature names (loads if necessary)."""
    _, _, feature_names = load_model_bundle(model_type)
    return feature_names

