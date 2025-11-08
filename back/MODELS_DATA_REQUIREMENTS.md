# Requisitos de Datos de los Modelos - OLD MODELS

## Modelo Diabetes (`old_model_xgb_calibrated.pkl`)

### Campos REQUERIDOS:
1. **edad** (age) - años
2. **genero** (sex) - 'M' o 'F'
3. **altura_cm** (height_cm) - centímetros
4. **peso_kg** (weight_kg) - kilogramos
5. **circunferencia_cintura** (waist_cm) - centímetros
6. **horas_sueno** (sleep_hours) - horas por noche
7. **tabaquismo** → convertido a **cigarrillos_por_dia** (smokes_cig_day)
8. **actividad_fisica** → convertido a **dias_mvpa_week** (days_mvpa_week)
9. **presion_sistolica** (systolic_bp) - mmHg
10. **colesterol_total** (total_cholesterol) - mg/dL

### Campos CALCULADOS:
- **imc** (BMI) - calculado de peso/altura
- Múltiples features derivadas (lifestyle_risk_score, waist_height_ratio, etc.)

---

## Modelo Cardiovascular (`old_model_cardiovascular.pkl`)

### Campos REQUERIDOS:
1. **edad** - años
2. **genero** - 'M' o 'F'
3. **altura_cm** - centímetros (para calcular IMC y rel_cintura_altura)
4. **peso_kg** - kilogramos (para calcular IMC)
5. **circunferencia_cintura** - centímetros
6. **glucosa_mgdl** - glucosa en ayunas (mg/dL)
7. **hdl_mgdl** - colesterol HDL "bueno" (mg/dL)
8. **ldl_mgdl** - colesterol LDL "malo" (mg/dL)
9. **trigliceridos_mgdl** - triglicéridos (mg/dL)

### Campos CALCULADOS:
- **imc** - calculado de peso/altura
- **rel_cintura_altura** - cintura / altura
- **imc_cuadratico** - imc²
- **imc_x_edad** - imc × edad
- **ratio_hdl_ldl** - hdl / ldl
- **trigliceridos_log** - log(triglicéridos)

### Campos NO USADOS:
❌ **presion_sistolica** - NO lo usa
❌ **colesterol_total** - NO lo usa (usa HDL/LDL por separado)
❌ **horas_sueno** - NO lo usa
❌ **tabaquismo** - NO lo usa
❌ **actividad_fisica** - NO lo usa

---

## Comparación

| Campo | Diabetes | Cardiovascular |
|-------|----------|----------------|
| edad | ✅ | ✅ |
| genero | ✅ | ✅ |
| altura_cm | ✅ | ✅ |
| peso_kg | ✅ | ✅ |
| circunferencia_cintura | ✅ | ✅ |
| horas_sueno | ✅ | ❌ |
| tabaquismo | ✅ | ❌ |
| actividad_fisica | ✅ | ❌ |
| presion_sistolica | ✅ | ❌ |
| colesterol_total | ✅ | ❌ |
| glucosa_mgdl | ❌ | ✅ |
| hdl_mgdl | ❌ | ✅ |
| ldl_mgdl | ❌ | ✅ |
| trigliceridos_mgdl | ❌ | ✅ |

---

## Implicaciones para el Chatbot

### Para obtener evaluación con modelo DIABETES:
El chatbot debe preguntar por:
- Datos básicos (edad, sexo, altura, peso, cintura)
- Estilo de vida (sueño, tabaquismo, actividad física)
- Datos clínicos básicos (presión sistólica, colesterol total)

### Para obtener evaluación con modelo CARDIOVASCULAR:
El chatbot debe preguntar por:
- Datos básicos (edad, sexo, altura, peso, cintura)
- **Panel lipídico completo** (glucosa, HDL, LDL, triglicéridos)
- NO necesita preguntar por estilo de vida ni presión/colesterol total

### Estrategia de Selección de Modelo:
1. Si el usuario menciona "análisis de sangre", "panel lipídico", "HDL/LDL", "triglicéridos" → preguntar por datos cardiovasculares
2. Si el usuario solo tiene datos básicos de salud → usar modelo diabetes
3. El modelo cardiovascular es MÁS ESPECÍFICO pero requiere análisis de laboratorio
4. El modelo diabetes es MÁS GENERAL y usa datos más accesibles

---

## Fuente de Información
- `back/app/ml/feature_engineering.py` - Funciones `build_feature_frame()` y `build_cardiovascular_feature_frame()`
- `back/app/ml/predictor.py` - Función `predict_risk()` con parámetros por modelo

