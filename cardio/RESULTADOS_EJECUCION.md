# Resultados de Ejecución - Modelo Cardiovascular

**Fecha de Ejecución:** Noviembre 7, 2025  
**Notebook:** `GUIA_HACKATHON_SALUD_NHANES_3.ipynb`  
**Dataset:** `nhanes_2017_2020_clean.csv` (2,987 registros finales)

---

## 📊 MÉTRICAS FINALES (Test Set)

### Rendimiento del Ensemble (LogReg + RandomForest)

```
AUROC = 0.752
AUPRC = 0.447
Brier Score = 0.181
Umbral óptimo (F1) = 0.50
Accuracy = 0.717
Precision = 0.393
Recall = 0.648
```

### Distribución de Datos

**Train Set:**
- Clase 0 (NoHTA): 1,889 registros
- Clase 1 (HTA): 500 registros
- **Total:** 2,389 registros

**Test Set:**
- Clase 0 (NoHTA): 473 registros
- Clase 1 (HTA): 125 registros
- **Total:** 598 registros

**Desbalance:** ~3.8:1 (manejado con SMOTE y class_weight)

---

## 🎯 PUNTUACIÓN SEGÚN RÚBRICA

### A. Rigor Técnico ML (30 puntos)

| Criterio | Métrica Obtenida | Puntos Máx | Puntos Obtenidos | Estado |
|----------|------------------|------------|------------------|---------|
| **A1. AUROC** | 0.752 | 12 | **10** | ✅ Bueno |
| **A2. Brier Score** | 0.181 | 6 | **1** | ⚠️ Bajo |
| **A3. Validación & Anti-fuga** | Implementado | 6 | **4** | ⚠️ Parcial |
| **A4. Explicabilidad** | No implementado | 6 | **0** | ❌ Falta |
| **TOTAL** | | **30** | **15** | **50%** |

### Detalle por Criterio

#### A1. AUROC: 10/12 puntos ✅

**Rúbrica:**
- 12 pts: AUROC ≥ 0.80 ❌
- **10 pts: AUROC 0.75-0.79** ← **LOGRADO (0.752)**
- 7 pts: AUROC 0.70-0.74
- 4 pts: AUROC < 0.70

**Análisis:**
- ✅ AUROC de 0.752 está en el rango 0.75-0.79
- ✅ Por encima del baseline aceptable (0.70)
- ⚠️ A 0.048 puntos del máximo (12 pts con AUROC ≥ 0.80)
- ✅ Cross-validation estable: 0.724 ± 0.020

**Mejoras para alcanzar 12 pts:**
1. Feature engineering adicional
2. Tuning más agresivo de hiperparámetros
3. Probar modelos más complejos (XGBoost, LightGBM)
4. Incluir más ciclos NHANES para mayor datos de entrenamiento

---

#### A2. Brier Score: 1/6 puntos ⚠️

**Rúbrica:**
- 6 pts: Brier ≤ 0.12 ❌
- 5 pts: Brier 0.13-0.15 ❌
- 3 pts: Brier 0.16-0.18 ❌
- **1 pt: Brier > 0.18** ← **OBTENIDO (0.181)**

**Análisis:**
- ❌ Brier Score de 0.181 apenas supera el umbral de 0.18
- ⚠️ Calibración insuficiente a pesar de usar CalibratedClassifierCV
- 📉 El Brier en CV fue 0.212, mejoró a 0.181 en test (calibración ayudó)
- ⚠️ Necesita mejor calibración para alcanzar ≤ 0.12

**Causa Principal:**
- Desbalance de clases (3.8:1)
- Probabilidades predichas no están bien calibradas
- SMOTE puede estar introduciendo ruido

**Mejoras para alcanzar 6 pts:**
1. **Probar calibración isotónica** en lugar de sigmoid:
   ```python
   calibrated = CalibratedClassifierCV(best_model, method='isotonic', cv=5)
   ```
2. **Ajustar probabilidades manualmente** con Platt scaling
3. **Usar ensemble más diverso** (StackingClassifier)
4. **Aplicar threshold moving** en lugar de SMOTE
5. **Aumentar CV folds** en calibración (cv=5 o cv=10)

---

#### A3. Validación & Anti-fuga: 4/6 puntos ⚠️

**Puntuación:**
- 6 pts: Split correcto + sin fuga ❌
- **4 pts: Dudas menores en implementación** ← **OBTENIDO**
- 2 pts: Errores de fuga o validación ❌

**Anti-fuga: PERFECTO ✅**
- ✅ Columnas BP excluidas correctamente
- ✅ Forbidden prefixes aplicados
- ✅ Label usa BPXO*, features NO tienen BP

**Validación Temporal: LIMITADA ⚠️**
- ⚠️ Solo un ciclo en datos (SDDSRVYR=66.0)
- ⚠️ Sistema cayó en fallback: split estratificado 80/20
- ✅ El código es correcto, pero los datos limitan la validación temporal

**Nota del sistema:**
```
⚠️ Split temporal no disponible/insuficiente. Usando split estratificado 80/20.
```

**Para alcanzar 6 pts:**
- Obtener datos de múltiples ciclos NHANES (2015-2016 + 2017-2020)
- Implementar split temporal verdadero

---

#### A4. Explicabilidad: 0/6 puntos ❌

**Estado:** NO IMPLEMENTADO

**Impacto:**
- ❌ Pérdida de 6 puntos completos
- ❌ Bloquea requisito de API: `/predict` debe retornar `drivers`
- ❌ Falta componente crítico para explicabilidad del modelo

**Solución:** Ver `ACTION_CHECKLIST.md` punto #1

---

## 📈 RENDIMIENTO DEL MODELO

### Cross-Validation (5-fold con SMOTE)

**LogisticRegression (Mejor modelo):**
```
Fold 1: AUROC=0.705 | Brier=0.209 | F1=0.436
Fold 2: AUROC=0.745 | Brier=0.213 | F1=0.481
Fold 3: AUROC=0.726 | Brier=0.212 | F1=0.434
Fold 4: AUROC=0.699 | Brier=0.221 | F1=0.425
Fold 5: AUROC=0.748 | Brier=0.206 | F1=0.485

Media: AUROC=0.724 ±0.020 | Brier=0.212 | F1=0.452
```

**RandomForest:**
```
Fold 1: AUROC=0.658 | Brier=0.189 | F1=0.362
Fold 2: AUROC=0.670 | Brier=0.190 | F1=0.352
Fold 3: AUROC=0.696 | Brier=0.182 | F1=0.398
Fold 4: AUROC=0.641 | Brier=0.199 | F1=0.328
Fold 5: AUROC=0.708 | Brier=0.174 | F1=0.396

Media: AUROC=0.675 | Brier=0.187 | F1=0.367
```

**Observación:** RandomForest tiene mejor Brier en CV pero peor AUROC que LogReg.

---

### Test Set - Classification Report

```
              precision    recall  f1-score   support

       NoHTA       0.89      0.74      0.80       473
         HTA       0.39      0.65      0.49       125

    accuracy                           0.72       598
   macro avg       0.64      0.69      0.65       598
weighted avg       0.78      0.72      0.74       598
```

**Análisis:**
- ✅ **Recall HTA = 0.648** → Buena detección de casos positivos
- ⚠️ **Precision HTA = 0.393** → Muchos falsos positivos
- ✅ **Especificidad NoHTA = 0.74** → Razonable para clase mayoritaria
- ⚠️ **F1-score HTA = 0.49** → Balance entre precision/recall mejorable

**Trade-off:**
El modelo prioriza recall sobre precision (detecta más casos de HTA a costa de falsos positivos). Esto es apropiado para un sistema de screening preventivo.

---

## 🎯 COMPARACIÓN CON OBJETIVOS

| Métrica | Objetivo Desafío | Obtenido | Gap | Status |
|---------|------------------|----------|-----|--------|
| AUROC | ≥ 0.80 (12 pts) | 0.752 | -0.048 | ⚠️ Cerca |
| Brier | ≤ 0.12 (6 pts) | 0.181 | +0.061 | ❌ Lejos |
| Anti-fuga | Implementado | ✅ | - | ✅ OK |
| Validación temporal | Multi-ciclo | Estratificado | - | ⚠️ Limitado |
| Explicabilidad | SHAP required | ❌ | - | ❌ Falta |
| Fairness | Subgrupos | ❌ | - | ❌ Falta |

---

## 🔥 ACCIONES PRIORITARIAS

### 1. Mejorar Brier Score (CRÍTICO) → +5 pts potenciales

**Objetivo:** Bajar de 0.181 a ≤ 0.12

**Estrategias:**

```python
# Estrategia 1: Calibración isotónica (mejor que sigmoid para pequeños datasets)
calibrated = CalibratedClassifierCV(best_model, method='isotonic', cv=5)
calibrated.fit(X_train_full, y_train_full)

# Estrategia 2: Ensemble con calibración por modelo
from sklearn.ensemble import StackingClassifier
stacker = StackingClassifier(
    estimators=[('lr', log_reg), ('rf', rf)],
    final_estimator=LogisticRegression(class_weight='balanced'),
    cv=5
)
calibrated_stack = CalibratedClassifierCV(stacker, method='isotonic', cv=5)

# Estrategia 3: Post-processing de probabilidades
from sklearn.calibration import calibration_curve
def recalibrate_probs(y_true, y_prob, n_bins=10):
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)
    # Crear lookup table para corrección
    ...
```

**Tiempo estimado:** 60-90 minutos

---

### 2. Implementar SHAP (CRÍTICO) → +6 pts

**Ver:** `ACTION_CHECKLIST.md` #1

**Tiempo estimado:** 30 minutos

---

### 3. Mejorar AUROC (IMPORTANTE) → +2 pts potenciales

**Objetivo:** Pasar de 0.752 a ≥ 0.80

**Estrategias:**

```python
# Feature engineering adicional
work['edad_al_cuadrado'] = work['edad'] ** 2
work['imc_cintura_interaccion'] = work['imc'] * work['rel_cintura_altura']
work['presion_estimada'] = (work['edad'] * 0.5 + work['imc'] * 2) / 100  # proxy feature

# Probar XGBoost con tuning
from xgboost import XGBClassifier
xgb = XGBClassifier(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=3.8,  # ratio de desbalance
    random_state=42
)

# Ensemble más sofisticado
from sklearn.ensemble import VotingClassifier
voting = VotingClassifier(
    estimators=[('lr', log_reg), ('rf', rf), ('xgb', xgb)],
    voting='soft',
    weights=[0.4, 0.3, 0.3]
)
```

**Tiempo estimado:** 90-120 minutos

---

## 📉 ANÁLISIS DE LIMITACIONES

### 1. Desbalance de Clases (3.8:1)

**Impacto:**
- Brier Score alto (modelo sobreconfiado en clase mayoritaria)
- Precision baja en clase minoritaria (HTA)

**Mitigación Actual:**
- ✅ SMOTE aplicado
- ✅ class_weight='balanced'

**Mejoras Posibles:**
- Threshold moving (cambiar umbral de 0.5 a valor óptimo)
- Focal Loss para penalizar más errores en clase minoritaria
- Cost-sensitive learning

---

### 2. Un Solo Ciclo de Datos

**Impacto:**
- Validación temporal no funcional
- Menos datos de entrenamiento (solo 2017-2020)
- Posible overfitting a un período específico

**Solución:**
- Descargar ciclos 2015-2016, 2013-2014, etc.
- Re-entrenar con más datos
- Implementar split temporal verdadero

---

### 3. Falta de Explicabilidad

**Impacto:**
- 0 puntos en A4
- No cumple requisito de API
- Falta transparencia del modelo

**Solución:**
- Implementar SHAP (30 minutos)

---

## ✅ FORTALEZAS DEL MODELO

1. **Anti-leakage perfecto:** Ninguna variable BP en features
2. **Reproducibilidad total:** Seeds fijos en todo el código
3. **Recall aceptable:** 64.8% de casos HTA detectados
4. **Ensemble robusto:** Combina LogReg + RF
5. **Calibración implementada:** CalibratedClassifierCV reduce Brier de 0.212 a 0.181
6. **SMOTE sin leakage:** Aplicado dentro de pipeline por fold
7. **Código limpio:** Bien documentado y organizado

---

## 📊 RESUMEN EJECUTIVO

**Puntuación Actual:** 15/30 pts (50%) en Rigor Técnico ML

**Fortalezas:**
- ✅ AUROC competitivo (0.752)
- ✅ Anti-leakage ejemplar
- ✅ Reproducibilidad completa

**Debilidades Críticas:**
- ❌ Brier Score alto (0.181 vs objetivo 0.12)
- ❌ Sin SHAP/explicabilidad
- ⚠️ Validación temporal limitada por datos

**Potencial de Mejora:**
- Con calibración mejorada: +5 pts (Brier ≤ 0.12)
- Con SHAP: +6 pts
- Con AUROC ≥ 0.80: +2 pts
- **Total alcanzable: 28/30 pts** con 4-6 horas de trabajo

---

## 🎯 PLAN DE ACCIÓN INMEDIATO

### Prioridad 1 (90 minutos):
1. [ ] Implementar SHAP (30 min) → +6 pts
2. [ ] Probar calibración isotónica (30 min) → potencial +3-5 pts
3. [ ] Añadir fairness analysis (30 min) → compliance

### Prioridad 2 (90 minutos):
4. [ ] Feature engineering adicional (30 min)
5. [ ] Probar XGBoost (30 min) → potencial +2 pts
6. [ ] Documentar resultados (30 min)

**Tiempo Total:** 3 horas  
**Mejora Esperada:** 15 → 24-28 pts (+60-87% de mejora)

---

**Generado:** Noviembre 7, 2025  
**Basado en:** Ejecución real del notebook  
**Siguiente Paso:** Ejecutar acciones prioritarias del checklist

