# Quick Start: Testing the ML Integration

## 🚀 Quick Test (5 minutes)

### 1. Start Backend
```bash
cd back
source venv/bin/activate
uvicorn main:app --reload
```

**Look for these startup messages:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
✅ Model loaded successfully with XX features
INFO:     Application startup complete.
```

### 2. Run Test Script
```bash
cd back
./test_api_live.sh
```

This will:
- ✓ Check health endpoint
- ✓ Test predict endpoint
- ✓ Verify model files exist
- ✓ Check knowledge base

### 3. Watch Backend Logs

When a prediction is made, you should see:
```
================================================================================
🔬 USING LOCAL ML MODEL (Not Colab/External API)
   Input: age=45, sex=M, bmi=31.0
================================================================================
✓ Model loaded: CalibratedClassifierCV
✓ Prediction complete: score=0.XXX, level=Alto
================================================================================
```

**❌ You should NOT see:**
- Any mention of "Colab"
- HTTP requests to external URLs
- Timeout errors
- Connection errors

### 4. Test from Frontend

```bash
cd front
npm run dev
```

1. Go to `http://localhost:3000/assess`
2. Fill in the form
3. Submit
4. **Check backend terminal** - you should see the log messages above
5. Frontend should display risk score and drivers

## 🔍 Verification Checklist

- [ ] Backend starts without errors
- [ ] Model loads successfully (check logs)
- [ ] Test script passes all checks
- [ ] Predict endpoint returns score and drivers
- [ ] Backend logs show "USING LOCAL ML MODEL"
- [ ] Backend logs show NO "Colab" or external API mentions
- [ ] Frontend can submit assessment
- [ ] Frontend displays risk score
- [ ] Frontend shows risk drivers/factors
- [ ] Coach page generates personalized plans

## 🐛 Common Issues

### Issue: "ModuleNotFoundError: No module named 'joblib'"
**Solution:**
```bash
cd back
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Model file not found"
**Solution:**
```bash
# Verify files exist
ls -la back/app/ml/models/
# Should see: model_xgb_calibrated.pkl, imputer.pkl, feature_names.pkl
```

### Issue: Frontend shows "API not available"
**Solution:**
```bash
# Check frontend .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> front/.env.local
echo "NEXT_PUBLIC_API_AVAILABLE=true" >> front/.env.local

# Restart Next.js
cd front
npm run dev
```

### Issue: "401 Unauthorized"
**Solution:**
- Make sure you're logged in on the frontend
- Check that Supabase credentials are correct in backend `.env`

### Issue: Still seeing Colab mentions
**Solution:**
- Verify you're running the updated backend
- Check that `ml_service.py` imports from `app.ml.predictor` not `requests`
- Restart the backend server

## 📊 Expected Response Format

### /predict endpoint
```json
{
  "score": 0.65,
  "drivers": [
    "bmi",
    "age", 
    "waist_height_ratio",
    "lifestyle_risk_score",
    "central_obesity"
  ],
  "categoria_riesgo": "Alto"
}
```

### /coach endpoint
```json
{
  "plan_ia": "# Plan Personalizado...",
  "citas_kb": ["actividad_fisica.md"],
  "fuente_modelo": "NHANES_XGB_v1"
}
```

## 🎯 Performance Expectations

- **Prediction Time**: < 1 second
- **Coach Generation**: 3-10 seconds (depends on OpenAI API)
- **Model Load Time**: < 2 seconds (first request only, then cached)

## 📝 Next Steps

Once basic testing works:
1. See `MULTI_MODEL_ARCHITECTURE.md` for adding cardiovascular model
2. See `TESTING_INTEGRATION.md` for detailed integration testing
3. Test with real user data
4. Monitor logs in production

## 🆘 Need Help?

Check:
1. Backend logs for error messages
2. Frontend browser console (F12)
3. Network tab for API responses
4. `TESTING_INTEGRATION.md` for detailed troubleshooting

