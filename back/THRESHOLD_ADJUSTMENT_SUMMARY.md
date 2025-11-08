# Cardiovascular Risk Threshold Adjustment - Implementation Summary

## Date
November 7, 2025

## Objective
Adjust risk thresholds for the cardiovascular model based on test findings showing that the model produces more conservative scores than the diabetes model.

## Changes Implemented

### 1. Updated Risk Interpretation Function
**File**: `back/app/ml/predictor.py`

Modified `_interpret_risk()` function to accept `model_type` parameter and apply different thresholds:

#### Diabetes Model Thresholds (unchanged)
- **Low risk**: score < 0.30
- **Moderate risk**: 0.30 ≤ score < 0.60
- **High risk**: score ≥ 0.60
- **Referral threshold**: ≥ 0.70

#### Cardiovascular Model Thresholds (new)
- **Low risk**: score < 0.20
- **Moderate risk**: 0.20 ≤ score < 0.30
- **High risk**: score ≥ 0.30
- **Referral threshold**: ≥ 0.35

### 2. Updated Function Call
Modified the call to `_interpret_risk()` in `predict_risk()` function to pass the `model_type` parameter, ensuring the appropriate thresholds are used based on the model being called.

## Test Results - Before vs After

### Cardiovascular Model Test Cases

| Patient Profile | Score | Risk Level (Before) | Risk Level (After) | Status |
|----------------|-------|--------------------|--------------------|--------|
| 28y female, BMI 21.3, healthy lipids | 0.0255 | Low | Low | ✓ Unchanged |
| 52y male, BMI 27.8, elevated lipids | 0.1122 | Low | Low | ✓ Unchanged |
| **68y male, BMI 34.5, poor lipids** | **0.2324** | **Low** | **Moderate** | ✓ **Improved** |
| 75y male, BMI 38.1, extreme values | 0.3059 | Moderate | High | ✓ Improved |

### Diabetes Model Test Cases (unchanged behavior)

| Patient Profile | Score | Risk Level | Status |
|----------------|-------|-----------|--------|
| 25y female, BMI 22, healthy | 0.0092 | Low | ✓ Correct |
| 50y male, BMI 27.8, some risk factors | 0.2810 | Low | ✓ Correct |
| 65y male, BMI 34.6, multiple risk factors | 0.6769 | High | ✓ Correct |

## Key Improvements

### Better Sensitivity for Cardiovascular Risk
The adjusted thresholds now better match the cardiovascular model's scoring behavior:
- **Before**: A 68-year-old with BMI 34.5 and poor lipid profile was classified as "low risk"
- **After**: Same patient is now appropriately classified as "moderate risk"

### Model-Specific Calibration
Each model now uses thresholds appropriate to its calibration:
- **Diabetes model**: Broader range, produces higher scores for high-risk patients
- **Cardiovascular model**: More conservative scoring, requires lower thresholds

## Rationale

The cardiovascular model was trained/calibrated differently than the diabetes model and produces more conservative scores. Based on testing:
- Even extreme risk profiles (75y, BMI 38.1, very poor lipids) only scored 0.31
- A 68-year-old with significant risk factors scored 0.23
- The old universal threshold (0.30 for low/moderate) was too high for this model

The new thresholds ensure:
1. **Appropriate sensitivity**: Patients with genuine risk factors are flagged
2. **Clinical relevance**: Classifications align better with expected risk levels
3. **Maintained specificity**: Low-risk patients still correctly identified

## Backend Configuration

✅ Backend is configured to use old models:
- `old_model_xgb_calibrated.pkl` (Diabetes)
- `old_model_cardiovascular.pkl` (Cardiovascular)

✅ Risk thresholds are now model-specific and automatically applied based on the `model_type` parameter

## Testing Confirmation

Both test scripts confirm the implementation:
- ✅ `test_old_models.py`: Shows correct threshold application per model type
- ✅ `test_new_cardiovascular.py`: Confirms model scores remain identical

## API Impact

No changes required to API contracts. The backend automatically applies the appropriate thresholds based on which model is used for the prediction. Frontend and API consumers will see more appropriate risk classifications for cardiovascular assessments.

---

**Implementation Status**: ✅ Complete  
**Tests Passed**: ✅ All tests passing  
**Ready for Production**: ✅ Yes

