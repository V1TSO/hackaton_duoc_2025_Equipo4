# Multi-Model Architecture: Diabetes + Cardiovascular

## Current State

Currently, the backend has ONE model integrated:
- **Diabetes/Cardiometabolic Risk Model** (`model_xgb_calibrated.pkl`)

## Proposed Architecture for Two Models

### Option 1: Separate Endpoints (Recommended)

```
POST /api/health/predict/diabetes
POST /api/health/predict/cardiovascular
POST /api/health/coach/diabetes
POST /api/health/coach/cardiovascular
```

**Pros**: Clear separation, easy to maintain, explicit routing
**Cons**: More endpoints to document

### Option 2: Model Selection Parameter

```
POST /api/health/predict?model_type=diabetes
POST /api/health/predict?model_type=cardiovascular
```

**Pros**: Fewer endpoints, unified interface
**Cons**: More complex validation, single point of failure

### Option 3: Auto-Detection Based on Input

The backend automatically selects the model based on available input features.

**Pros**: Smart, user-friendly
**Cons**: Complex logic, potential ambiguity

## Recommended Implementation (Option 1)

### Step 1: Prepare Cardiovascular Model

1. **Train/Export the cardiovascular model** (if not already done)
2. **Copy model files**:
   ```bash
   cp path/to/cardiovascular_model.pkl back/app/ml/models/model_cardiovascular.pkl
   cp path/to/cardiovascular_imputer.pkl back/app/ml/models/imputer_cardiovascular.pkl
   cp path/to/cardiovascular_features.pkl back/app/ml/models/feature_names_cardiovascular.pkl
   ```

### Step 2: Update Model Loader

Add to `back/app/ml/model_loader.py`:

```python
_model_diabetes = None
_imputer_diabetes = None
_feature_names_diabetes = None

_model_cardiovascular = None
_imputer_cardiovascular = None
_feature_names_cardiovascular = None

def load_model_bundle(model_type: str = "diabetes") -> Tuple[Any, SimpleImputer, List[str]]:
    """
    Load the model bundle for specified model type.
    
    Args:
        model_type: Either "diabetes" or "cardiovascular"
    """
    global _model_diabetes, _imputer_diabetes, _feature_names_diabetes
    global _model_cardiovascular, _imputer_cardiovascular, _feature_names_cardiovascular
    
    if model_type == "diabetes":
        if _model_diabetes is not None:
            return _model_diabetes, _imputer_diabetes, _feature_names_diabetes
        
        model_path = models_dir / "model_xgb_calibrated.pkl"
        # ... load diabetes model
        
    elif model_type == "cardiovascular":
        if _model_cardiovascular is not None:
            return _model_cardiovascular, _imputer_cardiovascular, _feature_names_cardiovascular
        
        model_path = models_dir / "model_cardiovascular.pkl"
        # ... load cardiovascular model
        
    else:
        raise ValueError(f"Unknown model_type: {model_type}")
```

### Step 3: Update Predictor

Add to `back/app/ml/predictor.py`:

```python
def predict_risk(
    model_type: str = "diabetes",
    age: int,
    sex: str,
    # ... other params
) -> Dict[str, Any]:
    """
    Predict risk using specified model.
    
    Args:
        model_type: "diabetes" or "cardiovascular"
        ...
    """
    model, imputer, feature_names = load_model_bundle(model_type)
    # ... rest of prediction logic
```

### Step 4: Create New Routes

Add to `back/app/routes/ml_routes.py`:

```python
@router.post(
    "/predict/diabetes",
    response_model=PrediccionResultado,
    summary="Predict Diabetes Risk",
    tags=["Health (ML)"]
)
async def predecir_riesgo_diabetes(
    data: AnalisisEntrada,
    usuario=Depends(verify_supabase_token)
):
    """Predict diabetes/cardiometabolic risk."""
    pred = obtener_prediccion(data, model_type="diabetes")
    
    if "error" in pred:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=pred["error"]
        )
    
    return PrediccionResultado(
        score=pred["score"],
        drivers=pred["drivers"],
        categoria_riesgo=pred["categoria_riesgo"]
    )

@router.post(
    "/predict/cardiovascular",
    response_model=PrediccionResultado,
    summary="Predict Cardiovascular Risk",
    tags=["Health (ML)"]
)
async def predecir_riesgo_cardiovascular(
    data: AnalisisEntrada,
    usuario=Depends(verify_supabase_token)
):
    """Predict cardiovascular disease risk."""
    pred = obtener_prediccion(data, model_type="cardiovascular")
    
    if "error" in pred:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=pred["error"]
        )
    
    return PrediccionResultado(
        score=pred["score"],
        drivers=pred["drivers"],
        categoria_riesgo=pred["categoria_riesgo"]
    )
```

### Step 5: Update ML Service

Modify `back/app/services/ml_service.py`:

```python
def obtener_prediccion(data: AnalisisEntrada, model_type: str = "diabetes") -> dict:
    """
    Obtiene predicción de riesgo usando el modelo ML local.
    
    Args:
        data: Datos del usuario
        model_type: "diabetes" o "cardiovascular"
    """
    try:
        # ... prepare data ...
        
        result = predict_risk(
            model_type=model_type,  # Add this parameter
            age=data.edad,
            sex=data.genero,
            # ... other params
        )
        
        # ... return result
```

### Step 6: Update Frontend API Client

Add to `front/src/lib/api/client.ts`:

```typescript
export const healthAPI = {
  async predictDiabetes(data: AssessmentData): Promise<PredictResponse> {
    const response = await fetchWithAuth("/api/health/predict/diabetes", {
      method: "POST",
      body: JSON.stringify({ assessment_data: data }),
    });
    return await response.json();
  },

  async predictCardiovascular(data: AssessmentData): Promise<PredictResponse> {
    const response = await fetchWithAuth("/api/health/predict/cardiovascular", {
      method: "POST",
      body: JSON.stringify({ assessment_data: data }),
    });
    return await response.json();
  },

  // Legacy endpoint that defaults to diabetes
  async predict(data: AssessmentData): Promise<PredictResponse> {
    return this.predictDiabetes(data);
  },
};
```

### Step 7: Frontend Model Selection

Add a selector in the assessment form:

```tsx
const [modelType, setModelType] = useState<"diabetes" | "cardiovascular">("diabetes");

// In the form:
<div className="mb-4">
  <label className="block text-sm font-medium mb-2">
    Tipo de Evaluación
  </label>
  <select
    value={modelType}
    onChange={(e) => setModelType(e.target.value as "diabetes" | "cardiovascular")}
    className="w-full px-4 py-2 border rounded-lg"
  >
    <option value="diabetes">Riesgo de Diabetes</option>
    <option value="cardiovascular">Riesgo Cardiovascular</option>
  </select>
</div>

// When submitting:
const result = modelType === "diabetes"
  ? await healthAPI.predictDiabetes(formData)
  : await healthAPI.predictCardiovascular(formData);
```

## Directory Structure

```
back/
├── app/
│   ├── ml/
│   │   ├── models/
│   │   │   ├── model_xgb_calibrated.pkl          # Diabetes model
│   │   │   ├── imputer.pkl                        # Diabetes imputer
│   │   │   ├── feature_names.pkl                  # Diabetes features
│   │   │   ├── model_cardiovascular.pkl           # CV model
│   │   │   ├── imputer_cardiovascular.pkl         # CV imputer
│   │   │   └── feature_names_cardiovascular.pkl   # CV features
│   │   ├── model_loader.py
│   │   ├── predictor.py
│   │   └── ...
```

## Testing Multi-Model Setup

```bash
# Test diabetes endpoint
curl -X POST "http://localhost:8000/api/health/predict/diabetes" \
  -H "Content-Type: application/json" \
  -d '{"edad": 45, "genero": "M", "imc": 31.0}'

# Test cardiovascular endpoint
curl -X POST "http://localhost:8000/api/health/predict/cardiovascular" \
  -H "Content-Type: application/json" \
  -d '{"edad": 55, "genero": "F", "presion_sistolica": 140}'
```

## Migration Path

1. **Phase 1** (Current): Single diabetes model working
2. **Phase 2**: Add cardiovascular model with separate endpoints
3. **Phase 3**: Update frontend to allow model selection
4. **Phase 4**: Deprecate old `/predict` endpoint or keep as alias to diabetes

## Notes

- Both models can use the same feature engineering pipeline if features overlap
- RAG system can be shared or have model-specific knowledge bases
- Consider creating a base `Predictor` class that both models inherit from

