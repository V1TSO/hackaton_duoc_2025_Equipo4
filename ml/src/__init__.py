"""
Módulo ML para predicción de riesgo cardiometabólico NHANES.

Estructura:
- config: Configuración global, paths, hiperparámetros
- features: Feature engineering y validación anti-fuga
- model: Entrenamiento y calibración de XGBoost
- eval: Métricas, fairness analysis y SHAP explanations
"""

__version__ = '1.0.0'
__author__ = 'Equipo 4 - Hackathon NHANES 2025'

# Importaciones principales
from .config import (
    SEED, set_seeds, setup_logging,
    MODELS_DIR, REPORTS_DIR, DATA_DIR,
    TRAIN_CYCLES, TEST_CYCLES
)

from .features import (
    create_base_features,
    create_interaction_features,
    create_categorical_risk_features,
    build_feature_pipeline,
    validate_no_leakage
)

from .model import (
    train_xgboost,
    calibrate_model,
    train_with_calibration_split,
    save_model_bundle,
    load_model_bundle
)

from .eval import (
    calculate_metrics,
    analyze_fairness,
    compute_shap_values,
    get_prediction_drivers,
    generate_reports
)

__all__ = [
    # Config
    'SEED', 'set_seeds', 'setup_logging',
    'MODELS_DIR', 'REPORTS_DIR', 'DATA_DIR',
    'TRAIN_CYCLES', 'TEST_CYCLES',
    
    # Features
    'create_base_features',
    'create_interaction_features',
    'create_categorical_risk_features',
    'build_feature_pipeline',
    'validate_no_leakage',
    
    # Model
    'train_xgboost',
    'calibrate_model',
    'train_with_calibration_split',
    'save_model_bundle',
    'load_model_bundle',
    
    # Eval
    'calculate_metrics',
    'analyze_fairness',
    'compute_shap_values',
    'get_prediction_drivers',
    'generate_reports',
]

