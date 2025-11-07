# Testing Frontend-Backend ML Integration

## Current Architecture

### Models Available
1. **Diabetes/Cardiometabolic Risk Model** (Currently Integrated)
   - Location: `back/app/ml/models/model_xgb_calibrated.pkl`
   - Type: XGBoost with calibration
   - Purpose: Predicts diabetes/cardiometabolic risk

2. **Cardiovascular Model** (TODO)
   - Needs to be added separately
   - Should follow same structure

## Step 1: Start the Backend Server

```bash
cd back
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 2: Test Backend Endpoints Directly

### Test /predict endpoint

```bash
curl -X POST "http://localhost:8000/api/health/predict" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN" \
  -d '{
    "edad": 45,
    "genero": "M",
    "imc": 31.0,
    "circunferencia_cintura": 105,
    "horas_sueno": 6.0,
    "tabaquismo": true,
    "actividad_fisica": "sedentario"
  }'
```

Expected response:
```json
{
  "score": 0.XX,
  "drivers": ["feature1", "feature2", ...],
  "categoria_riesgo": "Alto"
}
```

### Test /coach endpoint

```bash
curl -X POST "http://localhost:8000/api/health/coach" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN" \
  -d '{
    "prediccion": {
      "score": 0.65,
      "drivers": ["bmi", "age"],
      "categoria_riesgo": "Alto"
    },
    "datos_usuario": {
      "edad": 45,
      "genero": "M",
      "imc": 31.0
    }
  }'
```

## Step 3: Start the Frontend

```bash
cd front
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Step 4: Configure Environment Variables

### Backend (.env)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_AVAILABLE=true
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
```

## Step 5: Test Through Frontend

1. **Navigate to Assessment Page**: `http://localhost:3000/assess`
2. **Fill in health data**:
   - Age: 45
   - Gender: Male
   - BMI: 31
   - Waist: 105 cm
   - Sleep: 6 hours
   - Smoking: Yes
   - Activity: Sedentary

3. **Submit Assessment**
4. **Check Network Tab**:
   - Should see POST to `/api/health/predict`
   - Response should contain `score`, `drivers`, `categoria_riesgo`

5. **Go to Coach Page**
6. **Ask a question**
7. **Check Network Tab**:
   - Should see POST to `/api/health/coach`
   - Response should contain personalized plan with citations

## Step 6: Verify Local Model is Being Used

### Add Logging to Backend

Add this to `back/app/ml/predictor.py` at the start of `predict_risk()`:

```python
logger.info("=" * 80)
logger.info("USING LOCAL ML MODEL")
logger.info(f"Model type: {type(model)}")
logger.info(f"Input: age={age}, sex={sex}, bmi={bmi}")
logger.info("=" * 80)
```

When you make a prediction, check the backend console for these logs.

### Verify No External API Calls

Check that there are NO calls to Colab or external ML services:
```bash
# In backend terminal, you should NOT see:
grep -r "requests.post.*colab" back/app/
```

## Troubleshooting

### Frontend shows "API not available"
- Check `NEXT_PUBLIC_API_AVAILABLE=true` in `.env.local`
- Restart Next.js dev server after changing env vars

### Backend returns 422 errors
- Check that frontend is sending correct field names
- Verify schema matches between frontend and backend

### Model loading fails
- Verify `.pkl` files are in `back/app/ml/models/`
- Check Python version matches (should be 3.10)

## Next Steps: Adding Cardiovascular Model

See `MULTI_MODEL_ARCHITECTURE.md` for implementing the cardiovascular model.

