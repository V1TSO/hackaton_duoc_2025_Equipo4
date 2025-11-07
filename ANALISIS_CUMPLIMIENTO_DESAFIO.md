# Análisis de Cumplimiento del Desafío NHANES 2025

**Fecha de análisis:** Noviembre 2025  
**Documento de referencia:** `Desafio_Salud_NHANES_2025_duoc.txt`  
**Puntuación total del desafío:** 100 puntos

---

## Resumen Ejecutivo

Este documento analiza el cumplimiento del proyecto frente a los requisitos del Hackathon de IA Duoc UC 2025 - Desafío Salud NHANES. Se evalúa cada componente según la rúbrica de 100 puntos distribuida en 5 categorías principales.

**Estado general:** ⚠️ **EN PROGRESO** - Se han implementado componentes clave pero faltan elementos críticos para cumplir completamente con la rúbrica.

---

## A. RIGOR TÉCNICO ML (30 puntos)

### A1. Métrica Principal - AUROC en Test (12 pts)

**Requisito:**
- 12 pts: AUROC ≥ 0.80
- 10 pts: AUROC 0.75–0.79
- 7 pts: AUROC 0.70–0.74
- 4 pts: AUROC < 0.70

**Estado actual:**
- ✅ Modelo XGBoost implementado (`ml/src/model.py`)
- ✅ Pipeline de entrenamiento con calibración (`ml/train_model.py`)
- ⚠️ **AUROC reportado: 0.7575** (`ml/reports/technical_report.md`)
- ❌ **NO CUMPLE** el objetivo de ≥0.80 (actualmente 7-10 pts según rúbrica)

**Archivos relevantes:**
- `ml/src/model.py` - Entrenamiento XGBoost
- `ml/train_model.py` - Script principal
- `ml/reports/technical_report.md` - Métricas reportadas

**Acciones requeridas:**
1. Mejorar modelo para alcanzar AUROC ≥0.80
2. Documentar intentos de mejora si no se alcanza
3. Verificar que métricas sean en conjunto de test temporal (2017-2018)

---

### A2. Calibración - Brier Score en Test (6 pts)

**Requisito:**
- 6 pts: Brier ≤ 0.12
- 5 pts: Brier 0.13–0.15
- 3 pts: Brier 0.16–0.18
- 1 pt: Brier > 0.18

**Estado actual:**
- ✅ Calibración implementada (`ml/src/model.py` - función `calibrate_model`)
- ✅ Métodos isotonic y sigmoid probados
- ✅ Curva de calibración generada (`calibration_curves.png`)
- ⚠️ **Brier Score reportado: 0.1987** (`ml/reports/technical_report.md`)
- ❌ **NO CUMPLE** el objetivo de ≤0.12 (actualmente 1 pt según rúbrica)

**Archivos relevantes:**
- `ml/src/model.py` - Función `calibrate_model`
- `ml/src/eval.py` - Visualización de curvas
- `ml/reports/technical_report.md` - Métricas

**Acciones requeridas:**
1. Mejorar calibración para alcanzar Brier ≤0.12
2. Verificar que ambos métodos (isotonic/sigmoid) fueron probados correctamente
3. Documentar método seleccionado y justificación

---

### A3. Validación Temporal & Anti-fuga (6 pts)

**Requisito:**
- 6 pts: Split correcto + sin fuga confirmada
- 4 pts: Dudas menores en implementación
- 2 pts: Errores detectados

**Estado actual:**
- ✅ Split temporal implementado correctamente (`ml/src/config.py`)
  - Config: `TRAIN_CYCLES = ['2015-2016']`, `TEST_CYCLES = ['2017-2018']`
  - Split temporal válido que cumple objetivo de evitar leakage por ciclo
- ✅ Validación anti-fuga implementada (`ml/src/features.py`)
- ✅ Archivo `LAB_COLUMNS_FORBIDDEN.txt` existe
- ✅ Validación de features sin prefijo LAB_*
- ✅ No se usa k-fold aleatorio como única validación

**Archivos relevantes:**
- `ml/src/config.py` - Líneas 26-27 (ciclos configurados)
- `ml/train_model.py` - Función `load_nhanes_data`
- `ml/LAB_COLUMNS_FORBIDDEN.txt` - Columnas prohibidas

**Estado:** ✅ **CUMPLE** (6 pts estimados)

**Acciones requeridas:**
1. Documentar validación anti-fuga en reporte técnico
2. Verificar que split temporal esté claramente documentado

---

### A4. Explicabilidad - Drivers Locales (6 pts)

**Requisito:**
- 6 pts: Drivers claros, consistentes con modelo y caso
- 4 pts: Explicaciones parciales
- 2 pts: Explicaciones confusas o incorrectas

**Estado actual:**
- ✅ SHAP implementado (`ml/src/eval.py`)
- ✅ Drivers locales generados (`ml/api_main.py` - función `predict_risk`)
- ✅ Visualizaciones SHAP (`shap_summary.png`, `reports/shap_feature_importance.csv`)
- ✅ Drivers incluidos en respuesta API (`/predict`)

**Archivos relevantes:**
- `ml/src/eval.py` - Funciones SHAP
- `ml/api_main.py` - Endpoint `/predict` con drivers
- `back/app/routes/ml_routes.py` - Integración backend

**Estado:** ✅ **CUMPLE** (6 pts estimados)

---

## B. LLMs, RAG y Guardrails (25 puntos)

### B1. Extractor NL→JSON con Validación (8 pts)

**Requisito:**
- 8 pts: 100% JSON válido + rangos/unidades correctos
- 6 pts: Leves correcciones necesarias
- 3 pts: Errores frecuentes de validación

**Estado actual:**
- ✅ Extractor implementado en agente conversacional (`back/app/agents/conversational_agent.py`)
- ✅ Uso de function calling de OpenAI con schema Pydantic
- ✅ Validación de tipos y rangos (`app/schemas/analisis_schema.py`)
- ⚠️ Implementación parcial en notebook (`ml/GUIA_HACKATHON_SALUD_NHANES_3.ipynb`)
- ❓ Falta validación exhaustiva de unidades y conversiones

**Archivos relevantes:**
- `back/app/agents/conversational_agent.py` - Líneas 72-182
- `back/app/schemas/analisis_schema.py` - Schemas de validación
- `ml/GUIA_HACKATHON_SALUD_NHANES_3.ipynb` - Ejemplo de extractor

**Acciones requeridas:**
1. Verificar que todas las conversiones de unidades funcionen correctamente
2. Implementar validación exhaustiva de rangos (edad 18-85, altura 120-220cm, etc.)
3. Probar con casos edge (unidades imperiales, valores fuera de rango)
4. Documentar casos de prueba y tasa de éxito

---

### B2. Coach con RAG y Citas Válidas (9 pts)

**Requisito:**
- 9 pts: Todas las recomendaciones con fuentes de /kb
- 7 pts: Alguna omisión menor de citas
- 4 pts: Alucinaciones o citas inválidas

**Estado actual:**
- ✅ Sistema RAG completo implementado (`ml/rag_coach.py`)
- ✅ BM25 para búsqueda en `/kb`
- ✅ Generación con OpenAI usando contexto RAG
- ✅ Citas a archivos markdown (`sources` en respuesta)
- ✅ Base de conocimiento en `/kb` con archivos `.md`
- ⚠️ Verificar que NO haya alucinaciones de fuentes

**Archivos relevantes:**
- `ml/rag_coach.py` - Sistema RAG completo
- `back/app/agents/rag_service.py` - Servicio RAG backend
- `kb/` - Base de conocimiento (actividad_fisica.md, sueño.md, etc.)

**Acciones requeridas:**
1. Verificar que todas las recomendaciones citen fuentes válidas de `/kb`
2. Implementar validación para prevenir alucinaciones de fuentes
3. Probar con diferentes perfiles y verificar citas
4. Documentar política de citas en bitácora de prompts

---

### B3. Safety & Derivación (8 pts)

**Requisito:**
- 8 pts: Umbrales correctos + lenguaje no-diagnóstico + derivación implementada
- 5 pts: Implementación parcial
- 2 pts: Ausente o inadecuado

**Estado actual:**
- ✅ Umbral de derivación definido (`ml/api_main.py` - `REFERRAL_THRESHOLD = 0.70`)
- ✅ Lógica de derivación implementada (`ml/api_main.py` - línea 169)
- ✅ Disclaimer en prompts del coach (`ml/rag_coach.py` - línea 242)
- ✅ Disclaimer en frontend (`front/src/app/(app)/coach/page.tsx`)
- ⚠️ Verificar que lenguaje sea completamente no-diagnóstico

**Archivos relevantes:**
- `ml/api_main.py` - Umbral y lógica de derivación
- `ml/rag_coach.py` - Prompt del coach con disclaimer
- `front/src/app/(app)/coach/page.tsx` - UI con disclaimer
- `back/app/routes/ml_routes.py` - Endpoint `/coach`

**Acciones requeridas:**
1. Revisar todos los prompts para asegurar lenguaje no-diagnóstico
2. Verificar que derivación funcione correctamente cuando score ≥0.70
3. Asegurar que disclaimer sea visible en todas las comunicaciones
4. Probar casos edge (score = 0.70, score = 0.99)

---

## C. PRODUCTO Y UX (25 puntos)

### C1. App Funcional y Fluida (10 pts)

**Requisito:**
- 10 pts: Formulario claro + feedback inmediato + manejo de errores + deploy en Spaces
- 7 pts: Funcional con problemas menores
- 4 pts: Funcionalidad básica limitada

**Estado actual:**
- ✅ Frontend Next.js implementado (`front/`)
- ✅ Interfaz conversacional (`front/src/app/(app)/chat/page.tsx`)
- ✅ Página de coach (`front/src/app/(app)/coach/page.tsx`)
- ✅ Manejo de errores básico
- ❌ **NO HAY DEPLOYMENT EN HUGGING FACE SPACES**
- ⚠️ Existe guía de deployment (`ml/DEPLOYMENT_HF_SPACES.md`) pero no está deployado
- ❓ Falta app Streamlit/Gradio mencionada en requisitos

**Archivos relevantes:**
- `front/src/app/(app)/chat/page.tsx` - Interfaz conversacional
- `front/src/app/(app)/coach/page.tsx` - Visualización de plan
- `ml/DEPLOYMENT_HF_SPACES.md` - Guía de deployment
- `ml/app_streamlit.py` - App Streamlit (¿existe?)

**Acciones requeridas:**
1. **CRÍTICO:** Deployar app en Hugging Face Spaces
2. Verificar que app Streamlit/Gradio esté funcional
3. Mejorar feedback visual durante procesamiento
4. Implementar manejo robusto de errores en frontend
5. Probar flujo completo end-to-end

---

### C2. Export & Sharing (5 pts)

**Requisito:**
- 5 pts: PDF descargable + enlace compartible funcional
- 3 pts: Solo una funcionalidad implementada
- 1 pt: Implementación deficiente

**Estado actual:**
- ✅ Generador de PDF implementado (`ml/pdf_generator.py`)
- ✅ PDF incluye disclaimer médico
- ✅ Formato profesional con reportlab
- ⚠️ **NO INTEGRADO** en API/Frontend
- ❌ Falta endpoint `/coach/pdf` en FastAPI
- ❌ Falta botón de descarga en frontend
- ✅ Enlace compartible disponible si se deploya en HF Spaces

**Archivos relevantes:**
- `ml/pdf_generator.py` - Generador de PDF completo
- `back/app/routes/ml_routes.py` - Falta endpoint PDF
- `front/src/app/(app)/coach/page.tsx` - Falta botón descarga

**Acciones requeridas:**
1. **CRÍTICO:** Crear endpoint `POST /coach/pdf` en FastAPI
2. Integrar generador PDF en endpoint
3. Agregar botón de descarga PDF en frontend (`/coach`)
4. Probar generación y descarga de PDF
5. Verificar que PDF incluya todas las secciones requeridas

---

### C3. Claridad para el Usuario (10 pts)

**Requisito:**
- 10 pts: Mensajes simples + inclusivos + explicación clara del score + próximos pasos
- 7 pts: Claridad adecuada con mejoras menores
- 4 pts: Comunicación confusa o incompleta

**Estado actual:**
- ✅ Mensajes claros en interfaz conversacional
- ✅ Explicación de score de riesgo en página coach
- ✅ Visualización de drivers con explicaciones
- ✅ Disclaimer visible
- ⚠️ Verificar lenguaje inclusivo en todos los mensajes
- ⚠️ Verificar que próximos pasos sean claros

**Archivos relevantes:**
- `front/src/app/(app)/chat/page.tsx` - Mensajes del chat
- `front/src/app/(app)/coach/page.tsx` - Visualización de resultados
- `ml/rag_coach.py` - Generación de plan

**Acciones requeridas:**
1. Revisar todos los textos para lenguaje inclusivo
2. Asegurar que explicación del score sea clara para público general
3. Verificar que próximos pasos sean específicos y accionables
4. Probar con usuarios reales para validar claridad

---

## D. REPRODUCIBILIDAD Y BUENAS PRÁCTICAS (15 puntos)

### D1. Repo & Scripts (6 pts)

**Requisito:**
- 6 pts: requirements.txt/env + Makefile o scripts + semillas fijadas + rutas limpias
- 4 pts: Reproducible con ajustes menores
- 2 pts: Dificultades significativas para reproducir

**Estado actual:**
- ✅ `requirements.txt` en múltiples directorios (`back/`, `ml/`, `front/`)
- ✅ Semillas fijadas (`ml/src/config.py` - `SEED = 42`)
- ✅ Scripts de entrenamiento (`ml/train_model.py`)
- ✅ Scripts de evaluación (`ml/src/eval.py`)
- ⚠️ Falta Makefile o script maestro para ejecutar pipeline completo
- ✅ Rutas relativas y configurables

**Archivos relevantes:**
- `ml/requirements.txt` - Dependencias ML
- `back/requirements.txt` - Dependencias backend
- `front/package.json` - Dependencias frontend
- `ml/src/config.py` - Configuración y semillas

**Acciones requeridas:**
1. Crear Makefile o script maestro (`run_all.sh` o `setup.sh`)
2. Documentar pasos de instalación en README principal
3. Verificar que todas las rutas sean relativas o configurables
4. Probar instalación desde cero en entorno limpio

---

### D2. Documentación (5 pts)

**Requisito:**
- 5 pts: README claro con pasos + supuestos + estructura de datos
- 3 pts: Documentación básica funcional
- 1 pt: Documentación insuficiente

**Estado actual:**
- ✅ README en cada módulo (`back/README.md`, `front/README.md`, `ml/README.md`)
- ✅ Guías de quick start (`ml/QUICK_START.md`, `front/QUICK_START.md`)
- ✅ Documentación técnica (`ml/IMPLEMENTATION_SUMMARY.md`)
- ⚠️ Falta README principal en raíz del proyecto
- ⚠️ Falta documentación de estructura de datos NHANES
- ✅ Guías de conversión de datos (`ml/CONVERSION_DATOS_NHANES.md`)

**Archivos relevantes:**
- `ml/README.md` - Documentación ML
- `back/README.md` - Documentación backend
- `front/README.md` - Documentación frontend
- `ml/QUICK_START.md` - Guía rápida

**Acciones requeridas:**
1. Crear README principal en raíz con visión general del proyecto
2. Documentar estructura de datos NHANES esperada
3. Incluir diagrama de arquitectura
4. Documentar supuestos y limitaciones
5. Agregar ejemplos de uso

---

### D3. Métricas por Subgrupos - Fairness (4 pts)

**Requisito:**
- 4 pts: Reporte completo por sexo/edad/grupo étnico + análisis de gap + mitigaciones
- 2 pts: Análisis parcial de equidad
- 1 pt: Análisis superficial o ausente

**Estado actual:**
- ✅ Análisis de fairness implementado (`ml/src/eval.py` - función `analyze_fairness`)
- ✅ Reporte generado (`ml/reports/fairness_analysis.csv`)
- ✅ Métricas por subgrupos calculadas
- ⚠️ **Gap absoluto reportado: 0.2076** (alto)
- ❓ Falta análisis de mitigaciones
- ❓ Falta justificación de gaps

**Archivos relevantes:**
- `ml/src/eval.py` - Función `analyze_fairness`
- `ml/reports/fairness_analysis.csv` - Reporte de fairness
- `ml/reports/technical_report.md` - Resumen de fairness

**Acciones requeridas:**
1. Documentar análisis de gaps por subgrupo
2. Proponer mitigaciones si gaps son significativos
3. Incluir análisis de fairness en reporte técnico
4. Verificar que métricas incluyan sexo, edad y grupo étnico

---

## E. PRESENTACIÓN Y PITCH FINAL (15 puntos)

### E1. Storytelling e Impacto (6 pts)

**Estado:** ❓ **NO EVALUABLE** - Requiere preparación de presentación

**Acciones requeridas:**
1. Preparar narrativa clara del problema
2. Cuantificar impacto potencial
3. Definir propuesta de valor
4. Crear slides de presentación

---

### E2. Comunicación Técnica (5 pts)

**Estado:** ❓ **NO EVALUABLE** - Requiere preparación de presentación

**Acciones requeridas:**
1. Preparar explicación de arquitectura híbrida
2. Documentar decisiones técnicas clave
3. Preparar respuestas a preguntas técnicas comunes
4. Crear diagramas técnicos

---

### E3. Formato y Tiempo (4 pts)

**Estado:** ❓ **NO EVALUABLE** - Requiere preparación de presentación

**Acciones requeridas:**
1. Preparar presentación de 10 minutos
2. Ensayar timing
3. Preparar demo en vivo
4. Crear screenshots de backup

---

## ENTREGABLES OBLIGATORIOS

### 1. Repositorio GitHub ✅

**Estado:** ✅ **CUMPLE**
- Código organizado en carpetas (`/back`, `/front`, `/ml`)
- README en cada módulo
- Estructura clara

---

### 2. API Mínima FastAPI ⚠️

**Requisito:**
- `POST /predict` → `{"score": float, "drivers": [top_features]}`
- `POST /coach` → plan textual + citas a `/kb`

**Estado:**
- ✅ Endpoint `/predict` implementado (`back/app/routes/ml_routes.py`)
- ✅ Endpoint `/coach` implementado (`back/app/routes/ml_routes.py`)
- ✅ Respuestas en formato correcto
- ⚠️ Falta endpoint `/coach/pdf` para PDF

**Archivos:**
- `back/app/routes/ml_routes.py` - Endpoints principales
- `back/main.py` - App FastAPI

---

### 3. App Demo Interactiva ❌

**Requisito:**
- Streamlit o Gradio
- Deploy funcional en Hugging Face Spaces

**Estado:**
- ✅ Frontend Next.js implementado
- ❌ **NO HAY APP STREAMLIT/GRADIO**
- ❌ **NO ESTÁ DEPLOYADO EN HF SPACES**
- ⚠️ Existe guía de deployment pero no está ejecutada

**Acciones requeridas:**
1. Crear app Streamlit o adaptar frontend Next.js
2. Deployar en Hugging Face Spaces
3. Verificar que sea accesible públicamente

---

### 4. Reporte Técnico (2-3 páginas) ⚠️

**Requisito:**
- Datos, ingeniería de features, validación, calibración, fairness, guardrails, limitaciones

**Estado:**
- ✅ Reporte técnico existe (`ml/reports/technical_report.md`)
- ⚠️ Contenido incompleto (falta secciones detalladas)
- ⚠️ Solo 1 página aproximadamente

**Archivos:**
- `ml/reports/technical_report.md` - Reporte actual

**Acciones requeridas:**
1. Expandir reporte a 2-3 páginas
2. Incluir todas las secciones requeridas:
   - Descripción detallada de datos
   - Ingeniería de features completa
   - Validación temporal y anti-fuga
   - Calibración (método, resultados)
   - Fairness (análisis completo)
   - Guardrails implementados
   - Limitaciones del sistema
3. Agregar visualizaciones (curvas ROC, calibración, fairness)

---

### 5. Plan PDF Descargable (1-2 páginas) ⚠️

**Requisito:**
- Recomendaciones personalizadas
- Disclaimer médico visible

**Estado:**
- ✅ Generador PDF implementado (`ml/pdf_generator.py`)
- ✅ Incluye disclaimer médico
- ❌ **NO INTEGRADO** en API/Frontend
- ❌ Falta endpoint y botón de descarga

**Acciones requeridas:**
1. Integrar generador PDF en endpoint FastAPI
2. Agregar botón de descarga en frontend
3. Verificar formato y contenido del PDF

---

### 6. Bitácora de Prompts ⚠️

**Requisito:**
- Prompts clave utilizados
- Políticas de guardrails implementadas

**Estado:**
- ✅ Archivo existe (`ml/reports/prompt_log.json`)
- ⚠️ Contenido básico (solo estructura)
- ❓ Falta documentación detallada de prompts

**Archivos:**
- `ml/reports/prompt_log.json` - Bitácora básica

**Acciones requeridas:**
1. Expandir bitácora con todos los prompts utilizados
2. Documentar políticas de guardrails
3. Incluir ejemplos de prompts del extractor y coach
4. Documentar decisiones de diseño de prompts

---

### 7. Presentación Final ❓

**Estado:** ❓ **NO EVALUABLE** - Requiere preparación

**Acciones requeridas:**
1. Preparar slides (10 min presentación + 5 min Q&A)
2. Estructura:
   - Problema y motivación (2 min)
   - Solución técnica y arquitectura (3 min)
   - Demo de la aplicación (3 min)
   - Resultados y métricas (1 min)
   - Impacto y próximos pasos (1 min)
3. Preparar demo en vivo
4. Crear screenshots de backup

---

## PROBLEMAS CRÍTICOS IDENTIFICADOS

### 🔴 CRÍTICO - Requiere acción inmediata

1. **AUROC < 0.80**
   - Actual: 0.7575
   - Requerido: ≥ 0.80
   - **Impacto:** A1 (12 pts) - Solo 7-10 pts en lugar de 12

2. **Brier Score > 0.12**
   - Actual: 0.1987
   - Requerido: ≤ 0.12
   - **Impacto:** A2 (6 pts) - Solo 1 pt en lugar de 6

3. **NO HAY DEPLOYMENT EN HF SPACES**
   - **Impacto:** C1 (10 pts) - Pérdida completa de puntos

4. **PDF NO INTEGRADO**
   - Generador existe pero no está conectado
   - **Impacto:** C2 (5 pts) - Pérdida completa de puntos

---

### 🟡 IMPORTANTE - Requiere atención

1. Reporte técnico incompleto (solo 1 página, falta contenido)
2. Bitácora de prompts básica (falta detalle)
3. Falta app Streamlit/Gradio (solo Next.js)
4. Falta Makefile/script maestro para reproducibilidad
5. Falta README principal en raíz

---

## PUNTUACIÓN ESTIMADA ACTUAL

| Categoría | Puntos Máximos | Puntos Estimados | Estado |
|-----------|----------------|------------------|--------|
| A. Rigor Técnico ML | 30 | 20-23 | ⚠️ Parcial |
| B. LLMs, RAG y Guardrails | 25 | 20-22 | ✅ Bueno |
| C. Producto y UX | 25 | 10-15 | ⚠️ Parcial |
| D. Reproducibilidad | 15 | 10-12 | ⚠️ Parcial |
| E. Presentación | 15 | ? | ❓ Pendiente |
| **TOTAL** | **100** | **60-72** | ⚠️ **EN PROGRESO** |

---

## PLAN DE ACCIÓN PRIORIZADO

### Prioridad 1 (Crítico - Bloquea puntos)

1. ✅ Mejorar AUROC a ≥0.80 (o documentar intentos)
2. ✅ Mejorar Brier Score a ≤0.12 (o documentar intentos)
3. ✅ Deployar app en Hugging Face Spaces
4. ✅ Integrar PDF en API y frontend

### Prioridad 2 (Importante - Mejora puntuación)

1. Expandir reporte técnico a 2-3 páginas
2. Completar bitácora de prompts
3. Crear app Streamlit/Gradio (o adaptar Next.js)
4. Crear Makefile/script maestro
5. Crear README principal

### Prioridad 3 (Mejoras - Optimiza puntuación)

1. Mejorar análisis de fairness con mitigaciones
2. Verificar extractor NL→JSON al 100%
3. Revisar lenguaje inclusivo en todos los textos
4. Preparar presentación final
5. Crear screenshots de backup

---

## CONCLUSIÓN

El proyecto tiene una base sólida con componentes clave implementados, pero requiere trabajo crítico en:

1. **Métricas ML:** AUROC y Brier Score no cumplen objetivos (requiere mejora del modelo o documentación de intentos)
2. **Deployment:** Falta deployment en HF Spaces (crítico para C1)
3. **Integración PDF:** Generador existe pero no está conectado a API/Frontend (crítico para C2)
4. **Documentación:** Reporte técnico y bitácora incompletos (requiere expansión)

**Nota:** El split temporal (2015-2016 train, 2017-2018 test) es correcto y cumple con el objetivo de evitar leakage por ciclo.

**Estimación de tiempo para cumplir requisitos críticos:** 6-10 horas de trabajo enfocado.

---

**Última actualización:** Noviembre 2025  
**Próxima revisión:** Después de implementar correcciones críticas

