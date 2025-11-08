import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


FEATURE_DESCRIPTIONS = {
    'age': 'Edad',
    'age_squared': 'Edad al cuadrado',
    'sex_male': 'Sexo masculino',
    'bmi': 'Índice de Masa Corporal',
    'waist_height_ratio': 'Proporción cintura-altura',
    'high_waist_height_ratio': 'Relación cintura-altura elevada',
    'central_obesity': 'Obesidad abdominal',
    'sleep_hours': 'Horas de sueño',
    'poor_sleep': 'Sueño insuficiente/excesivo',
    'cigarettes_per_day': 'Cigarrillos por día',
    'current_smoker': 'Fumador activo',
    'ever_smoker': 'Historial de tabaquismo',
    'total_active_days': 'Días activos por semana',
    'meets_activity_guidelines': 'Cumple actividad física recomendada',
    'sedentary_flag': 'Indicador de sedentarismo',
    'lifestyle_risk_score': 'Puntaje de riesgo de estilo de vida',
    'bmi_age_interaction': 'Interacción IMC * edad',
    'waist_age_interaction': 'Interacción cintura-altura * edad',
    'high_risk_profile': 'Edad ≥45 + IMC ≥30',
    'edad': 'Edad',
    'sexo': 'Sexo (0=Masculino, 1=Femenino)',
    'educacion': 'Nivel educativo',
    'ratio_ingreso_pobreza': 'Relación ingreso-pobreza',
    'cintura_cm': 'Circunferencia de cintura (cm)',
    'glucosa_mgdl': 'Glucosa (mg/dL)',
    'hdl_mgdl': 'Colesterol HDL (mg/dL)',
    'trigliceridos_mgdl': 'Triglicéridos (mg/dL)',
    'ldl_mgdl': 'Colesterol LDL (mg/dL)',
    'imc_cuadratico': 'IMC al cuadrado',
    'imc_x_edad': 'Interacción IMC x Edad',
    'ratio_hdl_ldl': 'Relación HDL / LDL',
    'trigliceridos_log': 'Logaritmo de triglicéridos',
    'rel_cintura_altura': 'Relación cintura / altura',
    'etnia_2.0': 'Etnia (categoría 2)',
    'etnia_3.0': 'Etnia (categoría 3)',
    'etnia_4.0': 'Etnia (categoría 4)',
    'etnia_5.0': 'Etnia (categoría 5)'
}

CARDIO_FEATURE_COLUMNS = [
    'edad',
    'sexo',
    'educacion',
    'ratio_ingreso_pobreza',
    'imc',
    'cintura_cm',
    'rel_cintura_altura',
    'glucosa_mgdl',
    'hdl_mgdl',
    'trigliceridos_mgdl',
    'ldl_mgdl',
    'imc_cuadratico',
    'imc_x_edad',
    'ratio_hdl_ldl',
    'trigliceridos_log',
    'etnia_2.0',
    'etnia_3.0',
    'etnia_4.0',
    'etnia_5.0'
]

def build_feature_frame(
    age: int,
    sex: str,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    waist_cm: Optional[float] = None,
    sleep_hours: Optional[float] = None,
    smokes_cig_day: Optional[float] = None,
    days_mvpa_week: Optional[int] = None,
    bmi: Optional[float] = None,
    systolic_bp: Optional[float] = None,
    total_cholesterol: Optional[float] = None,
    feature_names: list = None
) -> pd.DataFrame:
    """
    Build feature frame from user profile data.
    Based on ml/api_main.py logic.
    
    Args:
        age: User age
        sex: User sex ('M' or 'F')
        height_cm: Height in cm (optional if bmi provided)
        weight_kg: Weight in kg (optional if bmi provided)
        waist_cm: Waist circumference in cm
        sleep_hours: Hours of sleep per night
        smokes_cig_day: Cigarettes per day
        days_mvpa_week: Days of moderate-vigorous physical activity per week
        bmi: Pre-calculated BMI (if not provided, calculated from height/weight)
        feature_names: List of expected feature names for ordering
    
    Returns:
        DataFrame with engineered features
    """
    if bmi is None:
        if height_cm is None or weight_kg is None:
            raise ValueError("Either bmi or both height_cm and weight_kg must be provided")
        bmi = weight_kg / ((height_cm / 100) ** 2)

    sex_code = (sex or "").upper()
    sex_male = 1 if sex_code == 'M' else 0

    waist_cm = float(waist_cm) if waist_cm is not None else None
    height_cm = float(height_cm) if height_cm is not None else None

    if waist_cm is not None and height_cm is not None and height_cm > 0:
        waist_height_ratio = waist_cm / height_cm
    else:
        waist_height_ratio = np.nan

    sleep_hours = float(sleep_hours) if sleep_hours is not None else np.nan

    cigarettes = float(smokes_cig_day) if smokes_cig_day is not None else np.nan
    if np.isnan(cigarettes):
        cigarettes = 0.0

    current_smoker = float(1.0 if cigarettes > 0 else 0.0)
    ever_smoker = current_smoker

    total_active_days = float(days_mvpa_week) if days_mvpa_week is not None else np.nan
    meets_activity_guidelines = np.nan
    sedentary_flag = np.nan
    if not np.isnan(total_active_days):
        meets_activity_guidelines = float(1.0 if total_active_days >= 5 else 0.0)
        sedentary_flag = float(1.0 if total_active_days < 5 else 0.0)

    poor_sleep = np.nan
    if not np.isnan(sleep_hours):
        poor_sleep = float(1.0 if (sleep_hours < 7 or sleep_hours > 9) else 0.0)

    central_obesity = np.nan
    high_waist_height_ratio = np.nan
    if not np.isnan(waist_height_ratio):
        central_obesity = float(1.0 if waist_height_ratio > 0.5 else 0.0)
        high_waist_height_ratio = float(1.0 if waist_height_ratio > 0.6 else 0.0)
    elif waist_cm is not None:
        threshold = 102 if sex_code == 'M' else 88
        central_obesity = float(1.0 if waist_cm >= threshold else 0.0)
        high_waist_height_ratio = central_obesity

    obesity_flag = np.nan
    if bmi is not None:
        obesity_flag = float(1.0 if bmi >= 30 else 0.0)

    bp_flag = np.nan
    if systolic_bp is not None:
        bp_flag = float(1.0 if systolic_bp >= 130 else 0.0)

    chol_flag = np.nan
    if total_cholesterol is not None:
        chol_flag = float(1.0 if total_cholesterol >= 240 else 0.0)

    lifestyle_components = [
        comp for comp in [poor_sleep, current_smoker, sedentary_flag, bp_flag, chol_flag]
        if not np.isnan(comp)
    ]
    lifestyle_risk_score = np.nan
    if lifestyle_components:
        lifestyle_risk_score = float(min(3.0, np.sum(lifestyle_components)))

    waist_age_interaction = np.nan
    if waist_cm is not None:
        waist_age_interaction = float(waist_cm * age)

    bmi_age_interaction = float(bmi * age) if bmi is not None else np.nan
    bmi_age_sex_interaction = float(bmi * age * sex_male) if bmi is not None else np.nan

    age_poor_sleep = np.nan
    if not np.isnan(poor_sleep):
        age_poor_sleep = float(age * poor_sleep)

    obesity_sedentary_combo = np.nan
    triple_risk = np.nan
    if not np.isnan(obesity_flag) and not np.isnan(sedentary_flag):
        obesity_sedentary_combo = float(1.0 if (obesity_flag == 1.0 and sedentary_flag == 1.0) else 0.0)
        triple_sum = obesity_flag + sedentary_flag + current_smoker
        triple_risk = float(1.0 if triple_sum >= 2 else 0.0)

    feature_values = {
        'age': float(age),
        'age_squared': float(age ** 2),
        'sex_male': float(sex_male),
        'bmi': float(bmi),
        'bmi_squared': float(bmi ** 2) if bmi is not None else np.nan,
        'waist_height_ratio': waist_height_ratio,
        'waist_height_ratio_squared': waist_height_ratio ** 2 if not np.isnan(waist_height_ratio) else np.nan,
        'high_waist_height_ratio': high_waist_height_ratio,
        'central_obesity': central_obesity,
        'high_risk_profile': float(1.0 if bmi is not None and bmi >= 30 and age >= 45 else 0.0) if bmi is not None else np.nan,
        'sleep_hours': sleep_hours,
        'poor_sleep': poor_sleep,
        'cigarettes_per_day': cigarettes,
        'current_smoker': current_smoker,
        'ever_smoker': ever_smoker,
        'total_active_days': total_active_days,
        'meets_activity_guidelines': meets_activity_guidelines,
        'sedentary_flag': sedentary_flag,
        'lifestyle_risk_score': lifestyle_risk_score,
        'bmi_age_interaction': bmi_age_interaction,
        'waist_age_interaction': waist_age_interaction,
        'bmi_age_sex_interaction': bmi_age_sex_interaction,
        'obesity_sedentary_combo': obesity_sedentary_combo,
        'age_poor_sleep': age_poor_sleep,
        'triple_risk': triple_risk
    }

    features_df = pd.DataFrame([feature_values])

    missing_values = pd.Series(feature_values).isna()
    if missing_values.any():
        logger.info(
            "Imputing missing engineered features: %s",
            missing_values[missing_values].index.tolist()
        )

    logger.debug(
        "Engineered features summary | bmi=%.2f, lifestyle_score=%s, waist_ratio=%s, bp_flag=%s, chol_flag=%s",
        feature_values['bmi'],
        lifestyle_risk_score,
        waist_height_ratio,
        bp_flag,
        chol_flag
    )
    
    if feature_names:
        # Efficiently add missing features using reindex (avoids DataFrame fragmentation)
        features_df = features_df.reindex(columns=feature_names, fill_value=0)
    
    return features_df

def get_feature_description(feature_name: str) -> str:
    """Get Spanish description for a feature name."""
    return FEATURE_DESCRIPTIONS.get(feature_name, feature_name)


def build_cardiovascular_feature_frame(
    edad: int,
    genero: Optional[str],
    imc: Optional[float] = None,
    altura_cm: Optional[float] = None,
    peso_kg: Optional[float] = None,
    circunferencia_cintura: Optional[float] = None,
    glucosa_mgdl: Optional[float] = None,
    hdl_mgdl: Optional[float] = None,
    trigliceridos_mgdl: Optional[float] = None,
    ldl_mgdl: Optional[float] = None,
    feature_names: Optional[List[str]] = None
) -> pd.DataFrame:
    """Build the feature frame expected by the cardiovascular pipeline."""

    sexo_value: float = np.nan
    if genero:
        genero_upper = genero.upper()
        if genero_upper == 'M':
            sexo_value = 0.0
        elif genero_upper == 'F':
            sexo_value = 1.0

    bmi_value = imc
    if bmi_value is None and altura_cm and peso_kg and altura_cm > 0:
        bmi_value = peso_kg / ((altura_cm / 100) ** 2)

    rel_cintura_altura = np.nan
    if circunferencia_cintura is not None and altura_cm:
        try:
            rel_cintura_altura = float(circunferencia_cintura) / float(altura_cm)
        except ZeroDivisionError:
            rel_cintura_altura = np.nan

    imc_cuadratico = float(bmi_value ** 2) if bmi_value is not None else np.nan
    imc_x_edad = float(bmi_value * edad) if bmi_value is not None else np.nan

    ratio_hdl_ldl = np.nan
    if hdl_mgdl not in (None, 0) and ldl_mgdl not in (None, 0):
        try:
            ratio_hdl_ldl = float(hdl_mgdl) / float(ldl_mgdl)
        except ZeroDivisionError:
            ratio_hdl_ldl = np.nan

    trigliceridos_log = np.nan
    if trigliceridos_mgdl is not None:
        try:
            trigliceridos_log = float(np.log1p(trigliceridos_mgdl))
        except Exception:
            trigliceridos_log = np.nan

    # Log valores críticos antes de construir features
    logger.info(f"🔍 Construyendo features cardiovasculares:")
    logger.info(f"   edad={edad}, sexo={genero}, imc={bmi_value}")
    logger.info(f"   cintura={circunferencia_cintura}, rel_cintura_altura={rel_cintura_altura}")
    logger.info(f"   glucosa={glucosa_mgdl}, hdl={hdl_mgdl}, ldl={ldl_mgdl}, trig={trigliceridos_mgdl}")
    logger.info(f"   Valores faltantes: hdl={hdl_mgdl is None}, ldl={ldl_mgdl is None}, trig={trigliceridos_mgdl is None}")
    
    cardio_values: Dict[str, Any] = {
        'edad': float(edad),
        'sexo': sexo_value,
        'educacion': np.nan,
        'ratio_ingreso_pobreza': np.nan,
        'imc': float(bmi_value) if bmi_value is not None else np.nan,
        'cintura_cm': float(circunferencia_cintura) if circunferencia_cintura is not None else np.nan,
        'rel_cintura_altura': rel_cintura_altura,
        'glucosa_mgdl': float(glucosa_mgdl) if glucosa_mgdl is not None else np.nan,
        'hdl_mgdl': float(hdl_mgdl) if hdl_mgdl is not None else np.nan,
        'trigliceridos_mgdl': float(trigliceridos_mgdl) if trigliceridos_mgdl is not None else np.nan,
        'ldl_mgdl': float(ldl_mgdl) if ldl_mgdl is not None else np.nan,
        'imc_cuadratico': imc_cuadratico,
        'imc_x_edad': imc_x_edad,
        'ratio_hdl_ldl': ratio_hdl_ldl,
        'trigliceridos_log': trigliceridos_log,
        'etnia_2.0': 0.0,
        'etnia_3.0': 0.0,
        'etnia_4.0': 0.0,
        'etnia_5.0': 0.0
    }
    
    # Validar valores extremos que podrían indicar errores de entrada
    if bmi_value is not None and bmi_value > 60:
        logger.warning(f"⚠️ IMC extremadamente alto detectado: {bmi_value:.2f}. Verificar si los datos son correctos.")
    if rel_cintura_altura is not None and not np.isnan(rel_cintura_altura) and rel_cintura_altura > 1.0:
        logger.warning(f"⚠️ Relación cintura-altura extremadamente alta: {rel_cintura_altura:.2f}. Verificar si los datos son correctos.")

    features_df = pd.DataFrame([cardio_values])

    if feature_names:
        for feat in feature_names:
            if feat not in features_df.columns:
                features_df[feat] = np.nan
        features_df = features_df[feature_names]
    else:
        missing = [col for col in CARDIO_FEATURE_COLUMNS if col not in features_df.columns]
        for col in missing:
            features_df[col] = np.nan
        features_df = features_df[CARDIO_FEATURE_COLUMNS]

    return features_df

