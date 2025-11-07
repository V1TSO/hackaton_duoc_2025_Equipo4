# Progreso Versión V

## Descarga y Preparación de Datos
- Conversión y combinación del ciclo 2015-2016 (train) y 2017-2018 (test) mediante `descargar_nhanes.py` y `prepare_nhanes_cycle.py`.
- Política actual: no se utilizan ciclos anteriores a 2015.
- Se agregó fallback temporal (split 80/20 del ciclo 2017-2018) para ejecutar notebooks mientras se completa la descarga de 2015-2016.

## Notebook `GUIA_HACKATHON_SALUD_NHANES_3.ipynb`
- Corrección del `NameError` incorporando `CYCLE_TO_LETTER` y constantes `TRAINING_CYCLES`/`TEST_CYCLES`.
- Limpieza sistemática (`clean_nhanes_data`) y validaciones anti-leak (lectura de `LAB_*` sólo para labels).
- Etiqueta de diabetes (`create_diabetes_label`) alineada con ADA 2024: HbA1c ≥ 6.0% o glucosa ≥ 110 mg/dL.
- Ingeniería de features ampliada: IMC, cintura/altura, obesidad central, puntaje de estilo de vida, métricas de sedentarismo e interacciones clave.
- Flujo ML completo: Logistic Regression baseline y XGBoost explicable (early stopping, `scale_pos_weight`).
- SHAP: resumen global + drivers locales, guardado en `reports/shap_feature_importance.csv` y `reports/shap_example_drivers.csv`.
- Calibración isotónica si Brier > 0.12 (con curvas de calibración exportadas).
- Fairness: reporte por sexo, edad y etnia con brecha AUROC; resultados en `reports/fairness_analysis.csv`.
- Reporte técnico auto-generado (`reports/technical_report.md`).
- Bitácora de prompts (`reports/prompt_log.json`).
- Checklist previo al despliegue para verificar métricas, artefactos y anti-leakage.

## Sistema RAG y LLM
- Creación de `kb/diabetes_prevention.md` con estrategias ADA/DPP.
- `SimpleRAG` con BM25 para búsquedas sobre la KB local.
- `generate_personalized_plan_with_shap`: prioriza áreas según drivers SHAP, construye contexto RAG y aplica guardrails.
- Documentación de los prompts (extractor y coach) con modelos, temperatura y restricciones.

## API (`ml/api_main.py`)
- Reemplazo por versión final: ingeniería de features de inferencia alineada al entrenamiento, explicaciones SHAP locales y descripciones legibles.
- Umbral de derivación configurado en 70% con recomendación médica cuando se supera.

## App Streamlit (`ml/app_streamlit.py`)
- Interfaz rediseñada para mostrar tabla + gráfico Altair de impactos SHAP.
- Mantiene flujo de llamada a `/predict` y placeholder para `/coach` (coordinado con equipo API/front).

## Artefactos Generados
- Modelos: `model_xgboost.pkl`, `imputer.pkl`, `feature_names.pkl`.
- Reportes en `reports/`: métricas SHAP, fairness, explicación local, reporte técnico, bitácora de prompts.

## Pendientes Manuales
- Verificar que los módulos laboratoriales 2015-2016 (`GHB_I.xpt`, `GLU_I.xpt`, `INS_I.xpt`, `HSCRP_I.xpt`) estén descargados, convertidos y disponibles como CSV en `./data/`.
- Integración final de `/coach` en la API y Frontend (depende del equipo correspondiente).
