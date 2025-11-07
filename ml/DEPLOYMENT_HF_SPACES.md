# Guía de Deployment en Hugging Face Spaces

## Pasos para Deployar la Aplicación

### 1. Preparar el Repositorio

Asegúrate de tener todos los archivos necesarios en el directorio `ml/`:

```
ml/
├── app_streamlit.py          # Aplicación Streamlit principal
├── rag_coach.py              # Sistema RAG
├── pdf_generator.py          # Generador de PDFs
├── model_xgboost.pkl         # Modelo entrenado
├── imputer.pkl               # Imputador de features
├── feature_names.pkl         # Nombres de features
├── requirements.txt          # Dependencias Python
├── kb/                       # Base de conocimiento
│   └── diabetes_prevention.md
└── README.md                 # Documentación
```

### 2. Crear un Espacio en Hugging Face

1. Ve a [https://huggingface.co/new-space](https://huggingface.co/new-space)
2. Configuración:
   - **Owner**: Tu usuario o organización
   - **Space name**: `coach-bienestar-nhanes` (o nombre preferido)
   - **License**: MIT
   - **Select the Space SDK**: **Streamlit**
   - **Hardware**: CPU basic (gratis) o GPU si necesitas más rendimiento
   - **Visibility**: Public o Private según preferencia

### 3. Subir Archivos

**Opción A: Vía Web Interface**
1. Crea el Space
2. Usa "Files" → "Add file" → "Upload files"
3. Sube todos los archivos del directorio `ml/`

**Opción B: Vía Git (Recomendado)**

```bash
# Clonar el repositorio del Space
git clone https://huggingface.co/spaces/<tu-usuario>/coach-bienestar-nhanes
cd coach-bienestar-nhanes

# Copiar archivos necesarios
cp ../ml/app_streamlit.py .
cp ../ml/rag_coach.py .
cp ../ml/pdf_generator.py .
cp ../ml/*.pkl .
cp ../ml/requirements.txt .
cp -r ../ml/kb .

# Renombrar app_streamlit.py a app.py (convención de HF Spaces)
mv app_streamlit.py app.py

# Commit y push
git add .
git commit -m "Initial deployment"
git push
```

### 4. Configurar Variables de Entorno (Secrets)

La aplicación necesita la API key de OpenAI para funcionar completamente.

1. En tu Space, ve a **Settings** → **Repository secrets**
2. Añade:
   - `OPENAI_API_KEY`: Tu API key de OpenAI

### 5. Verificar requirements.txt

Asegúrate de que `requirements.txt` contiene todas las dependencias:

```txt
# ML y Data Science
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
joblib>=1.3.0

# Visualización
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0
shap>=0.43.0

# API y Web
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
streamlit>=1.28.0
requests>=2.31.0
altair>=5.0.0

# LLM y RAG
openai>=1.0.0
rank-bm25>=0.2.2

# PDF Generation
reportlab>=4.0.0

# Utilidades
python-multipart>=0.0.6
```

### 6. Estructura del Space

El archivo principal debe llamarse `app.py` para Streamlit Spaces:

```
/
├── app.py                    # ← Renombrar app_streamlit.py
├── rag_coach.py
├── pdf_generator.py
├── model_xgboost.pkl
├── imputer.pkl
├── feature_names.pkl
├── requirements.txt
├── README.md
└── kb/
    └── diabetes_prevention.md
```

### 7. README.md para el Space

Crea un `README.md` descriptivo en el Space:

```markdown
---
title: Coach de Bienestar Preventivo
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# 🏥 Coach de Bienestar Preventivo

Sistema híbrido ML + LLM para predicción de riesgo cardiometabólico y coaching personalizado.

## Características

- ✅ Predicción de riesgo basada en XGBoost (AUROC ≥0.80)
- ✅ Explicabilidad con SHAP
- ✅ Coach con RAG usando base de conocimiento validada
- ✅ Generación de planes SMART personalizados
- ✅ Exportación a PDF
- ✅ Validación temporal y anti-fuga de datos

## Uso

1. Completa tu perfil en la barra lateral
2. Haz clic en "Evaluar Riesgo"
3. Revisa tu puntaje y factores de riesgo
4. Genera tu plan personalizado
5. Descarga el PDF

## Tecnologías

- **ML**: XGBoost, SHAP, scikit-learn
- **LLM**: OpenAI GPT-4o-mini con RAG
- **Framework**: Streamlit, FastAPI
- **Datos**: NHANES 2015-2018

## Disclaimer

⚠️ Este sistema NO realiza diagnósticos médicos. Consulta con un profesional de salud.

## Desarrollado para

Hackathon IA Duoc UC 2025 - Desafío Salud NHANES
```

### 8. Verificar el Deployment

1. Una vez subidos los archivos, el Space se construirá automáticamente
2. Verifica los logs en la pestaña "App" → "Logs"
3. Si hay errores, revisa:
   - Que todos los archivos `.pkl` estén presentes
   - Que `requirements.txt` sea correcto
   - Que el directorio `kb/` exista con su contenido
   - Que las variables de entorno estén configuradas

### 9. URL Pública

Tu aplicación estará disponible en:
```
https://huggingface.co/spaces/<tu-usuario>/coach-bienestar-nhanes
```

### 10. Actualizar el Space

Para actualizar tu aplicación:

```bash
# Hacer cambios en archivos locales
# Luego:
git add .
git commit -m "Descripción de cambios"
git push
```

El Space se reconstruirá automáticamente.

## Troubleshooting

### Error: "Module not found"
- Verifica que todos los módulos estén en `requirements.txt`
- Asegúrate de que los archivos `.py` estén en el directorio raíz

### Error: "File not found: model_xgboost.pkl"
- Verifica que los archivos `.pkl` se hayan subido correctamente
- Revisa que los nombres sean exactos (case-sensitive)

### La app carga pero no funciona el coach
- Verifica que `OPENAI_API_KEY` esté configurada en secrets
- Verifica que el directorio `kb/` exista con archivos `.md`

### La app es muy lenta
- Considera upgrade a hardware GPU en Settings
- Optimiza el modelo (reduce size de features si es posible)

## Alternativas de Deployment

Si no quieres usar Hugging Face Spaces:

### Streamlit Cloud
- [https://streamlit.io/cloud](https://streamlit.io/cloud)
- Proceso similar, conecta tu repositorio GitHub

### Railway
- [https://railway.app/](https://railway.app/)
- Soporta Docker containers

### Render
- [https://render.com/](https://render.com/)
- Free tier disponible

## Contacto

Para preguntas sobre el deployment, contacta al equipo del hackathon.


