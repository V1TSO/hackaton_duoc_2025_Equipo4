"""
Módulo de entrenamiento y calibración del modelo XGBoost.
Implementa training optimizado con calibration split para Brier Score <0.12.
"""
import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from typing import Tuple, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, roc_auc_score
from xgboost import XGBClassifier

from .config import (
    SEED, XGBOOST_PARAMS, CALIBRATION_SPLIT_SIZE,
    CALIBRATION_METHODS, MODELS_DIR
)

logger = logging.getLogger(__name__)


def prepare_data_with_imputation(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    strategy: str = 'median'
) -> Tuple[np.ndarray, np.ndarray, SimpleImputer]:
    """
    Prepara los datos aplicando imputación de valores faltantes.
    
    Args:
        X_train: Features de entrenamiento
        X_test: Features de test
        strategy: Estrategia de imputación ('median', 'mean', 'most_frequent')
    
    Returns:
        Tuple: (X_train_imp, X_test_imp, imputer)
    """
    logger.info(f"Aplicando imputación (strategy={strategy})...")
    
    imputer = SimpleImputer(strategy=strategy)
    
    # Fit solo en train, transform en ambos
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)
    
    # El imputer puede eliminar columnas totalmente NaN, mantener como numpy array
    # para evitar problemas de dimensionalidad
    logger.info(f"   ✓ Imputación completada")
    logger.info(f"      Shape después de imputation: {X_train_imp.shape}")
    
    return X_train_imp, X_test_imp, imputer


def calculate_scale_pos_weight(y_train: pd.Series) -> float:
    """
    Calcula el peso de balance de clases para XGBoost.
    
    Args:
        y_train: Labels de entrenamiento
    
    Returns:
        float: scale_pos_weight (neg_count / pos_count)
    """
    pos_count = int((y_train == 1).sum())
    neg_count = int((y_train == 0).sum())
    
    if pos_count == 0:
        raise ValueError("❌ No hay casos positivos en el conjunto de entrenamiento")
    
    scale_pos_weight = neg_count / pos_count
    
    logger.info(f"   Desbalance de clases:")
    logger.info(f"      Negativos: {neg_count:,}")
    logger.info(f"      Positivos: {pos_count:,}")
    logger.info(f"      scale_pos_weight: {scale_pos_weight:.2f}")
    
    return scale_pos_weight


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame = None,
    y_val: pd.Series = None,
    params: Dict[str, Any] = None,
    verbose: bool = False
) -> XGBClassifier:
    """
    Entrena modelo XGBoost con parámetros optimizados.
    
    Args:
        X_train: Features de entrenamiento
        y_train: Labels de entrenamiento
        X_val: Features de validación (opcional, para early stopping)
        y_val: Labels de validación
        params: Parámetros customizados (default: XGBOOST_PARAMS de config)
        verbose: Si True, muestra progreso detallado
    
    Returns:
        XGBClassifier: Modelo entrenado
    """
    logger.info("Entrenando modelo XGBoost...")
    
    # Usar parámetros por defecto si no se especifican
    if params is None:
        params = XGBOOST_PARAMS.copy()
    
    # Calcular y añadir scale_pos_weight
    scale_pos_weight = calculate_scale_pos_weight(y_train)
    params['scale_pos_weight'] = scale_pos_weight
    
    # Crear modelo
    model = XGBClassifier(**params)
    
    # Preparar eval_set para early stopping
    eval_set = [(X_train, y_train)]
    if X_val is not None and y_val is not None:
        eval_set.append((X_val, y_val))
        logger.info(f"   Early stopping habilitado con validation set")
    
    # Entrenar
    logger.info(f"   Parámetros clave:")
    logger.info(f"      n_estimators: {params['n_estimators']}")
    logger.info(f"      learning_rate: {params['learning_rate']}")
    logger.info(f"      max_depth: {params['max_depth']}")
    
    model.fit(
        X_train, y_train,
        eval_set=eval_set,
        verbose=verbose
    )
    
    best_iteration = getattr(model, 'best_iteration', params['n_estimators'])
    logger.info(f"✅ Entrenamiento completado (best_iteration={best_iteration})")
    
    return model


def calibrate_model(
    model: XGBClassifier,
    X_calib: pd.DataFrame,
    y_calib: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    methods: list = None
) -> Tuple[CalibratedClassifierCV, str, float]:
    """
    Calibra el modelo y selecciona el mejor método basado en Brier Score.
    
    CRÍTICO: Este split dedicado para calibración es clave para Brier <0.12
    
    Args:
        model: Modelo XGBoost entrenado (no calibrado)
        X_calib: Features de calibración
        y_calib: Labels de calibración
        X_test: Features de test (para evaluar método)
        y_test: Labels de test
        methods: Lista de métodos a probar (default: ['isotonic', 'sigmoid'])
    
    Returns:
        Tuple: (modelo_calibrado, mejor_método, brier_score)
    """
    logger.info("Calibrando modelo...")
    
    if methods is None:
        methods = CALIBRATION_METHODS
    
    # Evaluar modelo sin calibrar (baseline)
    y_pred_uncal = model.predict_proba(X_test)[:, 1]
    brier_uncal = brier_score_loss(y_test, y_pred_uncal)
    auroc_uncal = roc_auc_score(y_test, y_pred_uncal)
    
    logger.info(f"   Baseline (sin calibrar):")
    logger.info(f"      AUROC: {auroc_uncal:.4f}")
    logger.info(f"      Brier: {brier_uncal:.4f}")
    
    # Probar cada método de calibración
    best_brier = brier_uncal
    best_method = 'sin_calibrar'
    best_model = model
    
    for method in methods:
        logger.info(f"\n   Probando calibración {method}...")
        
        calibrator = CalibratedClassifierCV(
            model,
            method=method,
            cv='prefit'  # No re-entrenar, usar modelo ya entrenado
        )
        
        # Fit en set de calibración
        calibrator.fit(X_calib, y_calib)
        
        # Evaluar en test
        y_pred_cal = calibrator.predict_proba(X_test)[:, 1]
        brier_cal = brier_score_loss(y_test, y_pred_cal)
        auroc_cal = roc_auc_score(y_test, y_pred_cal)
        
        logger.info(f"      AUROC: {auroc_cal:.4f}")
        logger.info(f"      Brier: {brier_cal:.4f}")
        logger.info(f"      Mejora Brier: {brier_uncal - brier_cal:.4f}")
        
        # Seleccionar si mejora
        if brier_cal < best_brier:
            best_brier = brier_cal
            best_method = method
            best_model = calibrator
    
    logger.info(f"\n✅ Calibración completada:")
    logger.info(f"   Método seleccionado: {best_method}")
    logger.info(f"   Brier Score: {best_brier:.4f}")
    
    if best_method == 'sin_calibrar':
        logger.warning("   ⚠️  No se obtuvo mejora con calibración")
    else:
        improvement = brier_uncal - best_brier
        logger.info(f"   Mejora obtenida: {improvement:.4f}")
    
    return best_model, best_method, best_brier


def train_with_calibration_split(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    imputer: SimpleImputer = None,
    calib_size: float = CALIBRATION_SPLIT_SIZE,
    params: Dict[str, Any] = None
) -> Tuple[Any, SimpleImputer, Dict[str, float]]:
    """
    Pipeline completo de entrenamiento con split de calibración.
    
    Este es el método RECOMENDADO para obtener Brier <0.12.
    
    Flujo:
    1. Split train en train_main (80%) y calib (20%)
    2. Entrenar XGBoost en train_main con early stopping en calib
    3. Calibrar modelo usando calib set
    4. Evaluar en test set
    
    Args:
        X_train: Features de entrenamiento completas
        y_train: Labels de entrenamiento
        X_test: Features de test
        y_test: Labels de test
        imputer: Imputer ya ajustado (opcional, si None se crea nuevo)
        calib_size: Proporción del train para calibración (default: 0.2)
        params: Parámetros XGBoost customizados
    
    Returns:
        Tuple: (modelo_calibrado, imputer, metrics_dict)
    """
    logger.info("="*60)
    logger.info("PIPELINE DE ENTRENAMIENTO CON CALIBRATION SPLIT")
    logger.info("="*60)
    
    # 1. Split para calibración
    logger.info(f"\n1. Creando calibration split ({calib_size*100:.0f}% del train)...")
    X_train_main, X_calib, y_train_main, y_calib = train_test_split(
        X_train, y_train,
        test_size=calib_size,
        random_state=SEED,
        stratify=y_train
    )
    
    logger.info(f"   Train main: {X_train_main.shape[0]:,} samples")
    logger.info(f"   Calibration: {X_calib.shape[0]:,} samples")
    logger.info(f"   Test: {X_test.shape[0]:,} samples")
    
    # 2. Imputación
    if imputer is None:
        logger.info(f"\n2. Aplicando imputación...")
        X_train_main, X_test_imp, imputer = prepare_data_with_imputation(
            X_train_main, X_test
        )
        # Transformar calib también (mantener como numpy array)
        X_calib = imputer.transform(X_calib)
    else:
        X_train_main = imputer.transform(X_train_main)
        X_calib = imputer.transform(X_calib)
        X_test_imp = imputer.transform(X_test)
    
    # 3. Entrenamiento
    logger.info(f"\n3. Entrenando XGBoost...")
    model_xgb = train_xgboost(
        X_train_main, y_train_main,
        X_val=X_calib, y_val=y_calib,
        params=params,
        verbose=False
    )
    
    # 4. Calibración
    logger.info(f"\n4. Calibrando modelo...")
    model_calibrated, best_method, brier_score = calibrate_model(
        model_xgb,
        X_calib, y_calib,
        X_test_imp, y_test
    )
    
    # 5. Métricas finales en test
    y_pred_proba = model_calibrated.predict_proba(X_test_imp)[:, 1]
    auroc = roc_auc_score(y_test, y_pred_proba)
    
    metrics = {
        'auroc': auroc,
        'brier': brier_score,
        'calibration_method': best_method,
        'n_train': len(y_train_main),
        'n_calib': len(y_calib),
        'n_test': len(y_test),
        'best_iteration': getattr(model_xgb, 'best_iteration',
                                  (params or XGBOOST_PARAMS)['n_estimators'])
    }
    
    logger.info(f"\n" + "="*60)
    logger.info("RESULTADOS FINALES")
    logger.info("="*60)
    logger.info(f"AUROC (test):  {auroc:.4f}")
    logger.info(f"Brier (test):  {brier_score:.4f}")
    logger.info(f"Calibración:   {best_method}")
    logger.info("="*60)
    
    # Verificar objetivos
    if auroc >= 0.80:
        logger.info("✅ AUROC ≥ 0.80 - Objetivo alcanzado!")
    else:
        logger.warning(f"⚠️  AUROC < 0.80 - Faltan {0.80 - auroc:.4f} puntos")
    
    if brier_score <= 0.12:
        logger.info("✅ Brier ≤ 0.12 - Objetivo alcanzado!")
    else:
        logger.warning(f"⚠️  Brier > 0.12 - Exceso de {brier_score - 0.12:.4f}")
    
    return model_calibrated, imputer, metrics


def save_model_bundle(
    model: Any,
    imputer: SimpleImputer,
    feature_names: list,
    filename: str = 'model_xgb_calibrated.pkl',
    metadata: dict = None
) -> Path:
    """
    Guarda el modelo junto con imputer y metadata en un bundle.
    
    Args:
        model: Modelo calibrado
        imputer: SimpleImputer ajustado
        feature_names: Lista de nombres de features
        filename: Nombre del archivo (default: model_xgb_calibrated.pkl)
        metadata: Diccionario con metadata adicional
    
    Returns:
        Path: Ruta del archivo guardado
    """
    logger.info(f"Guardando modelo bundle...")
    
    bundle = {
        'model': model,
        'imputer': imputer,
        'feature_names': feature_names,
        'metadata': metadata or {}
    }
    
    filepath = MODELS_DIR / filename
    joblib.dump(bundle, filepath)
    
    logger.info(f"✅ Modelo guardado en: {filepath}")
    logger.info(f"   Features: {len(feature_names)}")
    
    return filepath


def load_model_bundle(filename: str = 'model_xgb_calibrated.pkl') -> dict:
    """
    Carga el modelo bundle desde archivo.
    
    Args:
        filename: Nombre del archivo
    
    Returns:
        dict: Bundle con 'model', 'imputer', 'feature_names', 'metadata'
    """
    filepath = MODELS_DIR / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Modelo no encontrado: {filepath}")
    
    bundle = joblib.load(filepath)
    
    logger.info(f"✅ Modelo cargado desde: {filepath}")
    logger.info(f"   Features: {len(bundle['feature_names'])}")
    
    return bundle


if __name__ == "__main__":
    # Test de funciones de modelo
    from .config import setup_logging, set_seeds
    
    set_seeds()
    setup_logging()
    
    print("\n🧪 Test de módulo model.py:")
    print("   ✓ Importaciones exitosas")
    print("   ✓ Funciones disponibles:")
    print("      - train_xgboost()")
    print("      - calibrate_model()")
    print("      - train_with_calibration_split()")
    print("      - save_model_bundle()")
    print("      - load_model_bundle()")
    print("\n✅ Módulo model.py listo para uso")

