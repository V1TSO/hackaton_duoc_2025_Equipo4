from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import joblib
import numpy as np
import pandas as pd
import shap
import os

# Importar sistema RAG
from rag_coach import RAGCoachSystem

app = FastAPI(
    title="Coach de Bienestar Preventivo",
    description="API para estimación de riesgo cardiometabólico y coaching personalizado",
    version="1.0.0"
)

model = joblib.load('model_xgboost.pkl')
imputer = joblib.load('imputer.pkl')
feature_names = joblib.load('feature_names.pkl')
feature_index_map = {name: idx for idx, name in enumerate(feature_names)}
try:
    with open('reports/top_drivers.json', 'r', encoding='utf-8') as f:
        TOP_DRIVERS = json.load(f).get('top_features', feature_names[:5])
except FileNotFoundError:
    TOP_DRIVERS = feature_names[:5]
TOP_DRIVERS = [feat for feat in TOP_DRIVERS if feat in feature_index_map]
explainer = shap.TreeExplainer(model)

# Inicializar sistema RAG
rag_system = RAGCoachSystem(
    kb_dir='./kb',
    api_key=os.getenv('OPENAI_API_KEY')
)

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
    'high_risk_profile': 'Edad ≥45 + IMC ≥30'
}

REFERRAL_THRESHOLD = 0.70


class UserProfile(BaseModel):
    age: int = Field(..., ge=18, le=85)
    sex: str = Field(..., pattern="^[MF]$")
    height_cm: float = Field(..., ge=120, le=220)
    weight_kg: float = Field(..., ge=30, le=220)
    waist_cm: float = Field(..., ge=40, le=170)
    sleep_hours: Optional[float] = Field(None, ge=3, le=14)
    smokes_cig_day: Optional[int] = Field(None, ge=0, le=60)
    days_mvpa_week: Optional[int] = Field(None, ge=0, le=7)
    fruit_veg_portions_day: Optional[float] = Field(None, ge=0, le=12)


class RiskResponse(BaseModel):
    score: float
    risk_level: str
    drivers: List[dict]
    recommendation: str


class CoachRequest(BaseModel):
    user_profile: UserProfile
    risk_score: float
    top_drivers: List[str]


class CoachResponse(BaseModel):
    plan: str
    sources: List[str]


def build_feature_frame(profile: UserProfile) -> pd.DataFrame:
    bmi = profile.weight_kg / ((profile.height_cm / 100) ** 2)
    waist_height_ratio = profile.waist_cm / profile.height_cm
    sleep_hours = profile.sleep_hours if profile.sleep_hours is not None else 7.5
    cigarettes = profile.smokes_cig_day if profile.smokes_cig_day is not None else 0
    total_active_days = profile.days_mvpa_week if profile.days_mvpa_week is not None else 0

    central_obesity = int(
        (profile.sex == 'M' and profile.waist_cm >= 102) or
        (profile.sex == 'F' and profile.waist_cm >= 88)
    )
    poor_sleep = int(sleep_hours < 7 or sleep_hours > 9)
    current_smoker = int(cigarettes > 0)
    sedentary_flag = int(total_active_days < 5)

    feature_values = {
        'age': profile.age,
        'age_squared': profile.age ** 2,
        'sex_male': 1 if profile.sex == 'M' else 0,
        'bmi': bmi,
        'waist_height_ratio': waist_height_ratio,
        'high_waist_height_ratio': int(waist_height_ratio >= 0.5),
        'central_obesity': central_obesity,
        'sleep_hours': sleep_hours,
        'poor_sleep': poor_sleep,
        'cigarettes_per_day': cigarettes,
        'current_smoker': current_smoker,
        'ever_smoker': current_smoker,
        'total_active_days': total_active_days,
        'meets_activity_guidelines': int(total_active_days >= 5),
        'sedentary_flag': sedentary_flag,
        'lifestyle_risk_score': poor_sleep + current_smoker + sedentary_flag,
        'bmi_age_interaction': bmi * profile.age,
        'waist_age_interaction': waist_height_ratio * profile.age,
        'high_risk_profile': int(bmi >= 30 and profile.age >= 45)
    }

    features_df = pd.DataFrame([feature_values])
    for feat in feature_names:
        if feat not in features_df.columns:
            features_df[feat] = 0
    return features_df[feature_names]


@app.get("/")
def read_root():
    return {
        "message": "Coach de Bienestar Preventivo API",
        "version": "1.0.0",
        "endpoints": ["/predict", "/coach", "/health"]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}


@app.post("/predict", response_model=RiskResponse)
def predict_risk(profile: UserProfile):
    try:
        X = build_feature_frame(profile)
        X_imp = imputer.transform(X)
        X_imp_df = pd.DataFrame(X_imp, columns=feature_names)

        risk_score = float(model.predict_proba(X_imp)[0, 1])

        if risk_score < 0.3:
            risk_level = "Bajo"
            recommendation = "Mantener hábitos saludables"
        elif risk_score < 0.6:
            risk_level = "Moderado"
            recommendation = "Mejorar estilo de vida con coaching personalizado"
        else:
            risk_level = "Alto"
            recommendation = "Consultar con profesional de salud urgentemente"
            if risk_score >= REFERRAL_THRESHOLD:
                recommendation += " y coordinar evaluación médica profesional"

        shap_values = explainer.shap_values(X_imp_df)
        if isinstance(shap_values, list):
            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        row_shap = shap_values[0]

        drivers = []
        for feature in TOP_DRIVERS:
            idx = feature_index_map.get(feature)
            if idx is None:
                continue
            shap_val = float(row_shap[idx])
            impact = 'aumenta' if shap_val > 0 else 'reduce'
            drivers.append({
                "feature": feature,
                "description": FEATURE_DESCRIPTIONS.get(feature, feature),
                "value": float(X_imp_df.iloc[0, idx]),
                "shap_value": shap_val,
                "impact": impact
            })

        return RiskResponse(
            score=risk_score,
            risk_level=risk_level,
            drivers=drivers,
            recommendation=recommendation
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/coach", response_model=CoachResponse)
def generate_coach_plan(request: CoachRequest):
    try:
        # Convertir UserProfile a dict
        profile_dict = {
            'age': request.user_profile.age,
            'sex': request.user_profile.sex,
            'height_cm': request.user_profile.height_cm,
            'weight_kg': request.user_profile.weight_kg,
            'waist_cm': request.user_profile.waist_cm,
            'sleep_hours': request.user_profile.sleep_hours,
            'smokes_cig_day': request.user_profile.smokes_cig_day,
            'days_mvpa_week': request.user_profile.days_mvpa_week,
            'fruit_veg_portions_day': request.user_profile.fruit_veg_portions_day
        }
        
        # Construir drivers como lista de dicts
        drivers_list = [{'description': d, 'feature': d} for d in request.top_drivers]
        
        # Generar plan usando RAG
        result = rag_system.generate_plan(
            user_profile=profile_dict,
            risk_score=request.risk_score,
            top_drivers=drivers_list
        )
        
        return CoachResponse(
            plan=result['plan'],
            sources=result['sources']
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
