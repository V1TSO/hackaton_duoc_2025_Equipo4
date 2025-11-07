# Action Checklist - Cardio Model Compliance

**Priority:** IMMEDIATE (Before Hackathon Submission)  
**Time Required:** 3-4 hours  
**Potential Score Improvement:** +10-14 points

---

## ✅ Completed (Already Done)

- [x] Anti-leakage implementation (EXCELLENT)
- [x] Calibration with CalibratedClassifierCV
- [x] Seed fixing throughout code
- [x] Feature engineering
- [x] Model training pipeline
- [x] SMOTE integration (no leakage)
- [x] Requirements.txt
- [x] Documentation (README, QUICK_START)

---

## 🔴 CRITICAL (Must Complete - 3 hours)

### [ ] 1. Add SHAP Explainability (30 minutes) → +6 pts

**Where:** After line 427 in notebook  
**Impact:** A4 compliance (0 → 6 pts)

```python
# ==========================================================
# SHAP EXPLAINABILITY
# ==========================================================
import shap

# Create explainer (use underlying model from calibrated)
base_model = calibrated.calibrated_classifiers_[0].estimator
explainer = shap.TreeExplainer(base_model)

# Calculate SHAP values for test set
# Note: Need to transform test data first
X_test_transformed = pre.transform(X_test)
shap_values = explainer.shap_values(X_test_transformed)

# Function to get top drivers for a single prediction
def get_top_drivers(shap_values_instance, feature_names, n=5):
    """Extract top N features driving prediction."""
    importance = np.abs(shap_values_instance)
    top_idx = np.argsort(importance)[-n:][::-1]
    drivers = []
    for i in top_idx:
        drivers.append({
            'feature': feature_names[i],
            'shap_value': float(shap_values_instance[i]),
            'impact': 'increases_risk' if shap_values_instance[i] > 0 else 'decreases_risk'
        })
    return drivers

# Example: Get drivers for first test instance
example_drivers = get_top_drivers(shap_values[0], feature_candidates)
print("Top drivers for first instance:", example_drivers)

# SHAP summary plot
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test_transformed, feature_names=feature_candidates, show=False)
plt.title('SHAP Feature Importance - Test Set')
plt.tight_layout()
plt.savefig('models/shap_summary.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ SHAP explainability implemented")
```

**Verification:**
- [ ] SHAP values calculated correctly
- [ ] Top drivers extracted per instance
- [ ] SHAP summary plot generated
- [ ] Function ready for API integration

---

### [ ] 2. Add Fairness Analysis (45 minutes) → Compliance

**Where:** After line 467 in notebook  
**Impact:** D3 compliance + mandatory rule

```python
# ==========================================================
# FAIRNESS ANALYSIS BY SUBGROUPS
# ==========================================================

def analyze_fairness_comprehensive(y_true, y_pred_proba, y_pred_binary, df, metrics=['auroc', 'precision', 'recall']):
    """
    Analyze model fairness across demographic subgroups.
    Returns metrics by subgroup and absolute gaps.
    """
    results = {}
    
    # Sex analysis
    if 'sexo' in df.columns:
        results['sex'] = {}
        for sex_val in df['sexo'].unique():
            if pd.notna(sex_val):
                mask = df['sexo'] == sex_val
                sex_label = 'Male' if sex_val == 0 else 'Female'
                n_samples = mask.sum()
                
                if n_samples > 0 and len(np.unique(y_true[mask])) > 1:
                    results['sex'][sex_label] = {
                        'n': int(n_samples),
                        'auroc': float(roc_auc_score(y_true[mask], y_pred_proba[mask])),
                        'precision': float(precision_score(y_true[mask], y_pred_binary[mask])),
                        'recall': float(recall_score(y_true[mask], y_pred_binary[mask]))
                    }
    
    # Age group analysis
    if 'edad' in df.columns:
        results['age_group'] = {}
        age_bins = [18, 40, 60, 100]
        age_labels = ['18-39', '40-59', '60+']
        df_temp = df.copy()
        df_temp['age_group'] = pd.cut(df_temp['edad'], bins=age_bins, labels=age_labels, include_lowest=True)
        
        for age_group in age_labels:
            mask = df_temp['age_group'] == age_group
            n_samples = mask.sum()
            
            if n_samples > 0 and len(np.unique(y_true[mask])) > 1:
                results['age_group'][age_group] = {
                    'n': int(n_samples),
                    'auroc': float(roc_auc_score(y_true[mask], y_pred_proba[mask])),
                    'precision': float(precision_score(y_true[mask], y_pred_binary[mask])),
                    'recall': float(recall_score(y_true[mask], y_pred_binary[mask]))
                }
    
    # Ethnicity analysis (if one-hot encoded columns exist)
    etnia_cols = [c for c in df.columns if c.startswith('etnia_')]
    if etnia_cols:
        results['ethnicity'] = {}
        for col in etnia_cols:
            mask = df[col] == 1
            n_samples = mask.sum()
            
            if n_samples > 0 and len(np.unique(y_true[mask])) > 1:
                results['ethnicity'][col] = {
                    'n': int(n_samples),
                    'auroc': float(roc_auc_score(y_true[mask], y_pred_proba[mask])),
                    'precision': float(precision_score(y_true[mask], y_pred_binary[mask])),
                    'recall': float(recall_score(y_true[mask], y_pred_binary[mask]))
                }
    
    return results

# Run fairness analysis
fairness_results = analyze_fairness_comprehensive(
    y_test.values, 
    proba_ensemble, 
    pred_opt,
    test_df
)

# Calculate absolute gaps
print("\n📊 FAIRNESS ANALYSIS RESULTS:")
print("="*60)

for dimension, groups in fairness_results.items():
    print(f"\n{dimension.upper()} Analysis:")
    aurocs = [g['auroc'] for g in groups.values()]
    gap = max(aurocs) - min(aurocs)
    
    for group_name, metrics in groups.items():
        print(f"  {group_name:20} (n={metrics['n']:4}): "
              f"AUROC={metrics['auroc']:.3f} | "
              f"Precision={metrics['precision']:.3f} | "
              f"Recall={metrics['recall']:.3f}")
    
    print(f"  → Absolute Gap (AUROC): {gap:.4f}")
    
    if gap > 0.1:
        print(f"  ⚠️  Significant disparity detected (gap > 0.1)")
    else:
        print(f"  ✅ Acceptable disparity (gap ≤ 0.1)")

# Save fairness report
import json
with open('models/fairness_report.json', 'w') as f:
    json.dump(fairness_results, f, indent=2)

print("\n✅ Fairness analysis completed and saved")
```

**Verification:**
- [ ] Metrics calculated by sex
- [ ] Metrics calculated by age group
- [ ] Metrics calculated by ethnicity
- [ ] Absolute gaps calculated and documented
- [ ] Report saved to JSON

---

### [ ] 3. Add Calibration Curve (15 minutes)

**Where:** After line 467 in notebook  
**Impact:** A2 visual verification

```python
# ==========================================================
# CALIBRATION CURVE
# ==========================================================
from sklearn.calibration import calibration_curve

prob_true, prob_pred = calibration_curve(y_test, proba_ensemble, n_bins=10)

plt.figure(figsize=(8, 6))
plt.plot(prob_pred, prob_true, marker='o', linewidth=2, label='Ensemble Model')
plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
plt.xlabel('Predicted Probability', fontsize=12)
plt.ylabel('True Probability', fontsize=12)
plt.title('Calibration Curve - Ensemble Model', fontsize=14)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('models/calibration_curve.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"✅ Calibration curve saved: Brier Score = {brier:.4f}")
```

**Verification:**
- [ ] Calibration curve generated
- [ ] Saved to models/ directory
- [ ] Visual shows calibration quality

---

### [ ] 4. Execute Notebook & Document Results (15 minutes)

**Steps:**
1. Open Jupyter: `jupyter notebook GUIA_HACKATHON_SALUD_NHANES_3.ipynb`
2. Restart kernel and run all cells
3. Document results:

```markdown
## FINAL RESULTS

**Executed:** [Date/Time]
**Environment:** Python [version], [key packages]

### Performance Metrics (Test Set)
- AUROC: [value]
- AUPRC: [value]
- Brier Score: [value]
- Optimal Threshold: [value]
- Accuracy: [value]
- Precision: [value]
- Recall: [value]

### Compliance Score
- A1 (AUROC): [X/12 pts]
- A2 (Brier): [X/6 pts]
- A3 (Validation): 4/6 pts
- A4 (Explainability): 6/6 pts
- **Total: [X/30 pts]**

### Fairness Metrics
- Sex Gap: [value]
- Age Gap: [value]
- Ethnicity Gap: [value]
```

**Verification:**
- [ ] All cells execute without errors
- [ ] AUROC ≥ 0.70 achieved
- [ ] Brier Score < 0.20 achieved
- [ ] Results documented

---

### [ ] 5. Add Medical Disclaimer (15 minutes)

**Where:** Beginning and end of notebook

```python
# ==========================================================
# MEDICAL DISCLAIMER
# ==========================================================

DISCLAIMER = """
╔══════════════════════════════════════════════════════════════╗
║                    ⚠️  MEDICAL DISCLAIMER  ⚠️                 ║
╚══════════════════════════════════════════════════════════════╝

This hypertension risk prediction model is for EDUCATIONAL and 
RESEARCH purposes ONLY. It does NOT provide medical diagnoses, 
treatment recommendations, or professional medical advice.

IMPORTANT:
• This is a statistical model based on population data
• Results are estimates and may not reflect individual health status
• Always consult a qualified healthcare professional for medical advice
• Do not use this tool to make medical decisions
• In case of health concerns, seek immediate professional medical care

By using this model, you acknowledge and accept these limitations.
"""

print(DISCLAIMER)

# Add referral threshold logic
REFERRAL_THRESHOLD = 0.70

def check_referral_needed(risk_score):
    """Determine if professional referral is recommended."""
    if risk_score >= REFERRAL_THRESHOLD:
        return True, (
            f"⚠️  HIGH RISK DETECTED (Score: {risk_score:.2f})\n"
            f"Immediate consultation with a healthcare professional is strongly recommended.\n"
            f"This is NOT a diagnosis, but warrants professional evaluation."
        )
    else:
        return False, (
            f"Risk Score: {risk_score:.2f}\n"
            f"Continue healthy lifestyle practices and regular check-ups.\n"
            f"Consult healthcare provider for personalized advice."
        )
```

**Verification:**
- [ ] Disclaimer printed at start
- [ ] Referral logic implemented
- [ ] Messages are non-diagnostic

---

### [ ] 6. Update requirements.txt (5 minutes)

**Add missing package:**

```bash
# Add to requirements.txt
imbalanced-learn>=0.11.0,<1.0.0   # SMOTE and resampling techniques
```

**Then reinstall:**
```bash
pip install -r requirements.txt
```

**Verification:**
- [ ] imbalanced-learn added
- [ ] All packages install successfully
- [ ] No dependency conflicts

---

## 🟡 IMPORTANT (If Time Permits - 2 hours)

### [ ] 7. Create Technical Report (60 minutes)

**File:** `TECHNICAL_REPORT.md`

**Sections:**
1. Introduction & Objectives
2. Data Description (NHANES 2017-2020)
3. Feature Engineering
4. Model Architecture (Ensemble + Calibration)
5. Validation Strategy (Temporal attempt + Fallback)
6. Anti-Leakage Measures
7. Performance Metrics
8. Calibration Analysis
9. Fairness Analysis
10. Explainability (SHAP)
11. Guardrails & Safety
12. Limitations & Future Work

**Target:** 2-3 pages

---

### [ ] 8. Multi-Cycle Data (60 minutes)

**If feasible:**
1. Download NHANES 2015-2016 cycle
2. Merge with existing 2017-2020 data
3. Re-run with true temporal split
4. Document improvement in temporal validation

**Note:** This is optional but improves A3 score from 4/6 to 6/6

---

## 🟢 NICE TO HAVE (Polish - 1 hour)

### [ ] 9. Architecture Diagram (30 minutes)

Create visual diagram showing:
- Data → Preprocessing → Feature Engineering
- Model Training (LogReg + RF + Ensemble)
- Calibration → SHAP → API

### [ ] 10. Unit Tests (30 minutes)

Test critical functions:
- Anti-leakage filter
- Feature engineering
- Model loading
- Driver extraction

---

## Execution Order

**Recommended sequence:**
1. SHAP (30 min) - Highest impact
2. Fairness (45 min) - Mandatory compliance
3. Calibration Curve (15 min) - Quick win
4. Execute Notebook (15 min) - Verify everything works
5. Document Results (15 min) - Capture metrics
6. Disclaimer (15 min) - Ethical requirement
7. Update requirements (5 min) - Reproducibility

**Total Core Time:** ~140 minutes (2.5 hours)

---

## Verification Checklist

**Before considering complete:**
- [ ] All CRITICAL items completed
- [ ] Notebook executes without errors
- [ ] AUROC and Brier documented
- [ ] SHAP drivers extractable
- [ ] Fairness report generated
- [ ] Calibration curve created
- [ ] Disclaimer visible
- [ ] Requirements.txt updated
- [ ] All plots saved to models/ directory
- [ ] Results documented in notebook

---

## Expected Score After Completion

**Before:**
- A1: 7-12? pts (unknown)
- A2: 3-6? pts (unknown)
- A3: 4 pts
- A4: 0 pts
- **Total: 14-22 pts**

**After:**
- A1: 7-12 pts (verified by execution)
- A2: 3-6 pts (verified + curve)
- A3: 4 pts (unchanged)
- A4: 6 pts (+6 pts improvement)
- **Total: 20-28 pts**

**Improvement:** +6 to +14 points depending on model performance

---

**Last Updated:** November 7, 2025  
**Status:** Ready for execution  
**Priority:** IMMEDIATE

