#!/usr/bin/env python
"""
Script principal de entrenamiento del modelo ML NHANES.

Este script implementa el pipeline completo:
1. Carga de datos con split temporal
2. Feature engineering avanzado
3. Entrenamiento con calibration split
4. Evaluación completa (métricas, fairness, SHAP)
5. Generación de reportes

Uso:
    python train_model.py [--data-path PATH] [--skip-shap]
"""
import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src import (
    # Config
    set_seeds, setup_logging, SEED,
    TRAIN_CYCLES, TEST_CYCLES,
    
    # Features
    build_feature_pipeline,
    
    # Model
    train_with_calibration_split,
    save_model_bundle,
    
    # Eval
    generate_reports
)


def load_nhanes_data(data_path: str = None) -> tuple:
    """
    Carga los datos NHANES con split temporal.
    
    Args:
        data_path: Ruta opcional a archivo CSV (si None, intenta cargar de múltiples fuentes)
    
    Returns:
        tuple: (train_df, test_df)
    """
    logger = setup_logging('training.log')
    logger.info("Cargando datos NHANES...")
    
    # Intentar cargar desde diferentes fuentes
    possible_paths = [
        data_path,
        'data/nhanes_processed.csv',
        'data/merged_nhanes.csv',
        '../data/nhanes_processed.csv'
    ]
    
    df = None
    for path in possible_paths:
        if path and Path(path).exists():
            logger.info(f"   Cargando desde: {path}")
            df = pd.read_csv(path)
            break
    
    if df is None:
        raise FileNotFoundError(
            "No se encontró archivo de datos NHANES.\n"
            "Por favor ejecuta el notebook GUIA_HACKATHON_SALUD_NHANES_3.ipynb "
            "para generar los datos procesados."
        )
    
    # Verificar que existe columna de cycle
    if 'cycle' not in df.columns:
        logger.warning("Columna 'cycle' no encontrada. Intentando derivar de SEQN...")
        # Lógica para derivar cycle si es posible
        # Por ahora, error
        raise ValueError("Se requiere columna 'cycle' para split temporal")
    
    # Split temporal
    train_df = df[df['cycle'].isin(TRAIN_CYCLES)].copy()
    test_df = df[df['cycle'].isin(TEST_CYCLES)].copy()
    
    logger.info(f"   ✓ Train: {len(train_df):,} samples (cycles {TRAIN_CYCLES})")
    logger.info(f"   ✓ Test:  {len(test_df):,} samples (cycles {TEST_CYCLES})")
    
    if len(train_df) == 0 or len(test_df) == 0:
        raise ValueError("Split temporal resultó en conjunto vacío. Verificar cycles.")
    
    return train_df, test_df


def prepare_features_and_target(df: pd.DataFrame, target_col: str = 'target') -> tuple:
    """
    Prepara features y target desde DataFrame raw.
    
    Args:
        df: DataFrame con datos raw
        target_col: Nombre de la columna target
    
    Returns:
        tuple: (X, y, feature_names)
    """
    logger = setup_logging()
    
    # Aplicar feature engineering
    df_features, feature_names = build_feature_pipeline(df, validate_leakage=True)
    
    # Separar features y target
    if target_col not in df_features.columns:
        raise ValueError(f"Columna target '{target_col}' no encontrada")
    
    X = df_features[feature_names]
    y = df_features[target_col]
    
    logger.info(f"   ✓ Features: {X.shape}")
    logger.info(f"   ✓ Target prevalence: {y.mean():.3f}")
    
    return X, y, feature_names


def main():
    """Función principal de entrenamiento."""
    
    parser = argparse.ArgumentParser(description='Entrenar modelo ML NHANES')
    parser.add_argument('--data-path', type=str, help='Ruta a archivo CSV de datos')
    parser.add_argument('--skip-shap', action='store_true', help='Saltar cálculo de SHAP (más rápido)')
    parser.add_argument('--model-name', type=str, default='xgb', help='Nombre del modelo')
    args = parser.parse_args()
    
    # Inicialización
    set_seeds(SEED)
    logger = setup_logging('training.log')
    
    logger.info("="*70)
    logger.info(" ENTRENAMIENTO MODELO ML - HACKATHON NHANES 2025 ")
    logger.info("="*70)
    logger.info(f"Seed: {SEED}")
    logger.info(f"Train cycles: {TRAIN_CYCLES}")
    logger.info(f"Test cycles: {TEST_CYCLES}")
    logger.info("="*70)
    
    try:
        # 1. Cargar datos
        logger.info("\n📂 PASO 1: Cargando datos...")
        train_df, test_df = load_nhanes_data(args.data_path)
        
        # 2. Feature engineering
        logger.info("\n🔧 PASO 2: Feature engineering...")
        X_train, y_train, feature_names = prepare_features_and_target(train_df)
        X_test, y_test, _ = prepare_features_and_target(test_df)
        
        logger.info(f"\n   Total features generadas: {len(feature_names)}")
        logger.info(f"   Top 10 features:")
        for i, feat in enumerate(feature_names[:10], 1):
            logger.info(f"      {i}. {feat}")
        
        # 3. Entrenamiento con calibration split
        logger.info("\n🚀 PASO 3: Entrenamiento con calibration split...")
        model_calibrated, imputer, metrics = train_with_calibration_split(
            X_train, y_train,
            X_test, y_test
        )
        
        # 4. Guardar modelo
        logger.info("\n💾 PASO 4: Guardando modelo...")
        metadata = {
            'train_cycles': TRAIN_CYCLES,
            'test_cycles': TEST_CYCLES,
            'n_features': len(feature_names),
            'seed': SEED,
            **metrics
        }
        
        save_model_bundle(
            model_calibrated,
            imputer,
            feature_names,
            filename=f'model_{args.model_name}_calibrated.pkl',
            metadata=metadata
        )
        
        # 5. Generar reportes
        logger.info("\n📊 PASO 5: Generando reportes...")
        # Aplicar imputación a X_test para generate_reports
        X_test_imp = imputer.transform(X_test)
        generate_reports(
            model_calibrated,
            X_test_imp,
            y_test,
            feature_names,
            metrics,
            model_name=args.model_name
        )
        
        # 6. Resumen final
        logger.info("\n" + "="*70)
        logger.info(" ENTRENAMIENTO COMPLETADO ")
        logger.info("="*70)
        logger.info(f"✅ AUROC:  {metrics['auroc']:.4f} {'(Objetivo ≥0.80)' if metrics['auroc'] >= 0.80 else '(⚠️  <0.80)'}")
        logger.info(f"✅ Brier:  {metrics['brier']:.4f} {'(Objetivo ≤0.12)' if metrics['brier'] <= 0.12 else '(⚠️  >0.12)'}")
        logger.info(f"✅ Método: {metrics['calibration_method']}")
        logger.info("="*70)
        
        # Verificar objetivos
        targets_met = []
        if metrics['auroc'] >= 0.80:
            targets_met.append("AUROC ≥ 0.80 (12 pts)")
        if metrics['brier'] <= 0.12:
            targets_met.append("Brier ≤ 0.12 (6 pts)")
        
        if targets_met:
            logger.info(f"\n🎯 Objetivos alcanzados:")
            for target in targets_met:
                logger.info(f"   ✅ {target}")
        
        points = 0
        if metrics['auroc'] >= 0.80:
            points += 12
        elif metrics['auroc'] >= 0.75:
            points += 10
        elif metrics['auroc'] >= 0.70:
            points += 7
        else:
            points += 4
        
        if metrics['brier'] <= 0.12:
            points += 6
        elif metrics['brier'] <= 0.15:
            points += 5
        elif metrics['brier'] <= 0.18:
            points += 3
        else:
            points += 1
        
        logger.info(f"\n📈 Puntos estimados (A1+A2): {points}/18")
        logger.info(f"   (A1 - AUROC: {'12' if metrics['auroc'] >= 0.80 else '10' if metrics['auroc'] >= 0.75 else '7' if metrics['auroc'] >= 0.70 else '4'}/12)")
        logger.info(f"   (A2 - Brier: {'6' if metrics['brier'] <= 0.12 else '5' if metrics['brier'] <= 0.15 else '3' if metrics['brier'] <= 0.18 else '1'}/6)")
        
        logger.info("\n📁 Archivos generados:")
        logger.info(f"   - models/model_{args.model_name}_calibrated.pkl")
        logger.info(f"   - reports/metrics_{args.model_name}.json")
        logger.info(f"   - reports/fairness_analysis.csv")
        logger.info(f"   - reports/shap_feature_importance.csv")
        logger.info(f"   - reports/shap_example_drivers.csv")
        logger.info(f"   - calibration_curves.png")
        logger.info(f"   - shap_summary.png")
        logger.info(f"   - roc_curve.png")
        
        logger.info("\n✅ Entrenamiento exitoso!")
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Error durante entrenamiento: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

