"""
Feature engineering para el modelo de riesgo cardiometabólico NHANES.
Implementa las features críticas basadas en análisis SHAP.
"""
import numpy as np
import pandas as pd
from typing import Tuple, List
import logging

from .config import get_lab_forbidden_columns

logger = logging.getLogger(__name__)


def create_base_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea features derivadas básicas (BMI, ratios, etc).
    
    Args:
        df: DataFrame con columnas base (weight_kg, height_cm, waist_cm)
    
    Returns:
        DataFrame con features base añadidas
    """
    df = df.copy()
    
    # BMI (Body Mass Index)
    if 'weight_kg' in df.columns and 'height_cm' in df.columns:
        df['bmi'] = df['weight_kg'] / (df['height_cm'] / 100) ** 2
    
    # Waist-to-Height Ratio (WHtR)
    if 'waist_cm' in df.columns and 'height_cm' in df.columns:
        df['waist_height_ratio'] = df['waist_cm'] / df['height_cm']
    
    # Convertir sexo a binario si es string
    if 'sex' in df.columns and df['sex'].dtype == 'object':
        df['sex_male'] = (df['sex'].str.upper() == 'M').astype(int)
    
    logger.debug(f"Features base creadas: {['bmi', 'waist_height_ratio', 'sex_male']}")
    
    return df


def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea features de interacción críticas basadas en SHAP importance.
    
    Top 5 interacciones según shap_feature_importance.csv:
    1. bmi_age_interaction (0.50)
    2. waist_height_ratio (0.31) - ya en base
    3. waist_age_interaction (0.30)
    4. bmi_age_sex_interaction (0.26)
    
    Args:
        df: DataFrame con features base
    
    Returns:
        DataFrame con features de interacción añadidas
    """
    df = df.copy()
    interactions = []
    
    # Interacciones multiplicativas críticas
    if 'bmi' in df.columns and 'age' in df.columns:
        df['bmi_age_interaction'] = df['bmi'] * df['age']
        interactions.append('bmi_age_interaction')
    
    if 'waist_cm' in df.columns and 'age' in df.columns:
        df['waist_age_interaction'] = df['waist_cm'] * df['age']
        interactions.append('waist_age_interaction')
    
    if all(col in df.columns for col in ['bmi', 'age', 'sex_male']):
        df['bmi_age_sex_interaction'] = df['bmi'] * df['age'] * df['sex_male']
        interactions.append('bmi_age_sex_interaction')
    
    # Features cuadráticas (potencian el efecto no-lineal)
    if 'waist_height_ratio' in df.columns:
        df['waist_height_ratio_squared'] = df['waist_height_ratio'] ** 2
        interactions.append('waist_height_ratio_squared')
    
    if 'age' in df.columns:
        df['age_squared'] = df['age'] ** 2
        interactions.append('age_squared')
    
    if 'bmi' in df.columns:
        df['bmi_squared'] = df['bmi'] ** 2
        interactions.append('bmi_squared')
    
    # Interacciones con estilo de vida
    if all(col in df.columns for col in ['age', 'sleep_hours']):
        # Poor sleep defined as < 7 or > 9 hours
        df['poor_sleep'] = ((df['sleep_hours'] < 7) | (df['sleep_hours'] > 9)).astype(int)
        df['age_poor_sleep'] = df['age'] * df['poor_sleep']
        interactions.extend(['poor_sleep', 'age_poor_sleep'])
    
    logger.debug(f"Features de interacción creadas: {interactions}")
    
    return df


def create_categorical_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea features categóricas de riesgo basadas en umbrales clínicos.
    
    Args:
        df: DataFrame con features base
    
    Returns:
        DataFrame con features categóricas añadidas
    """
    df = df.copy()
    risk_features = []
    
    # Central obesity (WHtR > 0.5 es indicador de riesgo)
    if 'waist_height_ratio' in df.columns:
        df['central_obesity'] = (df['waist_height_ratio'] > 0.5).astype(int)
        risk_features.append('central_obesity')
    
    # High waist-height ratio (> 0.6 es alto riesgo)
    if 'waist_height_ratio' in df.columns:
        df['high_waist_height_ratio'] = (df['waist_height_ratio'] > 0.6).astype(int)
        risk_features.append('high_waist_height_ratio')
    
    # Obesity (BMI > 30)
    if 'bmi' in df.columns:
        df['obesity'] = (df['bmi'] > 30).astype(int)
        risk_features.append('obesity')
    
    # High risk profile (obesity + edad > 45)
    if all(col in df.columns for col in ['bmi', 'age']):
        df['high_risk_profile'] = ((df['bmi'] > 30) & (df['age'] > 45)).astype(int)
        risk_features.append('high_risk_profile')
    
    # Lifestyle risk score (composite)
    lifestyle_cols = []
    if 'current_smoker' in df.columns:
        lifestyle_cols.append('current_smoker')
    if 'sedentary_flag' in df.columns:
        lifestyle_cols.append('sedentary_flag')
    if 'poor_sleep' in df.columns:
        lifestyle_cols.append('poor_sleep')
    
    if lifestyle_cols:
        df['lifestyle_risk_score'] = df[lifestyle_cols].sum(axis=1)
        risk_features.append('lifestyle_risk_score')
    
    # Triple risk (obesity + sedentary + smoker)
    triple_risk_cols = ['obesity', 'sedentary_flag', 'current_smoker']
    if all(col in df.columns for col in triple_risk_cols):
        df['triple_risk'] = (df[triple_risk_cols].sum(axis=1) >= 2).astype(int)
        risk_features.append('triple_risk')
    
    # Obesity + sedentary combo
    if all(col in df.columns for col in ['obesity', 'sedentary_flag']):
        df['obesity_sedentary_combo'] = (df['obesity'] & df['sedentary_flag']).astype(int)
        risk_features.append('obesity_sedentary_combo')
    
    logger.debug(f"Features categóricas de riesgo creadas: {risk_features}")
    
    return df


def validate_no_leakage(df: pd.DataFrame, feature_names: List[str]) -> bool:
    """
    Valida que no haya columnas de laboratorio (LAB_*) en las features.
    
    Args:
        df: DataFrame con features
        feature_names: Lista de nombres de features a usar
    
    Returns:
        bool: True si no hay fuga, False si se detecta fuga
    
    Raises:
        ValueError: Si se detecta fuga de datos
    """
    forbidden = get_lab_forbidden_columns()
    
    # Verificar que ninguna feature sea una columna prohibida
    leakage_features = [f for f in feature_names if f in forbidden]
    
    if leakage_features:
        error_msg = (
            f"❌ FUGA DE DATOS DETECTADA!\n"
            f"   Las siguientes features están prohibidas: {leakage_features}\n"
            f"   Estas son columnas de laboratorio que no pueden usarse para predicción."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Verificar también por prefijo LAB_
    lab_features = [f for f in feature_names if f.startswith('LAB_')]
    
    if lab_features:
        error_msg = (
            f"❌ FUGA DE DATOS DETECTADA!\n"
            f"   Features con prefijo LAB_: {lab_features}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"✅ Validación anti-fuga pasada: {len(feature_names)} features verificadas")
    return True


def build_feature_pipeline(df: pd.DataFrame, 
                          validate_leakage: bool = True) -> Tuple[pd.DataFrame, List[str]]:
    """
    Pipeline completo de feature engineering.
    
    Aplica en orden:
    1. Features base (BMI, WHtR, etc)
    2. Features de interacción (bmi_age, waist_age, etc)
    3. Features categóricas de riesgo
    4. Validación anti-fuga
    
    Args:
        df: DataFrame raw con columnas base
        validate_leakage: Si True, valida anti-fuga (default: True)
    
    Returns:
        Tuple[DataFrame, List[str]]: (DataFrame con features, lista de feature names)
    """
    logger.info("Iniciando pipeline de feature engineering...")
    
    # 1. Features base
    df = create_base_features(df)
    logger.info("   ✓ Features base creadas")
    
    # 2. Features de interacción (CRÍTICAS para AUROC >0.80)
    df = create_interaction_features(df)
    logger.info("   ✓ Features de interacción creadas")
    
    # 3. Features categóricas de riesgo
    df = create_categorical_risk_features(df)
    logger.info("   ✓ Features categóricas creadas")
    
    # Identificar features numéricas (excluir target, LAB_, y columnas raw)
    exclude_cols = {'target', 'label', 'cycle', 'SEQN', 'sex'}  # Agregar otras según necesidad
    feature_names = [col for col in df.columns 
                    if col not in exclude_cols 
                    and not col.startswith('LAB_')  # CRÍTICO: excluir columnas de laboratorio
                    and df[col].dtype in ['float64', 'int64', 'float32', 'int32']]
    
    # 4. Validación anti-fuga
    if validate_leakage:
        validate_no_leakage(df, feature_names)
        logger.info("   ✓ Validación anti-fuga pasada")
    
    logger.info(f"✅ Pipeline completado: {len(feature_names)} features generadas")
    
    return df, feature_names


def get_feature_groups() -> dict:
    """
    Retorna agrupación de features por categoría (útil para análisis).
    
    Returns:
        dict: Diccionario con grupos de features
    """
    return {
        'base': ['bmi', 'waist_height_ratio', 'age', 'sex_male'],
        'interactions': [
            'bmi_age_interaction',
            'waist_age_interaction', 
            'bmi_age_sex_interaction',
            'age_poor_sleep'
        ],
        'quadratic': [
            'bmi_squared',
            'age_squared',
            'waist_height_ratio_squared'
        ],
        'risk_categorical': [
            'central_obesity',
            'high_waist_height_ratio',
            'high_risk_profile',
            'lifestyle_risk_score',
            'triple_risk',
            'obesity_sedentary_combo'
        ],
        'lifestyle': [
            'current_smoker',
            'ever_smoker',
            'cigarettes_per_day',
            'total_active_days',
            'meets_activity_guidelines',
            'sedentary_flag',
            'sleep_hours',
            'poor_sleep'
        ]
    }


if __name__ == "__main__":
    # Test de funciones de features
    from .config import setup_logging, set_seeds
    
    set_seeds()
    setup_logging()
    
    # Crear datos de prueba
    test_data = pd.DataFrame({
        'age': [45, 50, 35],
        'sex': ['M', 'F', 'M'],
        'weight_kg': [85, 70, 95],
        'height_cm': [175, 165, 180],
        'waist_cm': [95, 80, 105],
        'sleep_hours': [6, 8, 5],
        'current_smoker': [1, 0, 1],
        'sedentary_flag': [1, 0, 1]
    })
    
    print("\n📊 Test de feature engineering:")
    print(f"   Datos originales: {test_data.shape}")
    
    df_features, feature_names = build_feature_pipeline(test_data)
    
    print(f"   Después de pipeline: {df_features.shape}")
    print(f"   Features generadas: {len(feature_names)}")
    print(f"\n   Top 10 features:")
    for feat in feature_names[:10]:
        print(f"      - {feat}")
    
    print("\n✅ Test de features completado")

