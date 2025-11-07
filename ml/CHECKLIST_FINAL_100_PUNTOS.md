# ✅ Checklist Final de Cumplimiento - 100 Puntos
## Hackathon IA Duoc UC 2025 - Desafío Salud NHANES

**Fecha de Validación:** _Completar antes del 7 de noviembre 2025_

---

## A. RIGOR TÉCNICO ML (30 puntos)

### A1. Métrica Principal - AUROC en Test (12 pts)

**Umbral de Puntos:**
- 12 pts: AUROC ≥ 0.80
- 10 pts: AUROC 0.75–0.79
- 7 pts: AUROC 0.70–0.74
- 4 pts: AUROC < 0.70

**Checklist:**
- [ ] Notebook ejecutado completamente (célula 30: modelo XGBoost)
- [ ] AUROC medido en conjunto de test temporal (2017-2018)
- [ ] Valor documentado en: `reports/technical_report.md`
- [ ] **AUROC Logrado:** `_____` → **Puntos:** `___/12`

**Notas:**
- Si AUROC < 0.80: Documentar intentos de mejora realizados
- Verificar que no hay overfitting (comparar train vs test)

---

### A2. Calibración - Brier Score en Test (6 pts)

**Umbral de Puntos:**
- 6 pts: Brier ≤ 0.12
- 5 pts: Brier 0.13–0.15
- 3 pts: Brier 0.16–0.18
- 1 pt: Brier > 0.18

**Checklist:**
- [ ] Calibración aplicada (célula 33: isotónica o sigmoide)
- [ ] Curva de calibración generada: `calibration_curves.png` existe
- [ ] Brier Score medido en test
- [ ] **Brier Score Logrado:** `_____` → **Puntos:** `___/6`

**Notas:**
- Si Brier > 0.12: Verificar que ambos métodos (isotonic/sigmoid) fueron probados
- Documentar método de calibración seleccionado

---

### A3. Validación Temporal & Anti-fuga (6 pts)

**Umbral de Puntos:**
- 6 pts: Split correcto + sin fuga confirmada
- 4 pts: Dudas menores en implementación
- 2 pts: Errores detectados

**Checklist - Split Temporal:**
- [ ] Train usa ciclos 2015-2016 ÚNICAMENTE
- [ ] Test usa ciclos 2017-2018 ÚNICAMENTE
- [ ] NO se usó k-fold aleatorio como única validación
- [ ] Confirmado en célula 9 del notebook

**Checklist - Anti-fuga:**
- [ ] Archivo `LAB_COLUMNS_FORBIDDEN.txt` existe
- [ ] Ninguna feature en `feature_names.pkl` empieza con `LAB_`
- [ ] Validación anti-fuga pasada (célula 26)
- [ ] Label usa LAB pero features NO

**→ Puntos:** `___/6`

---

### A4. Explicabilidad - Drivers Locales (6 pts)

**Umbral de Puntos:**
- 6 pts: Drivers claros, consistentes con modelo y caso
- 4 pts: Explicaciones parciales
- 2 pts: Explicaciones confusas o incorrectas

**Checklist:**
- [ ] SHAP implementado (célula 31)
- [ ] `shap_summary.png` generado y guardado
- [ ] `reports/shap_feature_importance.csv` existe
- [ ] `reports/shap_example_drivers.csv` existe
- [ ] Top drivers tienen sentido (ej: IMC alto → aumenta riesgo)
- [ ] API endpoint `/predict` retorna drivers en response

**→ Puntos:** `___/6`

**TOTAL SECCIÓN A:** `___/30`

---

## B. LLMs, RAG y GUARDRAILS (25 puntos)

### B1. Extractor NL→JSON con Validación (8 pts)

**Umbral de Puntos:**
- 8 pts: 100% JSON válido + rangos/unidades correctos
- 6 pts: Leves correcciones necesarias
- 3 pts: Errores frecuentes de validación

**Checklist:**
- [ ] Notebook FASE 6 implementada (células ~2673-2812)
- [ ] JSON Schema de validación definido
- [ ] OpenAI function calling implementado
- [ ] Pruebas realizadas con casos de texto libre
- [ ] Conversión de unidades funciona (ej: pies a cm)
- [ ] Validación de rangos (edad 18-85, peso 30-220, etc.)

**Casos de Prueba:**
```
Entrada: "Tengo 45 años, mido 1.75m y peso 90 kilos"
Salida esperada: {age: 45, height_cm: 175, weight_kg: 90}
```

- [ ] Caso 1 probado: ✓/✗
- [ ] Caso 2 probado: ✓/✗
- [ ] Caso 3 probado: ✓/✗

**→ Puntos:** `___/8`

**Notas:** Si no implementado, explicar en entregables por qué fue omitido.

---

### B2. Coach con RAG y Citas Válidas (9 pts)

**Umbral de Puntos:**
- 9 pts: Todas las recomendaciones con fuentes de /kb
- 7 pts: Alguna omisión menor de citas
- 4 pts: Alucinaciones o citas inválidas

**Checklist - Base de Conocimiento:**
- [ ] Directorio `kb/` existe con archivos `.md`
- [ ] `kb/diabetes_prevention.md` existe y tiene contenido
- [ ] Al menos 3 documentos en `/kb`

**Checklist - RAG:**
- [ ] Archivo `rag_coach.py` implementado
- [ ] BM25 o embeddings implementados para búsqueda
- [ ] Sistema recupera chunks relevantes
- [ ] Prompt incluye contexto recuperado

**Checklist - Generación:**
- [ ] OpenAI API key configurada (variable entorno o secret)
- [ ] Planes generados tienen estructura SMART
- [ ] TODAS las recomendaciones citan fuentes (ej: "según diabetes_prevention.md")
- [ ] NO hay alucinaciones (información inventada sin fuente)

**Checklist - Integración:**
- [ ] API endpoint `/coach` usa sistema RAG real
- [ ] `api_main.py` importa `rag_coach.py`
- [ ] Response incluye campo `sources` con lista de archivos citados

**Test Manual:**
- [ ] Generar plan para perfil de prueba
- [ ] Verificar que CADA recomendación menciona fuente
- [ ] Verificar que fuentes existen en `/kb`

**→ Puntos:** `___/9`

---

### B3. Safety & Derivación (8 pts)

**Umbral de Puntos:**
- 8 pts: Umbrales correctos + lenguaje no-diagnóstico + derivación implementada
- 5 pts: Implementación parcial
- 2 pts: Ausente o inadecuado

**Checklist - Umbrales:**
- [ ] `REFERRAL_THRESHOLD` definido (recomendado: 0.70)
- [ ] Umbral aplicado en API endpoint `/predict`
- [ ] Mensaje de derivación claro cuando riesgo > umbral

**Checklist - Lenguaje:**
- [ ] Disclaimer visible en:
  - [ ] API response
  - [ ] App Streamlit (pantalla principal)
  - [ ] PDF generado
  - [ ] Plan del coach
- [ ] Lenguaje es NO-diagnóstico (evita: "tienes diabetes", "estás enfermo")
- [ ] Lenguaje es claro y accesible (sin jerga médica excesiva)
- [ ] Lenguaje es inclusivo (no asume género, edad, etc.)

**Checklist - Derivación:**
- [ ] Sistema recomienda consulta médica cuando riesgo alto
- [ ] Texto específico: "Consulta con un profesional de salud"
- [ ] No reemplaza atención médica profesional

**→ Puntos:** `___/8`

**TOTAL SECCIÓN B:** `___/25`

---

## C. PRODUCTO Y UX (25 puntos)

### C1. App Funcional y Fluida (10 pts)

**Umbral de Puntos:**
- 10 pts: Formulario claro + feedback inmediato + manejo errores + deploy en Spaces
- 7 pts: Funcional con problemas menores
- 4 pts: Funcionalidad básica limitada

**Checklist - Formulario:**
- [ ] `app_streamlit.py` existe
- [ ] Formulario completo con todos los campos requeridos
- [ ] Validaciones de entrada (rangos correctos)
- [ ] UI clara y organizada (sidebar o similar)

**Checklist - Feedback:**
- [ ] Spinners durante cálculos ("Analizando tu perfil...")
- [ ] Resultados muestran score, nivel de riesgo, indicador visual
- [ ] Drivers mostrados en tabla y gráfico
- [ ] Mensajes de error claros si algo falla

**Checklist - Manejo de Errores:**
- [ ] Si API no responde: mensaje amigable
- [ ] Si datos inválidos: validación antes de enviar
- [ ] Try-except en lugares críticos

**Checklist - Deploy:**
- [ ] App deployada en Hugging Face Spaces (o similar)
- [ ] URL pública funcional
- [ ] Documentado en `DEPLOYMENT_HF_SPACES.md`

**→ Puntos:** `___/10`

---

### C2. Export & Sharing (5 pts)

**Umbral de Puntos:**
- 5 pts: PDF descargable + enlace compartible funcional
- 3 pts: Solo una funcionalidad implementada
- 1 pt: Implementación deficiente

**Checklist - PDF:**
- [ ] `pdf_generator.py` implementado
- [ ] Botón "Descargar PDF" funciona en app
- [ ] PDF incluye:
  - [ ] Perfil del usuario
  - [ ] Puntaje de riesgo
  - [ ] Drivers principales
  - [ ] Plan personalizado completo
  - [ ] Fuentes citadas
  - [ ] Disclaimer visible
- [ ] PDF formateado profesionalmente (no plain text)

**Checklist - Link Compartible (Opcional):**
- [ ] Sistema de sesiones implementado
- [ ] URL compartible generada
- [ ] Resultados persistidos temporalmente

**→ Puntos:** `___/5`

**Nota:** PDF es crítico (3 pts mínimo). Link compartible es nice-to-have (2 pts extra).

---

### C3. Claridad para el Usuario (10 pts)

**Umbral de Puntos:**
- 10 pts: Mensajes simples + inclusivos + explicación clara del score + próximos pasos
- 7 pts: Claridad adecuada con mejoras menores
- 4 pts: Comunicación confusa o incompleta

**Checklist:**
- [ ] Mensajes sin jerga técnica ("tu IMC es alto" vs "BMXWAIST > 102")
- [ ] Explicación clara del puntaje:
  - "Riesgo Alto (68%): esto significa que tu probabilidad de desarrollar diabetes es 68%"
- [ ] Drivers explicados en lenguaje natural:
  - ✓ "IMC elevado aumenta el riesgo"
  - ✗ "bmi_age_interaction: +0.75"
- [ ] Próximos pasos claros después de ver resultado
- [ ] Lenguaje inclusivo (no asume género en texto)
- [ ] Colores y visualizaciones intuitivas (rojo=alto, verde=bajo)

**→ Puntos:** `___/10`

**TOTAL SECCIÓN C:** `___/25`

---

## D. REPRODUCIBILIDAD Y BUENAS PRÁCTICAS (15 puntos)

### D1. Repositorio & Scripts (6 pts)

**Umbral de Puntos:**
- 6 pts: requirements.txt + scripts + semillas fijadas + rutas limpias
- 4 pts: Reproducible con ajustes menores
- 2 pts: Dificultades significativas

**Checklist:**
- [ ] `requirements.txt` actualizado con todas las dependencias
- [ ] Versiones específicas en requirements (>=, ==)
- [ ] Archivos `.pkl` (modelos) están en repositorio o instrucciones para generarlos
- [ ] Seeds fijados:
  - [ ] `np.random.seed(42)` en notebook
  - [ ] `random_state=42` en modelos
- [ ] Rutas relativas (no hardcoded como `/Users/miusuario/...`)
- [ ] Scripts ejecutables:
  - [ ] `python rag_coach.py` (test)
  - [ ] `python pdf_generator.py` (test)
  - [ ] `python api_main.py` (lanza API)
  - [ ] `streamlit run app_streamlit.py` (lanza app)

**Test de Reproducibilidad:**
```bash
# En un entorno limpio
pip install -r requirements.txt
python test_entorno.py  # Si existe
```

- [ ] Test pasado sin errores

**→ Puntos:** `___/6`

---

### D2. Documentación (5 pts)

**Umbral de Puntos:**
- 5 pts: README claro con pasos + supuestos + estructura
- 3 pts: Documentación básica funcional
- 1 pt: Documentación insuficiente

**Checklist:**
- [ ] `README.md` principal existe
- [ ] README incluye:
  - [ ] Descripción del proyecto
  - [ ] Instrucciones de instalación paso a paso
  - [ ] Instrucciones de uso (cómo correr notebook, API, app)
  - [ ] Estructura de carpetas explicada
  - [ ] Requisitos del sistema
  - [ ] Links a demo y documentación adicional
- [ ] `QUICK_START.md` o similar existe
- [ ] `DEPLOYMENT_HF_SPACES.md` existe (guía de deployment)
- [ ] Comentarios en código crítico (no excesivos, pero útiles)
- [ ] Docstrings en funciones clave

**→ Puntos:** `___/5`

---

### D3. Métricas por Subgrupos - Fairness (4 pts)

**Umbral de Puntos:**
- 4 pts: Reporte completo por sexo/edad/etnia + análisis gap + mitigaciones
- 2 pts: Análisis parcial
- 1 pt: Análisis superficial o ausente

**Checklist:**
- [ ] `reports/fairness_analysis.csv` existe
- [ ] Análisis incluye subgrupos:
  - [ ] Sexo: M / F
  - [ ] Edad: 18-44, 45-59, 60+
  - [ ] Etnia (RIDRETH3): Mexican, Hispanic, White, Black, Asian, Other
- [ ] Métricas por subgrupo:
  - [ ] n (tamaño muestra)
  - [ ] Prevalencia
  - [ ] AUROC
  - [ ] Brier Score
- [ ] Gap absoluto calculado:
  - [ ] `AUROC_gap = AUROC_max - AUROC_min`
  - [ ] Documentado en technical_report.md
- [ ] Si gap ≥ 0.05: Mitigaciones propuestas o justificación

**→ Puntos:** `___/4`

**TOTAL SECCIÓN D:** `___/15`

---

## E. PRESENTACIÓN Y PITCH FINAL (15 puntos)

### E1. Storytelling e Impacto (6 pts)

**Umbral de Puntos:**
- 6 pts: Narrativa clara + problema bien definido + impacto cuantificado + propuesta de valor convincente
- 4 pts: Storytelling adecuado con elementos menores faltantes
- 2 pts: Presentación confusa o impacto poco claro

**Checklist:**
- [ ] Presentación sigue estructura recomendada (ver PRESENTACION_ESTRUCTURA.md)
- [ ] Hook inicial impactante (estadística o pregunta)
- [ ] Problema claramente definido (1.5 min)
- [ ] Solución explicada con diagrama de arquitectura
- [ ] Casos de uso identificados
- [ ] Impacto cuantificado (ej: "puede reducir riesgo en 58%")
- [ ] Próximos pasos realistas

**→ Puntos:** `___/6`

---

### E2. Comunicación Técnica (5 pts)

**Umbral de Puntos:**
- 5 pts: Explica conceptos complejos accesiblemente + comprensión profunda + responde preguntas precisamente
- 3 pts: Comunicación técnica adecuada con algunas dificultades
- 1 pt: Dificultades significativas

**Checklist:**
- [ ] Métricas explicadas claramente (AUROC, Brier Score)
- [ ] Split temporal justificado (por qué es importante)
- [ ] RAG explicado sin jerga (o con definición clara)
- [ ] SHAP explicado como "explicabilidad del modelo"
- [ ] Equipo demuestra comprensión profunda en Q&A
- [ ] Respuestas técnicas precisas y confiadas

**Preguntas de Práctica:**
- "¿Por qué no usan laboratorio?" → Respuesta preparada
- "¿Cómo manejan el desbalance de clases?" → scale_pos_weight
- "¿Qué es RAG?" → Retrieval-Augmented Generation + ejemplo

**→ Puntos:** `___/5`

---

### E3. Formato y Tiempo (4 pts)

**Umbral de Puntos:**
- 4 pts: Respeta tiempo límite + estructura clara + visuales efectivos + demo fluida
- 2 pts: Cumple requisitos básicos con problemas menores
- 1 pt: Incumplimiento significativo

**Checklist:**
- [ ] Presentación dura 10 minutos (± 30 seg)
- [ ] Estructura clara con transiciones
- [ ] Diapositivas profesionales (no sobrecargadas)
- [ ] Demo en vivo funciona O backup de screenshots
- [ ] Demo narrada claramente
- [ ] Uso efectivo de visuales (gráficos, tablas, diagramas)
- [ ] Sin leer las diapositivas
- [ ] Contacto visual con jurado

**→ Puntos:** `___/4`

**TOTAL SECCIÓN E:** `___/15`

---

## 📊 PUNTUACIÓN TOTAL

| Sección | Puntos Máximos | Puntos Logrados |
|---------|----------------|-----------------|
| A. Rigor Técnico ML | 30 | ___ |
| B. LLMs, RAG y Guardrails | 25 | ___ |
| C. Producto y UX | 25 | ___ |
| D. Reproducibilidad | 15 | ___ |
| E. Presentación | 15 | ___ |
| **TOTAL** | **100** | **___** |

---

## 🎯 CRITERIO DE DESEMPATE

En caso de empate, se privilegia:
1. **Menor Brier Score** (mejor calibración)
2. **Menor gap de equidad** entre subgrupos

---

## ✅ VALIDACIÓN FINAL PRE-ENTREGA

### 24 Horas Antes:
- [ ] Este checklist completado al 100%
- [ ] Puntuación estimada calculada
- [ ] Gaps identificados y documentados
- [ ] Todos los archivos en GitHub actualizados
- [ ] App deployada y probada por alguien externo al equipo
- [ ] Presentación final ensayada 3+ veces

### 2 Horas Antes:
- [ ] Verificar que app sigue online
- [ ] Imprimir este checklist para referencia
- [ ] Backup de presentación en USB
- [ ] Equipo reunido y listo

---

## 📝 NOTAS ADICIONALES

**Observaciones del Equipo:**
```
[Espacio para notas sobre desafíos enfrentados, decisiones técnicas, etc.]







```

**Puntos Fuertes Identificados:**
```
[Lo que consideramos está muy bien implementado]







```

**Áreas de Mejora (si hubiera más tiempo):**
```
[Qué mejoraríamos con más tiempo/recursos]







```

---

## 🏆 ¡FELICITACIONES POR LLEGAR HASTA AQUÍ!

Completar este checklist demuestra:
- ✅ Rigor técnico
- ✅ Atención al detalle
- ✅ Compromiso con la calidad
- ✅ Trabajo en equipo

**¡Éxito en el Hackathon! 🚀**

---

**Firma del Equipo:**

_________________________    _________________________

_________________________    _________________________

**Fecha:** ___/___/2025


