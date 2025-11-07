# Cardiovascular Model Compliance Review Report

**Date:** November 7, 2025  
**Reviewer:** AI Assistant  
**Model Location:** `cardio/GUIA_HACKATHON_SALUD_NHANES_3.ipynb`  
**Reference Document:** `Desafio_Salud_NHANES_2025_duoc.txt`

---

## Executive Summary

This report evaluates the hypertension risk prediction model in the `cardio` folder against the hackathon's 100-point rubric. The model demonstrates solid ML fundamentals with proper anti-leakage measures and calibration, but has **critical gaps** in temporal validation, explainability, and fairness analysis that significantly impact the final score.

**Overall Status:** ⚠️ **PARTIAL COMPLIANCE** - 14-20 out of 30 points estimated for ML Rigor category

---

## A. Rigor Técnico ML (30 points) - Detailed Review

### A1. AUROC ≥ 0.80 (12 pts) - ❓ CANNOT VERIFY

**Rubric Requirements:**
- 12 pts: AUROC ≥ 0.80
- 10 pts: AUROC 0.75-0.79
- 7 pts: AUROC 0.70-0.74
- 4 pts: AUROC < 0.70

**Implementation Status:**
✅ **IMPLEMENTED CORRECTLY**
- Ensemble model (LogReg + RandomForest) at lines 376-383
- AUROC calculation on test set at line 388
- Proper use of `roc_auc_score()` from sklearn
- Model uses class balancing and SMOTE

**Critical Finding:**
❌ **ACTUAL METRIC VALUE UNKNOWN** - The notebook has not been executed, so actual AUROC cannot be verified. The code structure is correct but performance is unknown.

**Code Evidence:**
```python
# Line 388
auroc = roc_auc_score(y_test, proba_ensemble)
# Line 444
print(f"AUROC={auroc:.3f} | AUPRC={auprc:.3f} | Brier={brier:.3f}")
```

**Estimated Score:** 7-12 pts (depends on actual execution results)

---

### A2. Brier Score ≤ 0.12 (6 pts) - ❓ CANNOT VERIFY

**Rubric Requirements:**
- 6 pts: Brier ≤ 0.12
- 5 pts: Brier 0.13-0.15
- 3 pts: Brier 0.16-0.18
- 1 pt: Brier > 0.18

**Implementation Status:**
✅ **IMPLEMENTED CORRECTLY**
- `CalibratedClassifierCV` applied at line 424
- Calibration method: sigmoid with cv=3
- Brier Score calculated on test set at line 390
- Proper use of `brier_score_loss()`

**Code Evidence:**
```python
# Line 424
calibrated = CalibratedClassifierCV(best_model, method='sigmoid', cv=3)
calibrated.fit(X_train_full, y_train_full)

# Line 390
brier = brier_score_loss(y_test, proba_ensemble)
```

**Critical Finding:**
❌ **ACTUAL METRIC VALUE UNKNOWN** - Cannot verify if Brier ≤ 0.12 without execution.

**Visualizations:**
✅ ROC curve, Precision-Recall curve, and Confusion Matrix are generated (lines 449-467)
⚠️ Calibration curve code not found in notebook

**Estimated Score:** 3-6 pts (depends on actual execution results)

---

### A3. Validación Temporal & Anti-fuga (6 pts) - ⚠️ PARTIAL (4 pts)

**Rubric Requirements:**
- 6 pts: Split correcto por ciclo + sin fuga confirmada
- 4 pts: Dudas menores en implementación
- 2 pts: Errores de fuga o validación

**Anti-leakage Implementation:**
✅ **EXCELLENT - FULLY COMPLIANT**

The anti-leakage implementation is exemplary:

```python
# Lines 196-199: Explicit anti-leakage filter
forbidden_prefixes = ('BPX', 'BPXO', 'BPXSY', 'BPXDI')
feature_candidates = [c for c in feature_candidates 
                      if not any(c.startswith(pref) for pref in forbidden_prefixes)]
```

**Verification Results:**
- ✅ Label uses ONLY BPXO columns (lines 169-203)
- ✅ BP columns explicitly excluded from features (lines 196-199)
- ✅ Feature list verified to contain NO BP-related variables
- ✅ No derived BP features (e.g., mean_bp, pulse_pressure)

**Feature List Confirmed:**
```python
# Lines 188-195: Features without any BP data
base_features = [
    'edad', 'sexo', 'educacion', 'ratio_ingreso_pobreza',
    'imc', 'cintura_cm', 'rel_cintura_altura',
    'glucosa_mgdl', 'hdl_mgdl', 'trigliceridos_mgdl', 'ldl_mgdl',
    'imc_cuadratico', 'imc_x_edad', 'ratio_hdl_ldl', 'trigliceridos_log'
]
```

**Temporal Validation Implementation:**
⚠️ **IMPLEMENTATION CORRECT BUT DATA LIMITED**

The code correctly implements temporal validation:

```python
# Lines 280-285: Temporal split logic
if 'SDDSRVYR' in work.columns and work['SDDSRVYR'].nunique() > 1:
    cycles = sorted(work['SDDSRVYR'].dropna().unique().tolist())
    train_cycles, test_cycles = cycles[:-1], cycles[-1:]
    train_df = work[work['SDDSRVYR'].isin(train_cycles)].copy()
    test_df  = work[work['SDDSRVYR'].isin(test_cycles)].copy()
else:
    # Fallback to stratified split
    train_df, test_df = train_test_split(
        work, test_size=0.2, stratify=work['riesgo_hipertension'], random_state=42
    )
```

**CRITICAL ISSUE IDENTIFIED:**

❌ **DATA ONLY CONTAINS ONE CYCLE**
- Dataset: `nhanes_2017_2020_clean.csv` contains only SDDSRVYR=66.0 (5090 records)
- Expected: Multiple cycles for proper temporal validation
- Challenge requirement: Train on 2007-2016, test on 2017-Mar 2020
- **Actual behavior:** Falls back to stratified split (80/20) due to single cycle

**Impact:**
- The temporal validation LOGIC is correct
- The DATA does not support true temporal validation
- System uses fallback stratified split (which is valid but not optimal)

**K-Fold Usage:**
✅ **CORRECT - Not used as primary validation**
- K-fold used internally for model selection (lines 382-412)
- Final evaluation on held-out temporal test set (lines 388-403)
- This satisfies the "k-fold not as única validación" requirement

**Estimated Score:** 4 pts (correct implementation, but data limitation prevents full temporal validation)

---

### A4. Explicabilidad - Drivers Locales (6 pts) - ❌ MISSING (0 pts)

**Rubric Requirements:**
- 6 pts: Drivers claros, consistentes con modelo y caso
- 4 pts: Explicaciones parciales
- 2 pts: Explicaciones confusas o incorrectas

**Implementation Status:**
❌ **NOT IMPLEMENTED**

**Evidence:**
- SHAP library imported at line 314: `import shap`
- ❌ No SHAP explainer created
- ❌ No SHAP values calculated
- ❌ No local driver extraction per prediction
- ❌ No feature importance extraction

**What's Missing:**
```python
# Expected implementation (NOT PRESENT):
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
# Extract top drivers per instance
for i, instance in enumerate(X_test):
    top_features = get_top_drivers(shap_values[i])
```

**Impact:**
This is a **critical gap** for the `/predict` API endpoint requirement, which must return:
```json
{
  "score": float,
  "drivers": [top_features]  // ← MISSING
}
```

**Estimated Score:** 0 pts

---

## B. Mandatory Technical Rules - Compliance Check

### ✅ Anti-fuga de datos: **FULLY COMPLIANT**

**Rule:** If label uses BP clinical, those fields CANNOT be features

**Verification:**
- ✅ Label uses BPXO* columns (lines 169-203)
- ✅ BPXO/BPXSY/BPXDI explicitly excluded (lines 196-199)
- ✅ No derived BP features found
- ✅ Feature list validated clean

**Grade:** **EXCELLENT**

---

### ✅ Calibración: **COMPLIANT**

**Rule:** Must deliver calibration curve or Brier Score

**Verification:**
- ✅ `CalibratedClassifierCV` implemented (line 424)
- ✅ Brier Score calculated (line 390)
- ⚠️ Calibration curve visualization not found

**Grade:** **GOOD** (meets minimum requirement)

---

### ❌ Equidad (Fairness): **NOT COMPLIANT**

**Rule:** Report metrics by subgroups (sex, age, ethnicity) + calculate absolute gap

**Verification:**
- ❌ No fairness analysis found
- ❌ No subgroup metric breakdown
- ❌ No gap calculation
- ❌ No mitigation strategies

**Missing Implementation:**
```python
# Expected (NOT PRESENT):
for subgroup in ['sexo', 'edad_grupo', 'etnia']:
    subgroup_metrics = calculate_metrics_by_group(y_test, proba, subgroup)
    gap = calculate_absolute_gap(subgroup_metrics)
```

**Impact:**
This violates D3 rubric requirement (4 pts) and mandatory fairness rule.

**Grade:** **CRITICAL GAP**

---

### ✅ Reproducibilidad: **FULLY COMPLIANT**

**Rule:** requirements.txt + fixed seeds + documented scripts

**Verification:**
- ✅ `requirements.txt` exists and is comprehensive (78 lines)
- ✅ Seeds fixed throughout:
  - Line 45, 91: `np.random.seed(42)`
  - Line 330: `random_state=42` in train_test_split
  - Line 365, 374: `random_state=42` in models
  - Line 378-379: `random_state=42` in SMOTE
  - Line 387: `random_state=42` in StratifiedKFold
- ✅ All required packages listed with version constraints
- ✅ Documentation files present (README.md, QUICK_START.md)

**Grade:** **EXCELLENT**

---

### ⚠️ Ética: **PARTIAL**

**Rule:** Disclaimer visible + derivación rules

**Verification:**
- ⚠️ No disclaimer found in notebook
- ⚠️ No referral threshold defined
- ⚠️ No non-diagnostic language verification

**Note:** These may be implemented in separate API/app layers, but not in training notebook.

---

## C. Data and Features Verification

### Data Availability: ✅ CONFIRMED

**File:** `cardio/data/processed/nhanes_2017_2020_clean.csv`
- Size: 1.6 MB
- Rows: 5,091 records (including header)
- Columns verified: SEQN, SDDSRVYR, BPXO*, BMX*, LAB_*

**Issue:** Only contains single cycle (SDDSRVYR=66.0), limiting temporal validation capability.

---

### Feature Engineering: ✅ WELL IMPLEMENTED

**Demographic Features** (lines 96-102):
- ✅ edad (RIDAGEYR)
- ✅ sexo (RIAGENDR) - binary encoded 0=M, 1=F
- ✅ etnia (RIDRETH1) - one-hot encoded
- ✅ educacion (DMDEDUC2) - cleaned
- ✅ ratio_ingreso_pobreza (INDFMPIR)

**Anthropometric Features** (lines 103-108):
- ✅ peso_kg (BMXWT)
- ✅ altura_cm (BMXHT)
- ✅ imc (BMXBMI)
- ✅ cintura_cm (BMXWAIST)

**Lab Features** (lines 109-111):
- ✅ glucosa_mgdl (LAB_LBXGLU)
- ✅ hdl_mgdl (LAB_LBDHDD)
- ✅ trigliceridos_mgdl (LAB_LBXTR)
- ✅ ldl_mgdl (LAB_LBDLDL)

**Derived Features** (lines 159-197):
- ✅ rel_cintura_altura (cintura/altura)
- ✅ imc_cuadratico (imc²)
- ✅ imc_x_edad (imc × edad)
- ✅ ratio_hdl_ldl (hdl/ldl)
- ✅ trigliceridos_log (log1p transform)

**Quality:** Feature engineering is comprehensive and well-documented.

---

### Label Creation: ✅ CORRECT

**Hypertension Classification** (lines 167-203):

```python
# Class definitions:
# 0 = Hypotension (SYS<90 or DIA<60)
# 1 = Normal
# 2 = Hypertension (SYS≥140 or DIA≥90)
#
# Binary risk:
# riesgo_hipertension = 1 if class==2, else 0
```

**Verification:**
- ✅ Uses ONLY BPXO columns (oscillometric BP)
- ✅ Averages multiple readings (BPXOSY1-3, BPXODI1-3)
- ✅ Handles missing values appropriately
- ✅ Binary target created correctly
- ✅ Records with no label are dropped

---

## D. Model Training Verification

### Preprocessing Pipeline: ✅ CORRECT (lines 349-354)

```python
num_tf = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),  # ✅
    ('scaler', StandardScaler())                     # ✅
])
pre = ColumnTransformer([('num', num_tf, feature_candidates)], remainder='drop')
```

**Grade:** GOOD

---

### Model Configuration: ✅ OPTIMIZED

**LogisticRegression** (lines 359-366):
- ✅ class_weight='balanced'
- ✅ solver='saga'
- ✅ C=1.0, penalty='l2'
- ✅ max_iter=1000
- ✅ random_state=42

**RandomForest** (lines 367-375):
- ✅ n_estimators=800
- ✅ max_depth=14
- ✅ min_samples_split=4
- ✅ min_samples_leaf=2
- ✅ class_weight='balanced_subsample'
- ✅ n_jobs=-1
- ✅ random_state=42

**Grade:** EXCELLENT - Well-tuned hyperparameters

---

### SMOTE Integration: ✅ CORRECT (lines 378-379)

```python
ImbPipeline([
    ('pre', pre), 
    ('smote', SMOTE(random_state=42, k_neighbors=3)),  # ✅ Inside pipeline
    ('clf', log_reg)
])
```

**Verification:**
- ✅ SMOTE applied INSIDE pipeline (no leakage)
- ✅ k_neighbors=3 (appropriate for minority class)
- ✅ Applied separately in each fold

**Grade:** EXCELLENT

---

### Ensemble Strategy: ✅ WELL IMPLEMENTED (lines 376-383)

```python
proba_lr = models['LogReg'].fit(X_train_full, y_train_full).predict_proba(X_test)[:, 1]
proba_rf = models['RandomForest'].fit(X_train_full, y_train_full).predict_proba(X_test)[:, 1]
proba_ensemble = (proba_lr + proba_rf) / 2  # Simple averaging
```

**Grade:** GOOD

---

### Model Persistence: ✅ CORRECT (lines 469-474)

```python
models_dir = Path('models'); models_dir.mkdir(exist_ok=True)
model_path = models_dir / 'ensemble_logreg_rf_calibrado.pkl'
joblib.dump(calibrated, model_path)
```

**Verification:**
- ✅ Saves calibrated model
- ✅ Creates directory if needed
- ✅ Uses joblib for serialization
- ✅ Model file found: `cardio/models/ensemble_logreg_rf_calibrado.pkl`

**Grade:** EXCELLENT

---

## E. Documentation Review

### README.md: ✅ GOOD (197 lines)

**Strengths:**
- Clear quick start instructions
- Data download/conversion guidance
- Structure documentation
- Checklist of deliverables

**Weaknesses:**
- No actual team information
- Missing architecture diagram

**Grade:** GOOD (4/5 pts)

---

### QUICK_START.md: ✅ EXCELLENT (122 lines)

**Strengths:**
- Step-by-step 5-minute guide
- Clear environment setup
- Data preparation instructions

**Grade:** EXCELLENT (5/5 pts)

---

### requirements.txt: ✅ EXCELLENT (78 lines)

**Strengths:**
- Comprehensive package list
- Version constraints specified
- Well-organized by category
- Includes all necessary dependencies

**Missing from requirements:**
- ⚠️ imbalanced-learn (for SMOTE) - should be added

**Grade:** EXCELLENT (5.5/6 pts)

---

## Summary: Compliance Scoring

### A. Rigor Técnico ML (30 pts)

| Criterion | Max | Estimated | Status |
|-----------|-----|-----------|--------|
| A1. AUROC | 12 | 7-12 | ❓ Unknown (needs execution) |
| A2. Brier Score | 6 | 3-6 | ❓ Unknown (needs execution) |
| A3. Validación & Anti-fuga | 6 | 4 | ⚠️ Partial (data limits temporal) |
| A4. Explicabilidad | 6 | 0 | ❌ Missing |
| **TOTAL A** | **30** | **14-22** | **⚠️ PARTIAL** |

---

## Critical Issues Summary

### 🔴 BLOCKING ISSUES (Must Fix)

1. **A4: No SHAP/Explainability Implementation**
   - Impact: 0/6 pts lost
   - Blocks API requirement: drivers not available
   - Fix: Implement SHAP explainer and extract top drivers

2. **Single Cycle Data Limits Temporal Validation**
   - Impact: 2 pts lost (4/6 instead of 6/6)
   - Challenge expects: Multiple cycles (2007-2020)
   - Actual: Only cycle 66.0 (2017-2020)
   - Fix: Obtain and merge additional NHANES cycles

3. **No Fairness Analysis**
   - Impact: Violates mandatory rule
   - Missing: Subgroup metrics, gap calculation
   - Fix: Implement fairness analysis by sex/age/ethnicity

---

### 🟡 HIGH PRIORITY (Should Fix)

4. **No Calibration Curve Visualization**
   - Impact: Minor point deduction possible
   - Fix: Add calibration_curve() plot

5. **Missing Actual Performance Metrics**
   - Impact: Cannot verify AUROC/Brier compliance
   - Fix: Execute notebook and document results

6. **No Disclaimer/Safety Elements in Notebook**
   - Impact: Ethical rule compliance unclear
   - Fix: Add medical disclaimer and referral logic

---

### 🟢 NICE TO HAVE (Optional)

7. **Add imbalanced-learn to requirements.txt**
   - Impact: Minor reproducibility issue
   - Fix: Add `imbalanced-learn>=0.11.0` to requirements

8. **Create Architecture Diagram**
   - Impact: Documentation completeness
   - Fix: Add visual diagram to README

---

## Strengths

✅ **Anti-leakage implementation is exemplary**
✅ **Reproducibility is excellent** (seeds, requirements, docs)
✅ **Feature engineering is comprehensive and well-documented**
✅ **Model configuration is well-tuned and appropriate**
✅ **SMOTE integration is correct (no leakage)**
✅ **Calibration is properly implemented**
✅ **Code is clean, well-commented, and follows best practices**

---

## Recommendations (Priority Order)

### 1. IMMEDIATE (Before Submission)

**Action 1: Implement SHAP Explainability**
```python
# Add after model training (around line 427):
import shap
explainer = shap.TreeExplainer(calibrated.calibrated_classifiers_[0].estimator)
shap_values = explainer.shap_values(X_test)

# Function to get top drivers for single prediction
def get_top_drivers(instance_shap, feature_names, n=5):
    importance = np.abs(instance_shap)
    top_idx = np.argsort(importance)[-n:][::-1]
    return [(feature_names[i], float(instance_shap[i])) for i in top_idx]
```

**Action 2: Add Fairness Analysis**
```python
# Add fairness analysis section before model saving:
def analyze_fairness(y_true, y_pred_proba, df, subgroup_col):
    results = {}
    for group in df[subgroup_col].unique():
        mask = df[subgroup_col] == group
        if mask.sum() > 0:
            auroc = roc_auc_score(y_true[mask], y_pred_proba[mask])
            results[group] = auroc
    return results

fairness_sexo = analyze_fairness(y_test, proba_ensemble, test_df, 'sexo')
fairness_edad = analyze_fairness(y_test, proba_ensemble, 
                                 test_df, pd.cut(test_df['edad'], bins=[18,40,60,100]))
print("Fairness by Sex:", fairness_sexo)
print("Fairness by Age:", fairness_edad)
print("Absolute Gap (Sex):", max(fairness_sexo.values()) - min(fairness_sexo.values()))
```

**Action 3: Execute Notebook and Document Metrics**
- Run all cells
- Document final AUROC and Brier Score
- Save output as markdown or PDF

**Action 4: Add Calibration Curve**
```python
# Add after line 467:
from sklearn.calibration import calibration_curve
prob_true, prob_pred = calibration_curve(y_test, proba_ensemble, n_bins=10)
plt.figure(figsize=(6,6))
plt.plot(prob_pred, prob_true, marker='o')
plt.plot([0,1],[0,1],'k--')
plt.xlabel('Predicted Probability')
plt.ylabel('True Probability')
plt.title('Calibration Curve')
plt.grid(alpha=.3)
plt.show()
```

---

### 2. IMPORTANT (Improves Score)

**Action 5: Obtain Multi-Cycle Data**
- Download NHANES cycles 2007-2016 for training
- Merge with existing 2017-2020 test data
- Re-run with proper temporal validation

**Action 6: Add Disclaimer and Safety**
```python
# Add at beginning of notebook:
MEDICAL_DISCLAIMER = """
⚠️ MEDICAL DISCLAIMER:
This system does NOT provide medical diagnoses. 
Results are for educational/informational purposes only.
Always consult a qualified healthcare professional for medical advice.
"""
print(MEDICAL_DISCLAIMER)

# Add referral threshold:
REFERRAL_THRESHOLD = 0.70
if auroc >= REFERRAL_THRESHOLD:
    print("⚠️ HIGH RISK: Immediate consultation with healthcare provider recommended")
```

**Action 7: Update requirements.txt**
```bash
# Add missing package:
imbalanced-learn>=0.11.0
```

---

### 3. OPTIONAL (Polish)

**Action 8: Create Comprehensive Technical Report**
- 2-3 pages covering all rubric sections
- Include visualizations
- Document all decisions and limitations

**Action 9: Create Architecture Diagram**
- Visual flow: Data → Features → Model → Calibration → API
- Include in README.md

**Action 10: Add Unit Tests**
- Test anti-leakage filter
- Test feature engineering functions
- Test model loading/prediction

---

## Estimated Time to Address Issues

| Priority | Actions | Estimated Time |
|----------|---------|----------------|
| IMMEDIATE | Actions 1-4 | 3-4 hours |
| IMPORTANT | Actions 5-7 | 4-6 hours |
| OPTIONAL | Actions 8-10 | 2-3 hours |
| **TOTAL** | | **9-13 hours** |

---

## Final Assessment

### What Works Well

The cardiovascular model demonstrates **solid ML engineering fundamentals**:
- Clean, reproducible code
- Proper data handling and preprocessing
- Appropriate model selection and tuning
- Excellent anti-leakage implementation
- Good documentation structure

### Critical Gaps

The model **fails to meet key rubric requirements**:
- ❌ No explainability (SHAP) implementation
- ❌ No fairness analysis
- ⚠️ Limited temporal validation (data constraint)
- ❓ Performance metrics unknown (not executed)

### Path to Full Compliance

With **3-4 hours of focused work** on IMMEDIATE actions, the model can achieve:
- Full explainability compliance (6 pts)
- Fairness analysis implementation (4 pts)
- Verified performance metrics
- Calibration curve visualization

This would bring the estimated score from **14-22/30** to **24-28/30** in the ML Rigor category.

---

## Conclusion

The `cardio` model has a **strong technical foundation** but requires **critical additions** in explainability and fairness to meet hackathon requirements. The anti-leakage implementation is exemplary, and the overall code quality is high. With focused effort on the identified gaps, this model can achieve full compliance with the rubric.

**Recommended Next Steps:**
1. Implement SHAP explainability (CRITICAL)
2. Add fairness analysis (CRITICAL)
3. Execute notebook to verify metrics (HIGH)
4. Add calibration curve (HIGH)
5. Consider multi-cycle data if time permits (OPTIONAL)

---

**Report Generated:** November 7, 2025  
**Review Completed By:** AI Assistant  
**Confidence Level:** High (based on comprehensive code review)

