# Estructura de Presentación - Hackathon IA Duoc UC 2025
## Coach de Bienestar Preventivo con IA Híbrida (NHANES)

**Duración Total: 10 minutos + 5 minutos Q&A**

---

## 📊 DIAPOSITIVA 1: Portada (30 seg)
**Contenido:**
- Título: "Coach de Bienestar Preventivo con IA Híbrida"
- Subtítulo: "Sistema ML + LLM para Predicción de Riesgo Cardiometabólico"
- Logo Duoc UC
- Nombre del equipo y miembros
- Fecha: 6-7 noviembre 2025

**Notas del Orador:**
- Presentación breve y energética
- Captar atención desde el inicio

---

## 🎯 DIAPOSITIVA 2: Hook Inicial (30 seg)
**Contenido:**
- Estadística impactante:
  - "34.2 millones de adultos en EE.UU. tienen diabetes"
  - "1 de cada 3 adultos tiene prediabetes y el 80% no lo sabe"
  - "La prevención puede reducir el riesgo en 58%"

**Pregunta Provocativa:**
- "¿Y si pudieras conocer tu riesgo cardiometabólico en minutos y recibir un plan personalizado basado en evidencia?"

**Notas del Orador:**
- Usar tono serio pero esperanzador
- Conectar emocionalmente con la audiencia

---

## 🔍 DIAPOSITIVA 3-4: El Problema (1.5 min)

### DIAPOSITIVA 3: Contexto
**Contenido:**
- Diabetes y enfermedad cardiovascular: epidemia silenciosa
- Factores de riesgo modificables: obesidad, sedentarismo, mala alimentación, sueño
- Brecha: Falta de herramientas preventivas accesibles y personalizadas

### DIAPOSITIVA 4: Necesidad
**Contenido:**
- Sistemas actuales:
  - ❌ Genéricos (no personalizados)
  - ❌ Requieren exámenes de laboratorio
  - ❌ No explican el porqué del riesgo
  - ❌ No generan planes de acción concretos

**Oportunidad:**
- ✅ IA puede predecir riesgo usando solo estilo de vida
- ✅ Personalización masiva con LLMs
- ✅ Explicabilidad con SHAP

**Notas del Orador:**
- Enfatizar la brecha entre prevención y herramientas disponibles
- Preparar transición a la solución

---

## 💡 DIAPOSITIVA 5-7: Nuestra Solución (2.5 min)

### DIAPOSITIVA 5: Arquitectura General
**Contenido:**
- Diagrama de flujo del sistema:
  ```
  Usuario → Formulario Web → 
  [Modelo ML] → Puntaje de Riesgo + Drivers SHAP → 
  [LLM + RAG] → Plan Personalizado → 
  PDF Descargable
  ```

- **Componentes clave:**
  1. Motor de Riesgo (XGBoost)
  2. Explicabilidad (SHAP)
  3. Coach Inteligente (GPT-4o-mini + RAG)
  4. Guardrails éticos

### DIAPOSITIVA 6: Motor de Riesgo ML
**Contenido:**
- **Datos:** NHANES 2015-2018 (~15,000 participantes)
- **Features:** Solo estilo de vida (NO laboratorio)
  - Antropometría: IMC, cintura/altura
  - Hábitos: sueño, actividad física, tabaco
  - Interacciones avanzadas: BMI×edad×sexo
- **Modelo:** XGBoost optimizado
- **Validación:** Split temporal estricto
  - Train: 2015-2016
  - Test: 2017-2018

**Métricas (destacar con íconos):**
- 🎯 AUROC: **0.XX** (meta: ≥0.80)
- 📊 Brier Score: **0.XX** (meta: ≤0.12)
- ⚖️ Fairness: Gap AUROC < 0.05 entre subgrupos

### DIAPOSITIVA 7: Coach con RAG
**Contenido:**
- **RAG (Retrieval-Augmented Generation):**
  - Base de conocimiento local validada
  - BM25 para búsqueda semántica
  - Citas explícitas de fuentes (NO alucinaciones)

- **Prompts con Guardrails:**
  - Lenguaje claro y no-diagnóstico
  - Planes SMART (específicos, medibles, alcanzables, relevantes, temporales)
  - Disclaimer médico obligatorio
  - Derivación a profesional si riesgo > 70%

**Notas del Orador:**
- Enfatizar el enfoque ético
- Explicar por qué RAG es crítico (veracidad)

---

## 🎬 DIAPOSITIVA 8: Demo en Vivo (3 min)

**Contenido de la Diapositiva:**
- "DEMO EN VIVO"
- URL de la app: https://huggingface.co/spaces/...

**Flujo de la Demo:**

### Paso 1: Presentar la Interfaz (30 seg)
- Mostrar la app en pantalla completa
- Explicar los campos del formulario:
  - "Perfil simple: edad, sexo, medidas antropométricas, hábitos"
  - "NO requiere exámenes de sangre"

### Paso 2: Caso de Uso Real (1 min)
- **Persona de ejemplo:**
  - Hombre, 52 años
  - IMC 31 (sobrepeso)
  - Cintura 105 cm (obesidad central)
  - Sedentario (0-1 días actividad)
  - Sueño 5-6 horas

- **Llenar formulario en tiempo real**
- Clic en "Evaluar Riesgo"

### Paso 3: Resultados (1 min)
- **Mostrar puntaje:**
  - "Riesgo Alto: 68%"
  - Indicador rojo 🔴

- **Explicabilidad SHAP:**
  - "Top 3 factores que impulsan tu riesgo:"
    1. Interacción IMC×edad: +0.75
    2. Obesidad central: +0.42
    3. Sedentarismo: +0.38

- **Tabla y gráfico SHAP**
  - Mostrar impacto visual

### Paso 4: Plan Personalizado (30 seg)
- Clic en "Generar Plan"
- Mostrar plan de 2 semanas:
  - Semana 1: Objetivos concretos
  - Semana 2: Profundización
  - Citas a fuentes
  - Disclaimer visible

- Descargar PDF
- Mostrar PDF brevemente

**Notas del Orador:**
- Practicar la demo MUCHAS VECES
- Tener backup de screenshots si falla internet
- Narrar cada acción claramente
- Mantener energía y entusiasmo

---

## 📈 DIAPOSITIVA 9: Resultados y Métricas (1 min)

**Contenido:**

### Rigor Técnico
| Métrica | Objetivo | Logrado | Puntos |
|---------|----------|---------|--------|
| AUROC | ≥0.80 | **0.XX** | XX/12 |
| Brier Score | ≤0.12 | **0.XX** | XX/6 |
| Anti-fuga | ✓ | ✓ | 6/6 |
| Explicabilidad | SHAP | ✓ | 6/6 |

### Sistema LLM + RAG
| Componente | Estado |
|------------|--------|
| RAG con KB local | ✅ 100% citas válidas |
| Guardrails | ✅ Derivación + disclaimers |
| Planes SMART | ✅ 2 semanas personalizados |

### Producto
| Feature | Estado |
|---------|--------|
| App funcional | ✅ Deploy en HF Spaces |
| PDF descargable | ✅ |
| Fairness | ✅ Gap < 0.05 |

**Notas del Orador:**
- Ser honesto con las métricas (si no se alcanzó 0.80, explicar)
- Destacar fortalezas del sistema
- Transición a impacto

---

## 🌍 DIAPOSITIVA 10: Impacto y Próximos Pasos (1 min)

### Impacto Actual
**Contenido:**
- **Accesibilidad:** Evaluación de riesgo sin necesidad de laboratorio
- **Educación:** Usuarios entienden QUÉ impulsa su riesgo
- **Acción:** Planes concretos y descargables
- **Ética:** Sistema responsable con guardrails

**Casos de Uso:**
- Centros de salud comunitarios
- Programas de prevención empresarial
- Telehealth y apps de bienestar

### Próximos Pasos
**Contenido:**
- 📊 **Validación externa:** Evaluar en población chilena
- 🌐 **Multilingüe:** Expandir a español, portugués
- 📱 **App móvil:** iOS/Android nativa
- 🔗 **Integración EHR:** Conexión con sistemas médicos
- 🤖 **Modelos locales:** Reducir dependencia de OpenAI

**Visión:**
> "Un coach de bienestar preventivo en el bolsillo de cada persona"

**Notas del Orador:**
- Ser ambicioso pero realista
- Conectar con la misión de prevención en salud pública
- Terminar con energía

---

## 🙏 DIAPOSITIVA 11: Cierre y Agradecimientos (30 seg)

**Contenido:**
- **Resumen en 1 frase:**
  - "Sistema híbrido ML+LLM que predice riesgo cardiometabólico y genera planes personalizados con ética y explicabilidad"

- **Agradecimientos:**
  - Duoc UC por el hackathon
  - Mentores y jurado
  - Equipo

- **Contacto:**
  - GitHub: [enlace]
  - Email del equipo
  - Demo: [URL de HF Spaces]

- **Call to Action:**
  - "¡Prueba la demo!" [QR Code a la app]

---

## 📋 CHECKLIST PREVIO A LA PRESENTACIÓN

### 1 Semana Antes:
- [ ] Crear todas las diapositivas
- [ ] Practicar presentación completa (timing)
- [ ] Probar demo en vivo
- [ ] Capturar screenshots de backup
- [ ] Revisar métricas finales del modelo

### 3 Días Antes:
- [ ] Ensayo general con el equipo
- [ ] Ajustar timing de cada sección
- [ ] Preparar respuestas a preguntas comunes:
  - ¿Por qué no usar laboratorio?
  - ¿Cómo manejan datos sensibles?
  - ¿Cuál es el costo de inferencia?
  - ¿Cómo se actualiza el modelo?

### 1 Día Antes:
- [ ] Verificar que la app está desplegada y funcionando
- [ ] Backup de la presentación en USB y cloud
- [ ] Verificar laptop y cables
- [ ] Imprimir notas del orador

### El Día:
- [ ] Llegar 30 min antes
- [ ] Probar conexión y proyector
- [ ] Tener agua a mano
- [ ] Respirar profundo y sonreír 😊

---

## 💡 TIPS PARA LA PRESENTACIÓN

### Storytelling
- Usar narrativa: Problema → Solución → Impacto
- Conectar emocionalmente (salud es personal)
- Evitar jerga técnica excesiva

### Comunicación
- Contacto visual con jurado
- Lenguaje corporal abierto
- Voz clara y ritmo moderado
- Pausas estratégicas para enfatizar

### Técnica
- PRACTICAR, PRACTICAR, PRACTICAR
- Memorizar transiciones clave
- No leer las diapositivas
- Usar el demo para demostrar, no solo hablar

### Manejo de Tiempo
- Usar cronómetro silencioso
- Tener puntos de ajuste (si vas rápido/lento)
- Dejar tiempo para preguntas

### Plan B
- Screenshots de backup si falla demo
- Respuestas preparadas para preguntas difíciles
- No entrar en pánico si algo falla

---

## 🎯 PREGUNTAS FRECUENTES ANTICIPADAS

### Técnicas:
1. **¿Por qué XGBoost y no deep learning?**
   - "Datos tabulares → XGBoost es SOTA, más interpretable y eficiente"

2. **¿Cómo evitan bias en los datos NHANES?**
   - "Análisis de fairness por subgrupos, reportamos gaps y usamos pesos muestrales"

3. **¿Qué pasa si OpenAI falla?**
   - "Tenemos fallback plan template-based, también consideramos modelos locales"

### Producto:
4. **¿Cuánto cuesta por usuario?**
   - "Inferencia ML: <$0.001, OpenAI: ~$0.02 por plan, total <$0.03/usuario"

5. **¿Cómo se actualiza el modelo?**
   - "Pipeline de retraining con nuevos ciclos NHANES, validación continua"

### Impacto:
6. **¿Realmente funciona en población no-estadounidense?**
   - "Validación externa necesaria, pero features son universales (IMC, actividad física)"

7. **¿Cómo manejan responsabilidad legal?**
   - "Disclaimers claros, NO diagnóstico, derivación obligatoria si riesgo alto"

---

## 📁 RECURSOS ADICIONALES

### Para Crear Diapositivas:
- Google Slides (recomendado para colaboración)
- PowerPoint
- Canva (para diseño visual)

### Paleta de Colores Sugerida:
- Primario: #2C3E50 (azul oscuro)
- Secundario: #3498DB (azul claro)
- Acento: #E74C3C (rojo para alertas)
- Éxito: #27AE60 (verde)
- Texto: #2C3E50

### Fuentes:
- Títulos: Helvetica Bold / Roboto Bold
- Cuerpo: Helvetica / Roboto

### Iconos:
- Font Awesome (free)
- Material Design Icons
- Emojis para toque amigable

---

## ✅ ÚLTIMO RECORDATORIO

**La presentación es TAN importante como el código.**

- Jurado evalúa:
  1. Storytelling e impacto (6 pts)
  2. Comunicación técnica (5 pts)
  3. Formato y tiempo (4 pts)

- **Total: 15 puntos** de 100 totales

**¡Practiquen hasta que fluya naturalmente!**

**¡Éxito en el Hackathon! 🚀**


