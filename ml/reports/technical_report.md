
# Reporte Técnico: Modelo de Riesgo Cardiometabólico

## 1. Datos y Split Temporal
- Ciclos de entrenamiento: 2015-2016
- Ciclos de test: 2017-2018
- Registros entrenamiento: 5,239
- Registros test: 4,954
- Prevalencia entrenamiento: 29.1%
- Prevalencia test: 32.3%

## 2. Ingeniería de Features
- Total de features usadas: 25
- Features destacadas: bmi_age_interaction, waist_height_ratio, waist_age_interaction, age, bmi_age_sex_interaction
- Estrategias: IMC, cintura/altura, indicadores de estilo de vida, interacciones BMI*edad
- Validación anti-fuga confirmada (sin columnas LAB_*)

## 3. Desempeño del Modelo (XGBoost)
- AUROC: 0.7575
- AUPRC: 0.5527
- Brier Score: 0.1987

## 4. Fairness
- Subgrupo con mejor AUROC: Race_Hispanic
- Subgrupo con menor AUROC: Age_60+
- Gap absoluto de AUROC: 0.2076

## 5. Explainability
- Método: SHAP (TreeExplainer)
- Drivers locales disponibles para cada predicción
- Viz global: reports/shap_feature_importance.csv

## 6. Guardrails y Ética
- Umbral de derivación médica: 70%
- Reglas anti-fuga y validación temporal implementadas
- Disclaimer visible en API y App

## 7. Limitaciones
- Validación externa aún pendiente
- Datos centrados en población NHANES EEUU
- Dependencia de API OpenAI para generación del plan

