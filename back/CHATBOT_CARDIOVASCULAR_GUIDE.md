# Guía: Cómo Activar el Modelo Cardiovascular en el Chatbot

## ✅ Cambios Implementados

Se ha actualizado el chatbot para que pueda usar correctamente el modelo cardiovascular cuando el usuario proporcione los datos necesarios.

---

## 🔍 Requisitos de Datos por Modelo

### Modelo DIABETES (predeterminado)
**Datos comunes:**
- Edad, Sexo, Altura, Peso, Circunferencia de cintura

**Datos específicos:**
- ✅ Horas de sueño
- ✅ Tabaquismo (sí/no)
- ✅ Actividad física
- ✅ Presión sistólica
- ✅ Colesterol total

**NO usa:** Glucosa, HDL, LDL, Triglicéridos

---

### Modelo CARDIOVASCULAR (análisis de laboratorio)
**Datos comunes:**
- Edad, Sexo, Altura, Peso, Circunferencia de cintura

**Datos específicos:**
- ✅ Glucosa en ayunas (mg/dL)
- ✅ HDL - Colesterol bueno (mg/dL)
- ✅ LDL - Colesterol malo (mg/dL)
- ✅ Triglicéridos (mg/dL)

**NO usa:** Horas de sueño, Tabaquismo, Actividad física, Presión sistólica, Colesterol total

---

## 🎯 Cómo Activar el Modelo Cardiovascular

### Opción 1: Mencionar explícitamente que tienes análisis de sangre
```
Usuario: "Quiero una evaluación cardiovascular, tengo mis análisis de sangre"
Usuario: "Tengo mi panel lipídico completo"
Usuario: "Me hice exámenes y tengo HDL, LDL y triglicéridos"
```

### Opción 2: Mencionar los valores específicos
```
Usuario: "Mi HDL es 50, LDL es 130, y triglicéridos 150"
Usuario: "Quiero analizar mi perfil de lípidos"
Usuario: "Necesito evaluar mis niveles de HDL y LDL"
```

### Opción 3: Durante la conversación
Cuando el chatbot te pregunte qué tipo de evaluación quieres o si tienes análisis de sangre, responde afirmativamente.

---

## 📝 Ejemplos de Conversación

### ✅ CORRECTO - Para activar modelo cardiovascular

**Usuario:** "Hola, tengo mis análisis de sangre recientes y quiero una evaluación cardiovascular"

**ChatBot:** "¡Perfecto! Veo que tienes análisis de laboratorio. Voy a usar nuestro modelo cardiovascular especializado que analiza tu perfil lipídico. Empecemos con algunos datos básicos. ¿Cuál es tu edad?"

*[Continúa recopilando: edad, sexo, altura, peso, cintura]*
*[Luego pide: glucosa, HDL, LDL, triglicéridos]*
*[NO pedirá: sueño, tabaquismo, actividad física, presión, colesterol total]*

---

### ✅ CORRECTO - Modelo diabetes (predeterminado)

**Usuario:** "Hola, quiero saber mi riesgo de salud"

**ChatBot:** "¡Con gusto! Voy a ayudarte con una evaluación completa. Empecemos..."

*[Recopila: edad, sexo, altura, peso, cintura]*
*[Pregunta si tiene análisis de sangre]*
*[Si dice NO → pide: sueño, tabaquismo, actividad, presión, colesterol total]*

---

### ❌ PROBLEMA ANTERIOR - Por qué no funcionaba

**Antes:**
- El chatbot solo pedía "colesterol total" por defecto
- NUNCA preguntaba por HDL, LDL, triglicéridos
- El modelo cardiovascular requiere HDL+LDL+triglicéridos
- Resultado: Siempre usaba modelo diabetes

**Ahora:**
- El chatbot pregunta si tienes análisis de sangre
- Si dices SÍ, pide los valores específicos (HDL, LDL, triglicéridos, glucosa)
- El modelo cardiovascular se activa automáticamente
- Los umbrales ajustados (0.2/0.3) funcionan correctamente

---

## 🔄 Flujo de Decisión del Chatbot

```
┌─────────────────────────────────┐
│ Usuario inicia conversación     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Recopila datos comunes:         │
│ - Edad, Sexo                    │
│ - Altura, Peso                  │
│ - Circunferencia cintura        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ ¿Tiene análisis de sangre       │
│ con HDL/LDL/triglicéridos?      │
└────────┬───────────┬────────────┘
         │ SÍ        │ NO
         ▼           ▼
┌────────────┐  ┌───────────────┐
│ MODELO     │  │ MODELO        │
│ CARDIOVASC.│  │ DIABETES      │
├────────────┤  ├───────────────┤
│ Pide:      │  │ Pide:         │
│ - Glucosa  │  │ - Sueño       │
│ - HDL      │  │ - Tabaquismo  │
│ - LDL      │  │ - Actividad   │
│ - Triglic. │  │ - Presión     │
│            │  │ - Colesterol  │
└────────────┘  └───────────────┘
         │           │
         └─────┬─────┘
               ▼
    ┌─────────────────┐
    │ Genera predicción│
    │ con modelo       │
    │ correspondiente  │
    └──────────────────┘
```

---

## 🧪 Prueba Rápida

### Test 1: Modelo Cardiovascular
1. Inicia chat
2. Di: **"Tengo mis análisis de sangre con HDL, LDL y triglicéridos"**
3. Proporciona los datos cuando los pida
4. Verifica que al final diga: **"usando el modelo de cardiovascular"**

### Test 2: Modelo Diabetes (predeterminado)
1. Inicia chat
2. Di: **"Quiero una evaluación de riesgo"**
3. Cuando pregunte por análisis de sangre, di: **"No tengo análisis recientes"**
4. Proporciona los datos básicos de estilo de vida
5. Verifica que use el modelo diabetes

---

## 📊 Umbrales Aplicados

### Modelo Diabetes
- Bajo: < 0.30
- Moderado: 0.30 - 0.60
- Alto: ≥ 0.60

### Modelo Cardiovascular (ajustados)
- Bajo: < 0.20
- Moderado: 0.20 - 0.30
- Alto: ≥ 0.30

Los umbrales del modelo cardiovascular son más bajos porque este modelo es naturalmente más conservador.

---

## 🐛 Solución de Problemas

### "El chatbot sigue sin usar el modelo cardiovascular"

**Verificar:**
1. ¿Mencionaste explícitamente "análisis de sangre", "HDL", "LDL", o "triglicéridos"?
2. ¿Proporcionaste los 4 valores: glucosa, HDL, LDL, triglicéridos?
3. Revisa los logs del backend para ver qué modelo eligió

**En los logs verás:**
```
Modelo elegido por el agente: cardiovascular
```

### "El modelo cambió de cardiovascular a diabetes"

Esto es NORMAL si:
- Dijiste que usarías cardiovascular pero NO proporcionaste HDL/LDL/triglicéridos
- El sistema automáticamente cambia a diabetes como respaldo

**En los logs verás:**
```
⚠️ El agente eligió 'cardiovascular' pero faltan datos completos de lípidos
Cambiando a 'diabetes'
```

---

## ✨ Resumen

| Aspecto | Estado |
|---------|--------|
| ✅ Modelos antiguos cargados | `old_model_*.pkl` |
| ✅ Umbrales ajustados | Diabetes: 0.3/0.6, Cardio: 0.2/0.3 |
| ✅ Chatbot actualizado | Pregunta por datos correctos |
| ✅ Selección inteligente | Detecta análisis de sangre |
| ✅ Validación de datos | Verifica campos requeridos |
| ✅ Respaldo automático | Cambia a diabetes si faltan datos |

**Estado:** ✅ **COMPLETAMENTE FUNCIONAL**

---

**Última actualización:** 7 de noviembre de 2025  
**Archivos modificados:**
- `back/app/agents/conversational_agent.py`
- `back/app/ml/model_loader.py`
- `back/app/ml/predictor.py`

