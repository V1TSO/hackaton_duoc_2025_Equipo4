"""
Configuración global para el proyecto ML NHANES.
Define constantes, paths y funciones de inicialización.
"""
import os
import random
import logging
from pathlib import Path
import numpy as np

# Semilla para reproducibilidad
SEED = 42

# Paths base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
KB_DIR = BASE_DIR / "kb"

# Crear directorios si no existen
MODELS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Configuración de split temporal
TRAIN_CYCLES = ['2015-2016']  # Ciclos para entrenamiento
TEST_CYCLES = ['2017-2018']    # Ciclos para test

# Columnas prohibidas (anti-fuga)
LAB_FORBIDDEN_FILE = BASE_DIR / "LAB_COLUMNS_FORBIDDEN.txt"

# Hiperparámetros del modelo optimizado
XGBOOST_PARAMS = {
    'n_estimators': 800,
    'learning_rate': 0.02,
    'max_depth': 6,
    'subsample': 0.85,
    'colsample_bytree': 0.85,
    'min_child_weight': 3,
    'gamma': 0.1,
    'objective': 'binary:logistic',
    'eval_metric': ['auc', 'logloss'],
    'random_state': SEED,
    'early_stopping_rounds': 50,
    'n_jobs': -1
}

# Configuración de calibración
CALIBRATION_SPLIT_SIZE = 0.2
CALIBRATION_METHODS = ['isotonic', 'sigmoid']

# Configuración de SHAP
SHAP_SAMPLE_SIZE = 1000  # Para visualizaciones (si dataset muy grande)
TOP_DRIVERS = 5  # Top N features para drivers locales

# Configuración de fairness
SENSITIVE_FEATURES = ['sex_male', 'age_group', 'race']
FAIRNESS_METRICS = ['auroc', 'brier', 'prevalence']

# Logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO


def set_seeds(seed: int = SEED):
    """
    Fija todas las semillas para reproducibilidad.
    
    Args:
        seed: Valor de la semilla (default: SEED global)
    """
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    
    # Para XGBoost, la semilla se pasa en los parámetros del modelo
    print(f"✅ Semillas fijadas a {seed}")


def setup_logging(log_file: str = None):
    """
    Configura el sistema de logging.
    
    Args:
        log_file: Archivo de log opcional (default: solo consola)
    """
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_path = REPORTS_DIR / log_file
        handlers.append(logging.FileHandler(log_path))
    
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=handlers
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configurado - nivel {LOG_LEVEL}")
    
    return logger


def get_lab_forbidden_columns():
    """
    Lee las columnas prohibidas del archivo LAB_COLUMNS_FORBIDDEN.txt.
    
    Returns:
        set: Conjunto de nombres de columnas prohibidas
    """
    if not LAB_FORBIDDEN_FILE.exists():
        return set()
    
    with open(LAB_FORBIDDEN_FILE, 'r') as f:
        forbidden = {line.strip() for line in f if line.strip()}
    
    return forbidden


if __name__ == "__main__":
    # Test de configuración
    set_seeds()
    logger = setup_logging()
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Models directory: {MODELS_DIR}")
    logger.info(f"Reports directory: {REPORTS_DIR}")
    logger.info(f"Train cycles: {TRAIN_CYCLES}")
    logger.info(f"Test cycles: {TEST_CYCLES}")
    print("✅ Configuración cargada correctamente")

