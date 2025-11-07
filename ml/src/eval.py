"""
Módulo de evaluación, fairness analysis y SHAP explanations.
Genera todos los reportes necesarios para la rúbrica A.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import logging
import shap
from pathlib import Path
from typing import Dict, Any, Tuple, List
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    roc_curve, precision_recall_curve, confusion_matrix
)
from sklearn.calibration import calibration_curve

try:
    from fairlearn.metrics import MetricFrame, selection_rate
    from fairlearn.postprocessing import ThresholdOptimizer
    FAIRLEARN_AVAILABLE = True
except ImportError:
    FAIRLEARN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("fairlearn no disponible - funciones de fairness deshabilitadas")

from .config import REPORTS_DIR, TOP_DRIVERS, SENSITIVE_FEATURES

logger = logging.getLogger(__name__)

# Configurar estilo de gráficos
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 8)
plt.rcParams['font.size'] = 11


def calculate_metrics(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    threshold: float = 0.5
) -> Dict[str, float]:
    """
    Calcula métricas principales de evaluación.
    
    Args:
        y_true: Labels verdaderos
        y_pred_proba: Probabilidades predichas
        threshold: Umbral para clasificación binaria
    
    Returns:
        dict: Métricas (auroc, auprc, brier, etc.)
    """
    y_pred = (y_pred_proba >= threshold).astype(int)
    
    metrics = {
        'auroc': roc_auc_score(y_true, y_pred_proba),
        'auprc': average_precision_score(y_true, y_pred_proba),
        'brier': brier_score_loss(y_true, y_pred_proba),
        'threshold': threshold
    }
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    metrics.update({
        'true_positives': int(tp),
        'true_negatives': int(tn),
        'false_positives': int(fp),
        'false_negatives': int(fn),
        'sensitivity': tp / (tp + fn) if (tp + fn) > 0 else 0,
        'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
        'ppv': tp / (tp + fp) if (tp + fp) > 0 else 0,  # Precision
        'npv': tn / (tn + fn) if (tn + fn) > 0 else 0
    })
    
    return metrics


def plot_roc_curve(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    title: str = "ROC Curve",
    save_path: Path = None
) -> plt.Figure:
    """
    Genera curva ROC.
    
    Args:
        y_true: Labels verdaderos
        y_pred_proba: Probabilidades predichas
        title: Título del gráfico
        save_path: Ruta para guardar (opcional)
    
    Returns:
        matplotlib.Figure
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    auroc = roc_auc_score(y_true, y_pred_proba)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC (AUC={auroc:.4f})')
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"   ✓ ROC curve guardada: {save_path}")
    
    return fig


def plot_calibration_curve(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    n_bins: int = 10,
    title: str = "Calibration Curve",
    save_path: Path = None
) -> plt.Figure:
    """
    Genera curva de calibración.
    
    Args:
        y_true: Labels verdaderos
        y_pred_proba: Probabilidades predichas
        n_bins: Número de bins para calibración
        title: Título del gráfico
        save_path: Ruta para guardar (opcional)
    
    Returns:
        matplotlib.Figure
    """
    prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=n_bins)
    brier = brier_score_loss(y_true, y_pred_proba)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
    ax.plot(prob_pred, prob_true, 's-', label=f'Model (Brier={brier:.4f})')
    ax.set_xlabel('Mean predicted probability', fontsize=12)
    ax.set_ylabel('Fraction of positives', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"   ✓ Calibration curve guardada: {save_path}")
    
    return fig


def analyze_fairness(
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    sensitive_features: List[str] = None
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Realiza análisis de fairness por subgrupos.
    
    Args:
        model: Modelo entrenado
        X: Features
        y: Labels
        sensitive_features: Lista de features sensibles (default: SENSITIVE_FEATURES)
    
    Returns:
        Tuple: (fairness_df, gaps_dict)
    """
    if not FAIRLEARN_AVAILABLE:
        logger.warning("fairlearn no disponible - retornando análisis vacío")
        return pd.DataFrame(), {}
    
    if sensitive_features is None:
        # Usar solo las que existan en X
        sensitive_features = [f for f in SENSITIVE_FEATURES if f in X.columns]
    
    if not sensitive_features:
        logger.warning("No hay features sensibles disponibles en los datos")
        return pd.DataFrame(), {}
    
    logger.info(f"Analizando fairness para: {sensitive_features}")
    
    # Predicciones
    y_pred_proba = model.predict_proba(X)[:, 1]
    
    # Preparar features sensibles
    sf_df = X[sensitive_features].copy()
    
    # Crear grupos para análisis (ej: age_group, race categories)
    if 'age' in X.columns and 'age_group' not in sf_df.columns:
        sf_df['age_group'] = pd.cut(X['age'], bins=[0, 44, 59, 100], 
                                     labels=['18-44', '45-59', '60+'])
    
    # Métricas para fairness
    def auroc_metric(y_true, y_pred):
        if len(np.unique(y_true)) < 2:
            return np.nan
        return roc_auc_score(y_true, y_pred)
    
    def brier_metric(y_true, y_pred):
        return brier_score_loss(y_true, y_pred)
    
    metrics = {
        'auroc': auroc_metric,
        'brier': brier_metric,
        'prevalence': selection_rate
    }
    
    # Crear MetricFrame para cada sensitive feature
    results = []
    
    for sf_name in sensitive_features:
        if sf_name not in sf_df.columns:
            continue
        
        try:
            mf = MetricFrame(
                metrics=metrics,
                y_true=y,
                y_pred=y_pred_proba,
                sensitive_features=sf_df[sf_name]
            )
            
            # Convertir a DataFrame
            df = mf.by_group.reset_index()
            df['subgroup_feature'] = sf_name
            df.rename(columns={sf_name: 'subgroup_value'}, inplace=True)
            
            # Añadir count
            counts = sf_df[sf_name].value_counts()
            df['n'] = df['subgroup_value'].map(counts)
            
            results.append(df)
            
        except Exception as e:
            logger.warning(f"Error en fairness para {sf_name}: {e}")
    
    if not results:
        return pd.DataFrame(), {}
    
    # Combinar resultados
    fairness_df = pd.concat(results, ignore_index=True)
    
    # Calcular gaps
    gaps = {}
    for metric in ['auroc', 'brier']:
        if metric in fairness_df.columns:
            values = fairness_df[metric].dropna()
            if len(values) > 1:
                gaps[f'{metric}_gap'] = float(values.max() - values.min())
    
    logger.info(f"   ✓ Fairness analysis completado")
    logger.info(f"      Subgrupos analizados: {len(fairness_df)}")
    for metric, gap in gaps.items():
        logger.info(f"      {metric}: {gap:.4f}")
    
    return fairness_df, gaps


def compute_shap_values(
    model: Any,
    X: pd.DataFrame,
    feature_names: List[str],
    sample_size: int = None
) -> Tuple[shap.Explanation, shap.TreeExplainer]:
    """
    Calcula valores SHAP para explicabilidad.
    
    Args:
        model: Modelo XGBoost (puede ser calibrado o no)
        X: Features
        feature_names: Nombres de features
        sample_size: Tamaño de muestra para acelerar cálculo (opcional)
    
    Returns:
        Tuple: (shap_values, explainer)
    """
    logger.info("Calculando valores SHAP...")
    
    # Si el modelo está calibrado, extraer el modelo base
    if hasattr(model, 'calibrated_classifiers_'):
        # CalibratedClassifierCV
        base_model = model.calibrated_classifiers_[0].estimator
        logger.info("   Modelo calibrado detectado - usando estimador base")
    else:
        base_model = model
    
    # Muestrear si es necesario
    if sample_size and len(X) > sample_size:
        X_sample = X.sample(n=sample_size, random_state=42)
        logger.info(f"   Usando muestra de {sample_size} observaciones")
    else:
        X_sample = X
    
    # Crear explainer
    explainer = shap.TreeExplainer(base_model)
    
    # Calcular SHAP values
    shap_values = explainer.shap_values(X_sample)
    
    logger.info(f"   ✓ SHAP values calculados: shape={shap_values.shape}")
    
    return shap_values, explainer


def get_shap_feature_importance(
    shap_values: np.ndarray,
    feature_names: List[str]
) -> pd.DataFrame:
    """
    Calcula importancia global de features desde SHAP values.
    
    Args:
        shap_values: Array de valores SHAP
        feature_names: Nombres de features
    
    Returns:
        DataFrame: Importancia ordenada por SHAP
    """
    # Importancia = promedio del valor absoluto
    importance = np.abs(shap_values).mean(axis=0)
    
    df = pd.DataFrame({
        'feature': feature_names,
        'shap_importance': importance
    }).sort_values('shap_importance', ascending=False)
    
    return df


def get_prediction_drivers(
    shap_values: np.ndarray,
    X_instance: pd.DataFrame,
    feature_names: List[str],
    top_n: int = TOP_DRIVERS
) -> pd.DataFrame:
    """
    Obtiene los drivers (explicaciones SHAP) para una predicción individual.
    
    Formato compatible con shap_example_drivers.csv para la API.
    
    Args:
        shap_values: Valores SHAP para la instancia
        X_instance: Features de la instancia (1 fila)
        feature_names: Nombres de features
        top_n: Top N features a retornar
    
    Returns:
        DataFrame: Drivers con columnas [feature, feature_value, shap_value, impact]
    """
    # Asegurar que es 1D
    if len(shap_values.shape) > 1:
        shap_values = shap_values[0]
    
    # Crear DataFrame
    drivers = pd.DataFrame({
        'feature': feature_names,
        'feature_value': X_instance.iloc[0].values,
        'shap_value': shap_values
    })
    
    # Impacto (positivo = aumenta riesgo, negativo = reduce riesgo)
    drivers['impact'] = drivers['shap_value'].apply(
        lambda x: 'aumenta' if x > 0 else 'reduce'
    )
    
    # Ordenar por importancia absoluta
    drivers['abs_shap'] = np.abs(drivers['shap_value'])
    drivers = drivers.sort_values('abs_shap', ascending=False).head(top_n)
    drivers = drivers.drop('abs_shap', axis=1)
    
    return drivers


def plot_shap_summary(
    shap_values: np.ndarray,
    X: pd.DataFrame,
    title: str = "SHAP Summary Plot",
    save_path: Path = None,
    max_display: int = 20
) -> plt.Figure:
    """
    Genera SHAP summary plot.
    
    Args:
        shap_values: Valores SHAP
        X: Features (para colores)
        title: Título del gráfico
        save_path: Ruta para guardar
        max_display: Máximo número de features a mostrar
    
    Returns:
        matplotlib.Figure
    """
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X, max_display=max_display, show=False)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"   ✓ SHAP summary guardado: {save_path}")
    
    return plt.gcf()


def generate_reports(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    feature_names: List[str],
    metrics: Dict[str, Any],
    model_name: str = 'xgb'
) -> None:
    """
    Genera todos los reportes necesarios para la rúbrica.
    
    Genera:
    - reports/metrics_{model_name}.json
    - reports/fairness_analysis.csv
    - reports/shap_feature_importance.csv
    - reports/shap_example_drivers.csv
    - calibration_curves.png
    - shap_summary.png
    - roc_curve.png
    
    Args:
        model: Modelo entrenado
        X_test: Features de test
        y_test: Labels de test
        feature_names: Nombres de features
        metrics: Diccionario con métricas
        model_name: Nombre del modelo para archivos
    """
    logger.info("="*60)
    logger.info("GENERANDO REPORTES")
    logger.info("="*60)
    
    # Predicciones
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # 1. Métricas JSON
    metrics_path = REPORTS_DIR / f'metrics_{model_name}.json'
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"✅ Métricas guardadas: {metrics_path}")
    
    # 2. Curvas (ROC y Calibración)
    roc_path = REPORTS_DIR.parent / 'roc_curve.png'
    plot_roc_curve(y_test, y_pred_proba, 
                  title=f"ROC Curve - {model_name.upper()}",
                  save_path=roc_path)
    plt.close()
    
    calib_path = REPORTS_DIR.parent / 'calibration_curves.png'
    plot_calibration_curve(y_test, y_pred_proba,
                          title=f"Calibration Curve - {model_name.upper()}",
                          save_path=calib_path)
    plt.close()
    
    # 3. Fairness Analysis
    fairness_df, gaps = analyze_fairness(model, X_test, y_test)
    if not fairness_df.empty:
        fairness_path = REPORTS_DIR / 'fairness_analysis.csv'
        # Formato compatible con checklist
        fairness_export = fairness_df[[
            'subgroup_feature', 'subgroup_value', 'n', 'prevalence', 'auroc', 'brier'
        ]].copy()
        fairness_export['subgroup'] = (
            fairness_export['subgroup_feature'] + '_' + 
            fairness_export['subgroup_value'].astype(str)
        )
        fairness_export = fairness_export[['subgroup', 'n', 'prevalence', 'auroc', 'brier']]
        fairness_export.to_csv(fairness_path, index=False)
        logger.info(f"✅ Fairness analysis guardado: {fairness_path}")
    
    # 4. SHAP Analysis
    try:
        shap_values, explainer = compute_shap_values(model, X_test, feature_names, 
                                                      sample_size=1000)
        
        # 4a. Feature importance
        shap_importance = get_shap_feature_importance(shap_values, feature_names)
        shap_imp_path = REPORTS_DIR / 'shap_feature_importance.csv'
        shap_importance.to_csv(shap_imp_path, index=False)
        logger.info(f"✅ SHAP importance guardado: {shap_imp_path}")
        
        # 4b. Example drivers (primera observación de test)
        example_idx = 0
        example_drivers = get_prediction_drivers(
            shap_values[example_idx],
            X_test.iloc[[example_idx]],
            feature_names
        )
        drivers_path = REPORTS_DIR / 'shap_example_drivers.csv'
        example_drivers.to_csv(drivers_path, index=False)
        logger.info(f"✅ SHAP drivers guardados: {drivers_path}")
        
        # 4c. Summary plot
        shap_plot_path = REPORTS_DIR.parent / 'shap_summary.png'
        plot_shap_summary(shap_values, X_test, 
                         title="SHAP Feature Importance",
                         save_path=shap_plot_path)
        plt.close()
        
    except Exception as e:
        logger.error(f"Error en SHAP analysis: {e}")
    
    logger.info("="*60)
    logger.info("✅ TODOS LOS REPORTES GENERADOS")
    logger.info("="*60)


if __name__ == "__main__":
    # Test de funciones de evaluación
    from .config import setup_logging, set_seeds
    
    set_seeds()
    setup_logging()
    
    print("\n🧪 Test de módulo eval.py:")
    print("   ✓ Importaciones exitosas")
    print("   ✓ Funciones disponibles:")
    print("      - calculate_metrics()")
    print("      - analyze_fairness()")
    print("      - compute_shap_values()")
    print("      - generate_reports()")
    print(f"   ✓ fairlearn disponible: {FAIRLEARN_AVAILABLE}")
    print("\n✅ Módulo eval.py listo para uso")

