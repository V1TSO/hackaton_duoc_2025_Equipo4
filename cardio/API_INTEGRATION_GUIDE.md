# API Integration Guide - Cardio Model with SHAP

**Date:** November 7, 2025  
**Model:** Cardiovascular Hypertension Risk Predictor  
**Features:** SHAP Explainability, Calibrated Predictions, Fairness-Aware

---

## 📋 Overview

This guide shows how to integrate the improved cardiovascular model with SHAP explainability into the FastAPI backend and frontend.

---

## 🔧 Model Artifacts

### Required Files

```
cardio/models/
├── ensemble_logreg_rf_calibrado.pkl      # Calibrated model
├── shap_values_test.npy                  # SHAP values (optional)
├── shap_feature_importance.csv           # Feature rankings
├── fairness_report.json                  # Fairness metrics
└── [visualizations].png                  # Plots for documentation
```

### Feature Names (Must Match Training)

```python
CARDIO_FEATURES = [
    'edad', 'sexo', 'educacion', 'ratio_ingreso_pobreza',
    'imc', 'cintura_cm', 'rel_cintura_altura',
    'glucosa_mgdl', 'hdl_mgdl', 'trigliceridos_mgdl', 'ldl_mgdl',
    'imc_cuadratico', 'imc_x_edad', 'ratio_hdl_ldl', 'trigliceridos_log',
    'etnia_2.0', 'etnia_3.0', 'etnia_4.0', 'etnia_5.0'
]
```

---

## 🚀 Backend Integration

### Step 1: Update Model Loader

File: `back/app/ml/model_loader.py`

```python
import joblib
import shap
from pathlib import Path
from typing import Tuple, Optional

def load_cardio_model_bundle() -> Tuple[object, object, list]:
    """
    Load cardiovascular model with SHAP explainer.
    
    Returns:
        Tuple of (model, explainer, feature_names)
    """
    model_path = Path(__file__).parent / 'models' / 'cardio_ensemble_calibrado.pkl'
    
    # Load calibrated model
    model = joblib.load(model_path)
    
    # Extract base classifier for SHAP
    if hasattr(model, 'calibrated_classifiers_'):
        base_clf = model.calibrated_classifiers_[0].estimator
    else:
        base_clf = model.base_estimator
    
    # Handle pipeline structure
    if hasattr(base_clf, 'named_steps'):
        clf = base_clf.named_steps.get('clf', base_clf)
    else:
        clf = base_clf
    
    # Initialize SHAP explainer
    explainer = shap.TreeExplainer(clf)
    
    # Feature names
    feature_names = [
        'edad', 'sexo', 'educacion', 'ratio_ingreso_pobreza',
        'imc', 'cintura_cm', 'rel_cintura_altura',
        'glucosa_mgdl', 'hdl_mgdl', 'trigliceridos_mgdl', 'ldl_mgdl',
        'imc_cuadratico', 'imc_x_edad', 'ratio_hdl_ldl', 'trigliceridos_log',
        'etnia_2.0', 'etnia_3.0', 'etnia_4.0', 'etnia_5.0'
    ]
    
    return model, explainer, feature_names
```

### Step 2: Update Feature Engineering

File: `back/app/ml/feature_engineering.py`

Add cardio-specific feature descriptions:

```python
CARDIO_FEATURE_DESCRIPTIONS = {
    'edad': 'Edad',
    'sexo': 'Sexo',
    'educacion': 'Nivel educativo',
    'ratio_ingreso_pobreza': 'Relación ingreso-pobreza',
    'imc': 'IMC',
    'cintura_cm': 'Cintura (cm)',
    'rel_cintura_altura': 'Relación cintura/altura',
    'glucosa_mgdl': 'Glucosa (mg/dL)',
    'hdl_mgdl': 'Colesterol HDL (mg/dL)',
    'trigliceridos_mgdl': 'Triglicéridos (mg/dL)',
    'ldl_mgdl': 'Colesterol LDL (mg/dL)',
    'imc_cuadratico': 'IMC²',
    'imc_x_edad': 'IMC × Edad',
    'ratio_hdl_ldl': 'Ratio HDL/LDL',
    'trigliceridos_log': 'Log(Triglicéridos)',
    'etnia_2.0': 'Etnia grupo 2',
    'etnia_3.0': 'Etnia grupo 3',
    'etnia_4.0': 'Etnia grupo 4',
    'etnia_5.0': 'Etnia grupo 5'
}

def build_cardiovascular_features(user_data: dict) -> pd.DataFrame:
    """
    Build feature dataframe for cardiovascular model.
    
    Args:
        user_data: Dict with user inputs
        
    Returns:
        DataFrame with features in correct order
    """
    import numpy as np
    import pandas as pd
    
    # Extract base features
    edad = user_data.get('age', 50)
    sexo = 0 if user_data.get('sex', 'M') == 'M' else 1
    educacion = user_data.get('education_level', 3)  # Default to some college
    ratio_ingreso_pobreza = user_data.get('income_poverty_ratio', 2.0)
    
    # Calculate IMC if not provided
    if 'bmi' in user_data:
        imc = user_data['bmi']
    else:
        weight_kg = user_data.get('weight_kg', 75)
        height_m = user_data.get('height_cm', 170) / 100
        imc = weight_kg / (height_m ** 2)
    
    cintura_cm = user_data.get('waist_cm', 90)
    altura_cm = user_data.get('height_cm', 170)
    
    # Lab values
    glucosa_mgdl = user_data.get('glucose_mgdl', 100)
    hdl_mgdl = user_data.get('hdl_mgdl', 50)
    trigliceridos_mgdl = user_data.get('triglycerides_mgdl', 150)
    ldl_mgdl = user_data.get('ldl_mgdl', 100)
    
    # Derived features
    rel_cintura_altura = cintura_cm / altura_cm if altura_cm > 0 else 0.5
    imc_cuadratico = imc ** 2
    imc_x_edad = imc * edad
    ratio_hdl_ldl = hdl_mgdl / ldl_mgdl if ldl_mgdl > 0 else 1.0
    trigliceridos_log = np.log1p(trigliceridos_mgdl)
    
    # Ethnicity (one-hot encoded)
    etnia = user_data.get('ethnicity', 3)  # Default to group 3
    etnia_2 = 1.0 if etnia == 2 else 0.0
    etnia_3 = 1.0 if etnia == 3 else 0.0
    etnia_4 = 1.0 if etnia == 4 else 0.0
    etnia_5 = 1.0 if etnia == 5 else 0.0
    
    # Build dataframe
    features = pd.DataFrame([{
        'edad': edad,
        'sexo': sexo,
        'educacion': educacion,
        'ratio_ingreso_pobreza': ratio_ingreso_pobreza,
        'imc': imc,
        'cintura_cm': cintura_cm,
        'rel_cintura_altura': rel_cintura_altura,
        'glucosa_mgdl': glucosa_mgdl,
        'hdl_mgdl': hdl_mgdl,
        'trigliceridos_mgdl': trigliceridos_mgdl,
        'ldl_mgdl': ldl_mgdl,
        'imc_cuadratico': imc_cuadratico,
        'imc_x_edad': imc_x_edad,
        'ratio_hdl_ldl': ratio_hdl_ldl,
        'trigliceridos_log': trigliceridos_log,
        'etnia_2.0': etnia_2,
        'etnia_3.0': etnia_3,
        'etnia_4.0': etnia_4,
        'etnia_5.0': etnia_5
    }])
    
    return features
```

### Step 3: Update Predictor with SHAP

File: `back/app/ml/predictor.py`

```python
def predict_cardiovascular_risk(user_data: dict) -> dict:
    """
    Predict hypertension risk with SHAP explainability.
    
    Args:
        user_data: Dict with user inputs
        
    Returns:
        Dict with score, drivers, and metadata
    """
    import numpy as np
    
    # Load model bundle
    model, explainer, feature_names = load_cardio_model_bundle()
    
    # Build features
    X = build_cardiovascular_features(user_data)
    
    # Get prediction
    proba = model.predict_proba(X)[0, 1]
    
    # Calculate SHAP values
    # Note: Model includes preprocessing, so we need to extract transformed features
    if hasattr(model, 'calibrated_classifiers_'):
        base_model = model.calibrated_classifiers_[0].estimator
    else:
        base_model = model
    
    # Transform through preprocessing
    if hasattr(base_model, 'named_steps') and 'pre' in base_model.named_steps:
        X_transformed = base_model.named_steps['pre'].transform(X)
    else:
        X_transformed = X.values
    
    # Get SHAP values
    shap_values = explainer.shap_values(X_transformed)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # Positive class
    
    # Extract top drivers
    drivers = get_top_drivers(
        shap_values[0],
        feature_names,
        X.values[0],
        n=5
    )
    
    # Determine referral
    REFERRAL_THRESHOLD = 0.70
    needs_referral = proba >= REFERRAL_THRESHOLD
    
    return {
        "score": float(proba),
        "risk_level": "HIGH" if proba >= 0.70 else "MODERATE" if proba >= 0.40 else "LOW",
        "drivers": drivers,
        "needs_referral": needs_referral,
        "disclaimer": "This is not a medical diagnosis. Consult a healthcare professional.",
        "model_type": "cardiovascular_hypertension",
        "calibrated": True
    }


def get_top_drivers(shap_values_instance, feature_names, feature_values, n=5):
    """
    Extract top N features driving prediction.
    
    Args:
        shap_values_instance: SHAP values array for one prediction
        feature_names: List of feature names
        feature_values: Array of feature values
        n: Number of top drivers to return
    
    Returns:
        List of dicts with feature info
    """
    import numpy as np
    
    importance = np.abs(shap_values_instance)
    top_idx = np.argsort(importance)[-n:][::-1]
    
    drivers = []
    for idx in top_idx:
        feat_name = feature_names[idx]
        shap_val = float(shap_values_instance[idx])
        feat_val = float(feature_values[idx])
        
        # Impact direction
        impact = 'increases_risk' if shap_val > 0 else 'decreases_risk'
        
        # Human-readable description
        desc = CARDIO_FEATURE_DESCRIPTIONS.get(feat_name, feat_name)
        
        drivers.append({
            'feature': feat_name,
            'description': desc,
            'value': round(feat_val, 2),
            'shap_value': round(shap_val, 4),
            'impact': impact,
            'explanation': f"{desc} = {feat_val:.2f} → {'AUMENTA' if shap_val > 0 else 'DISMINUYE'} riesgo"
        })
    
    return drivers
```

### Step 4: Update API Route

File: `back/app/routes/ml_routes.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

router = APIRouter()

class CardioRiskRequest(BaseModel):
    age: int
    sex: str  # 'M' or 'F'
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    bmi: Optional[float] = None
    glucose_mgdl: Optional[float] = 100
    hdl_mgdl: Optional[float] = 50
    ldl_mgdl: Optional[float] = 100
    triglycerides_mgdl: Optional[float] = 150
    education_level: Optional[int] = 3
    income_poverty_ratio: Optional[float] = 2.0
    ethnicity: Optional[int] = 3


class CardioRiskResponse(BaseModel):
    score: float
    risk_level: str
    drivers: List[Dict]
    needs_referral: bool
    disclaimer: str
    model_type: str
    calibrated: bool


@router.post("/predict/cardio", response_model=CardioRiskResponse)
async def predict_cardio_risk(request: CardioRiskRequest):
    """
    Predict cardiovascular/hypertension risk with SHAP explainability.
    
    Returns:
        - score: Risk probability (0-1)
        - drivers: Top 5 features influencing prediction
        - needs_referral: Whether medical consultation is recommended
    """
    try:
        result = predict_cardiovascular_risk(request.dict())
        return CardioRiskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎨 Frontend Integration

### Display Drivers in UI

```typescript
// types/cardio.ts
export interface Driver {
  feature: string;
  description: string;
  value: number;
  shap_value: number;
  impact: 'increases_risk' | 'decreases_risk';
  explanation: string;
}

export interface CardioRiskResponse {
  score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH';
  drivers: Driver[];
  needs_referral: boolean;
  disclaimer: string;
  model_type: string;
  calibrated: boolean;
}

// components/DriversList.tsx
import { Driver } from '@/types/cardio';

export function DriversList({ drivers }: { drivers: Driver[] }) {
  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-lg">Factores Principales</h3>
      {drivers.map((driver, idx) => (
        <div
          key={idx}
          className={`p-3 rounded-lg border-l-4 ${
            driver.impact === 'increases_risk'
              ? 'border-red-500 bg-red-50'
              : 'border-green-500 bg-green-50'
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="font-medium">{driver.description}</p>
              <p className="text-sm text-gray-600">
                Valor: {driver.value.toFixed(2)}
              </p>
            </div>
            <div className="text-right">
              <span
                className={`text-2xl ${
                  driver.impact === 'increases_risk'
                    ? 'text-red-600'
                    : 'text-green-600'
                }`}
              >
                {driver.impact === 'increases_risk' ? '↑' : '↓'}
              </span>
              <p className="text-xs text-gray-500">
                SHAP: {Math.abs(driver.shap_value).toFixed(3)}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Usage in page
export default function CardioResultPage() {
  const [result, setResult] = useState<CardioRiskResponse | null>(null);

  return (
    <div className="max-w-4xl mx-auto p-6">
      {result && (
        <>
          <RiskScore score={result.score} level={result.risk_level} />
          <DriversList drivers={result.drivers} />
          {result.needs_referral && (
            <ReferralAlert />
          )}
          <Disclaimer text={result.disclaimer} />
        </>
      )}
    </div>
  );
}
```

---

## 🧪 Testing

### Test Endpoint

```bash
curl -X POST "http://localhost:8000/api/predict/cardio" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55,
    "sex": "M",
    "height_cm": 175,
    "weight_kg": 90,
    "waist_cm": 105,
    "glucose_mgdl": 110,
    "hdl_mgdl": 40,
    "ldl_mgdl": 150,
    "triglycerides_mgdl": 200
  }'
```

### Expected Response

```json
{
  "score": 0.68,
  "risk_level": "MODERATE",
  "drivers": [
    {
      "feature": "imc_x_edad",
      "description": "IMC × Edad",
      "value": 1608.16,
      "shap_value": 0.1234,
      "impact": "increases_risk",
      "explanation": "IMC × Edad = 1608.16 → AUMENTA riesgo"
    },
    {
      "feature": "cintura_cm",
      "description": "Cintura (cm)",
      "value": 105.0,
      "shap_value": 0.0987,
      "impact": "increases_risk",
      "explanation": "Cintura (cm) = 105.00 → AUMENTA riesgo"
    },
    {
      "feature": "hdl_mgdl",
      "description": "Colesterol HDL (mg/dL)",
      "value": 40.0,
      "shap_value": 0.0654,
      "impact": "increases_risk",
      "explanation": "Colesterol HDL (mg/dL) = 40.00 → AUMENTA riesgo"
    }
  ],
  "needs_referral": false,
  "disclaimer": "This is not a medical diagnosis. Consult a healthcare professional.",
  "model_type": "cardiovascular_hypertension",
  "calibrated": true
}
```

---

## 📊 Monitoring and Fairness

### Log Predictions for Fairness Monitoring

```python
# Add to predictor.py
def log_prediction_for_fairness(user_data: dict, result: dict):
    """
    Log prediction for periodic fairness analysis.
    """
    import json
    from datetime import datetime
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'age': user_data.get('age'),
        'sex': user_data.get('sex'),
        'ethnicity': user_data.get('ethnicity'),
        'score': result['score'],
        'risk_level': result['risk_level']
    }
    
    # Append to log file
    with open('logs/cardio_predictions.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

### Periodic Fairness Check

```python
# scripts/check_fairness.py
import pandas as pd
import json
from sklearn.metrics import roc_auc_score

def analyze_production_fairness(log_file='logs/cardio_predictions.jsonl'):
    """
    Analyze fairness of production predictions.
    """
    # Load predictions
    predictions = []
    with open(log_file) as f:
        for line in f:
            predictions.append(json.loads(line))
    
    df = pd.DataFrame(predictions)
    
    # Analyze by subgroups
    print("Fairness Analysis - Last 30 Days")
    print("=" * 50)
    
    for group_col in ['sex', 'ethnicity']:
        print(f"\n{group_col.upper()} Analysis:")
        for group_val in df[group_col].unique():
            mask = df[group_col] == group_val
            avg_score = df[mask]['score'].mean()
            high_risk_pct = (df[mask]['risk_level'] == 'HIGH').mean()
            print(f"  {group_val}: Avg Score={avg_score:.3f}, High Risk %={high_risk_pct:.1%}")
```

---

## ✅ Checklist

### Backend
- [ ] Copy model file to `back/app/ml/models/`
- [ ] Update `model_loader.py` with SHAP support
- [ ] Update `feature_engineering.py` with cardio features
- [ ] Update `predictor.py` with `get_top_drivers()`
- [ ] Add `/predict/cardio` route
- [ ] Test endpoint with curl
- [ ] Add fairness logging

### Frontend
- [ ] Create `Driver` interface
- [ ] Create `DriversList` component
- [ ] Update result page to display drivers
- [ ] Add risk level visualization
- [ ] Add referral alert for high risk
- [ ] Test end-to-end flow

### Documentation
- [ ] API documentation with examples
- [ ] Frontend component storybook
- [ ] Deployment guide
- [ ] Monitoring setup

---

## 🔗 Related Files

- `RESULTADOS_FINALES_MEJORADOS.md` - Performance metrics
- `COMPLIANCE_REVIEW_REPORT.md` - Full technical review
- `ACTION_CHECKLIST.md` - Implementation steps
- `GUIA_HACKATHON_SALUD_NHANES_3.ipynb` - Model training notebook

---

**Last Updated:** November 7, 2025  
**Status:** Ready for Integration  
**Contact:** See main README for team info

