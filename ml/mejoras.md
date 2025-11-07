Análisis Estratégico y Plan de Acción para la Hackathon de Salud NHANES 2025




I. Introducción: La Estrategia de los 100 Puntos para Ganar




A. La Rúbrica es el Plan de Batalla


El objetivo principal de esta hackathon no es simplemente construir el modelo de Machine Learning (ML) con el mayor $AUROC$. El objetivo es acumular la mayor cantidad de puntos según la rúbrica de evaluación.1 Esta es una competición de producto de IA híbrida, no un desafío exclusivo de ML.
La distribución de puntos revela la verdadera naturaleza del desafío 1:
* A. Rigor Técnico ML: 30 puntos
* B. LLMS, RAG y Guardrails: 25 puntos
* C. Producto y UX: 25 puntos
* D. Reproducibilidad y Buenas Prácticas: 15 puntos
* E. Presentación y Pitch Final: 15 puntos
Un análisis de esta distribución deja claro que las categorías B (LLM) y C (Producto/UX) suman 50 puntos, una puntuación significativamente mayor que la categoría A (ML), que vale 30. Un equipo que dedique el 90% de su tiempo a optimizar el $AUROC$ está matemáticamente posicionado para perder. La estrategia ganadora debe asignar recursos en paralelo a tres pistas de trabajo desde la Hora 0: ML (Rúbrica A), LLM/RAG (Rúbrica B) y Producto/Deploy (Rúbrica C), tal como lo sugiere el cronograma de 27 horas.1


B. El Arma Secreta: El Criterio de Desempate


En una competición de alto nivel, es casi seguro que varios equipos alcanzarán los umbrales máximos de puntuación, especialmente en la métrica principal de $AUROC$. La victoria se decidirá en los márgenes. El documento de la hackathon proporciona explícitamente el mecanismo para romper estos empates.
El criterio de desempate oficial es: "Se privilegia mejor calibración (menor Brier Score) y menor gap de equidad entre subgrupos".1
Esto significa que las rúbricas A2 (Brier Score, 6 puntos) y D3 (Métricas por subgrupos/Fairness, 4 puntos) no son solo 10 puntos combinados; son los puntos más importantes de toda la competición. Una inversión estratégica desproporcionada en la optimización de la calibración (Brier Score) y la mitigación de la equidad (Fairness Gap) es el pilar central de este plan de acción.


C. Tabla 1: Hoja de Ruta de Puntuación (El "Scorecard" del Ganador)


La siguiente tabla desglosa los criterios de puntuación más críticos y define el playbook técnico exacto para asegurar la máxima puntuación en cada uno. Esta tabla debe servir como el checklist principal del equipo durante la competición.


Criterio
  Puntos
  Métrica de Éxito
  Playbook de Acción (Técnica / Biblioteca)
  A1. $AUROC$
  12
  $AUROC > 0.80$
  XGBClassifier + Ingeniería de Features de Interacción 1
  A2. Calibración
  6
  $Brier < 0.12$
  sklearn.calibration.CalibratedClassifierCV(method='isotonic') 2
  A3. Validación
  6
  Split temporal + Sin fuga de datos
  Split por ciclo NHANES (Train $\le$ 2016, Test $\ge$ 2017) 1
  A4. Explicabilidad
  6
  Drivers locales claros y consistentes
  shap.TreeExplainer 4; formato de salida debe coincidir con 1
  B1. Extractor JSON
  8
  100% JSON válido + rangos correctos
  Clases Pydantic 5 + LLM con Salida Estructurada (ej. OpenAI Tools 7)
  B2. Coach RAG
  9
  Todas las recomendaciones con fuentes de /kb
  LangChain 8 o LlamaIndex 9 RAG apuntando solo al directorio /kb.10
  C1. App Funcional
  10
  Deploy funcional en HF Spaces
  Docker Space 11 corriendo FastAPI (backend) y Streamlit (frontend).13
  C2. Export & Sharing
  5
  PDF descargable
  Endpoint de FastAPI 14 usando fpdf2 15 para generación en memoria.
  D1. Repo & Scripts
  6
  requirements.txt + Semillas fijadas
  SEED = 42 en numpy, random, xgboost.1
  D3. Fairness
  4
  Reporte completo + análisis de gap
  fairlearn.metrics.MetricFrame 16 para replicar.11
  Desempate 1
  -
  Menor Brier Score
  Ganado por la estrategia de la Rúbrica A2.
  Desempate 2
  -
  Menor Gap de Equidad
  fairlearn.postprocessing.ThresholdOptimizer 17 para mitigar el gap.1
  

II. Playbook de Rigor Técnico (Rúbrica A - 30 pts): El Modelo ML




A. Fundamentos Innegociables: Anti-Fuga y Validación Temporal (A3 - 6 pts)


No seguir estas reglas resulta en la descalificación o una puntuación mínima. Son los 6 puntos más fáciles de asegurar.
1. Restricción Crítica (Anti-fuga): La regla es absoluta. Si la etiqueta (ej. Label A: Alto riesgo de diabetes) se define usando analitos de laboratorio como $A1c$ o glucosa, esas columnas (y sus derivadas obvias) están estrictamente prohibidas como features.1 El modelo debe predecir basándose únicamente en demografía, antropometría (peso, altura, cintura) y cuestionarios (estilo de vida, sueño, tabaquismo).1
2. Validación Temporal (Obligatoria): La validación debe ser temporal por ciclo NHANES.1 Queda prohibido usar k-fold aleatorio sobre todo el conjunto de datos como única validación.1 La división correcta es:
   * train_df = df[df['cycle'] <= 2016]
   * test_df = df[df['cycle'] >= 2017]
   * Se permite usar un split de validación (ej. train_test_split) dentro del train_df (datos 2007-2016) para validación intermedia y calibración, pero la evaluación final para la Rúbrica A debe reportarse sobre el test_df ciego (2017-Mar 2020).1


B. Ganando en AUROC (A1 - 12 pts): Feature Engineering Dirigido


El objetivo es superar $AUROC > 0.80$.1 La línea base sugerida es XGBoost.1 La clave para superar este umbral no es un ajuste de hiperparámetros exhaustivo, sino una ingeniería de características (feature engineering) precisa.
El archivo shap_feature_importance.csv 1 es una guía explícita. Revela las características más importantes de un modelo de alto rendimiento.1 Las 5 características principales por shap_importance son:
1. bmi_age_interaction (Importancia SHAP: 0.5317)
2. age (Importancia SHAP: 0.2645)
3. waist_height_ratio (Importancia SHAP: 0.2423)
4. bmi_age_sex_interaction (Importancia SHAP: 0.2212)
5. waist_age_interaction (Importancia SHAP: 0.2001)
El hecho de que bmi_age_interaction sea más importante que casi todas las demás características combinadas indica que el efecto del IMC (BMI) sobre el riesgo cardiometabólico no es lineal, sino que se multiplica exponencialmente con la edad. El script src/features.py 1 debe priorizar la creación de estas interacciones:


Python




# Ejemplo de src/features.py
def create_features(df):
   # Features base
   df['bmi'] = df['weight_kg'] / (df['height_cm'] / 100)**2
   df['waist_height_ratio'] = df['waist_cm'] / df['height_cm']
   
   # Features de interacción (las más importantes)
   df['bmi_age_interaction'] = df['bmi'] * df['age']
   df['waist_age_interaction'] = df['waist_cm'] * df['age']
   
   # Asumiendo sex_male = 1 para M, 0 para F
   df['bmi_age_sex_interaction'] = df['bmi'] * df['age'] * df['sex_male']
   
   return df



C. Ganando el Desempate 1: Calibración (A2 - 6 pts)


El objetivo es un Brier Score $< 0.12$.1 Esta es una métrica clave para el desempate.1
Los modelos de árbol potenciados (como XGBoost), aunque son excelentes en discriminación (alto $AUROC$), son conocidos por estar mal calibrados. Tienden a producir probabilidades predichas extremas (muy cercanas a 0.0 o 1.0), lo que penaliza fuertemente el Brier Score.18 Intentar optimizar XGBoost directamente para brier es complejo y puede perjudicar el $AUROC$.20
La estrategia ganadora es un enfoque de post-procesamiento en dos pasos:
1. Entrenar el XGBClassifier para maximizar el $AUROC$ (ej. usando eval_metric='logloss' o 'auc').
2. Calibrar las probabilidades de salida del modelo entrenado usando sklearn.calibration.CalibratedClassifierCV.2
La implementación específica es crucial:
* Se debe usar method='isotonic' (Regresión Isotónica).3 Es un método no paramétrico que es más potente y se adapta mejor a conjuntos de datos grandes (que NHANES) en comparación con method='sigmoid' (Platt Scaling).19
* El modelo XGBoost debe pasarse con cv='prefit' para evitar reentrenarlo.


Python




from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
import xgboost as xgb

# Dividir el set de entrenamiento (2007-2016) para tener un set de calibración
X_train_main, X_calib, y_train_main, y_calib = train_test_split(X_train, y_train, test_size=0.2, random_state=SEED)

# 1. Entrenar el modelo base para AUROC
model_xgb = xgb.XGBClassifier(random_state=SEED, eval_metric='logloss')
model_xgb.fit(X_train_main, y_train_main)

# 2. Calibrar el modelo para Brier Score (y el desempate)
calibrated_model = CalibratedClassifierCV(model_xgb, method='isotonic', cv='prefit')
calibrated_model.fit(X_calib, y_calib)

# 'calibrated_model' es el modelo final que se usará para predicciones
# y se persistirá en 'src/model.py'

Este calibrated_model asegura los 6 puntos de A2 y posiciona al equipo para ganar el primer criterio de desempate.


D. Explicabilidad Accionable (A4 - 6 pts): Implementando SHAP


Se requieren "drivers claros, consistentes con modelo y caso".1 Esto se debe entregar de dos formas:
1. Para el Reporte Técnico (Global): Se debe usar shap.TreeExplainer 4 para generar un gráfico de importancia de características global. El resultado debe ser visualmente coherente con shap_feature_importance.csv 1, demostrando que las features de interacción creadas son, de hecho, las más importantes.1
2. Para la API /predict (Local): El endpoint POST /predict debe devolver {"score": float, "drivers": [top_features]}.1 Los drivers son la explicación SHAP para una única predicción.26 El formato de esta salida debe coincidir exactamente con la estructura de shap_example_drivers.csv.1


Python




# En api/main.py (Lógica)
import shap

# Cargar el modelo base (XGBoost) del clasificador calibrado
# y el explainer UNA VEZ en el arranque de la app, no en cada request [27]
model_base = calibrated_model.base_estimator_
explainer = shap.TreeExplainer(model_base) [4]

def get_prediction_drivers(X_instance):
   # X_instance debe ser un DataFrame de 1 fila
   shap_values = explainer.shap_values(X_instance)
   
   #... Lógica para formatear la salida...
   # Crear un DataFrame con columnas:
   # 'feature', 'feature_value', 'shap_value', 'impact'
   # donde 'impact' = 'aumenta' si shap_value > 0 else 'reduce'
   
   drivers_list = formated_df.to_dict('records')
   return drivers_list

Esta implementación cumple con A4 y proporciona el payload necesario para el endpoint /predict.


III. Playbook del Coach Híbrido (Rúbrica B - 25 pts): LLM, RAG y Guardrails




A. El Extractor NL-JSON (B1 - 8 pts): Garantizando un JSON 100% Válido


El objetivo de 8 puntos es "100% JSON válido + rangos/unidades correctos".1 Confiar en un prompt simple (ej. "responde en formato JSON") es una estrategia de alto riesgo que probablemente resulte en errores frecuentes de validación, llevando a una puntuación de 3/8.1
La única estrategia robusta para asegurar los 8 puntos es usar Salida Estructurada (Structured Output).
1. Definir un Esquema Pydantic: El Esquema JSON de la página 8 del PDF 1 debe traducirse directamente a una clase Pydantic en Python.5 Esto permite la validación automática de tipos, rangos (minimum, maximum) y enumeraciones (enum).
2. Forzar la Salida del LLM: Utilizar una herramienta que fuerce al LLM a adherirse a este esquema.
   * Opción 1 (Nativa): Usar la API de OpenAI con response_format={ "type": "json_object" } y pasar el esquema JSON de Pydantic en la llamada de tools o structured_outputs.7
   * Opción 2 (LangChain): Usar el método .with_structured_output() en la cadena, pasándole la clase Pydantic.32


Python




from pydantic import BaseModel, Field
from typing import Literal

# Definido en src/prompts.py o similar
# Basado en , p. 8
class PerfilUsuario(BaseModel):
   age: int = Field(..., minimum=18, maximum=85, description="Edad del usuario en años completos")
   sex: Literal["F", "M"] = Field(..., description="Sexo biológico (F=Femenino, M=Masculino)")
   height_cm: float = Field(..., minimum=120, maximum=220, description="Altura en centímetros")
   weight_kg: float = Field(..., minimum=30, maximum=220, description="Peso corporal en kilogramos")
   waist_cm: float = Field(..., minimum=40, maximum=170, description="Circunferencia de cintura en centímetros")
   #... resto de campos...

# Lógica del Extractor (ej. con LangChain)
# chain = llm.with_structured_output(PerfilUsuario)
# valid_json = chain.invoke("Tengo 45 años, soy hombre, mido 175cm...")
# Pydantic validará automáticamente la salida [35]



B. El Coach RAG (B2 - 9 pts): Cero Alucinaciones, 100% Citado


El objetivo de 9 puntos es que "Todas las recomendaciones [estén] con fuentes de /kb".1 Cualquier alucinación o cita inválida reduce drásticamente la puntuación a 4 puntos. El sistema debe usar un LLM reforzado con una mini-base de conocimiento local (RAG).1
La arquitectura RAG debe configurarse para ser local-only y restrictiva:
1. Ingesta: Usar DirectoryLoader de LangChain 8 o SimpleDirectoryReader de LlamaIndex 9 para cargar exclusivamente los archivos Markdown (.md) del directorio /kb.1
2. Índice: Crear un índice vectorial en memoria (ej. FAISS, ChromaDB) con los chunks de estos documentos.
3. Prompt de Cero Alucinaciones: El componente más crítico es el prompt del sistema que se pasa al create_retrieval_chain.36 Este prompt debe instruir explícitamente al LLM para que no use conocimiento externo y cite cada una de sus afirmaciones.37
Plantilla de Prompt del Sistema (para src/prompts.py):


Fragmento de código




Eres un 'Coach de Bienestar Preventivo' profesional y empático.
Tu tarea es generar un plan de 2 semanas con acciones SMART (específicas, medibles, alcanzables, relevantes, temporales) para el usuario.

REGLAS CRÍTICAS:
1.  Debes basar tu respuesta *única y exclusivamente* en el siguiente 'Contexto' (los documentos de la base de conocimiento).
2.  NO uses ningún conocimiento externo o pre-entrenado.
3.  Si la respuesta no se encuentra en el Contexto, debes decir explícitamente: "No tengo información validada sobre ese tema en mi base de conocimiento."
4.  CADA recomendación específica que des debe terminar con una cita a su fuente. La fuente se encuentra en los metadatos del contexto. Formato de cita: [Fuente: /kb/nombre_del_archivo.md]

Contexto:
{context}

Pregunta del Usuario (basada en su perfil):
{input}

Esta plantilla 40 fuerza el comportamiento requerido para los 9 puntos de la rúbrica B2.


C. Guardrails y Seguridad (B3 - 8 pts): El Lenguaje No-Diagnóstico


Se requieren tres componentes para los 8 puntos: umbral de derivación, lenguaje no-diagnóstico y disclaimer visible.1
1. Disclaimer Explícito: Cada salida de la API (/coach) y cada página de la App Streamlit debe mostrar el disclaimer obligatorio: "Este sistema es un coach de bienestar y NO realiza diagnósticos médicos. Las recomendaciones no sustituyen la consulta con un profesional de la salud.".1
2. Umbral de Derivación: Esta es una regla de negocio simple que debe implementarse en la lógica del endpoint /coach antes de llamar al RAG. Se debe definir un umbral de riesgo (ej. $score > 0.75$).
Python
# Lógica en el endpoint /coach
score = request_data['score']

if score > 0.75: # Umbral crítico (definir en la hackathon)
   return {"plan": "Tu perfil muestra un riesgo elevado. Es crucial que consultes a un profesional de la salud para una evaluación completa. [Fuente: /kb/derivacion.md]", "citas": ["/kb/derivacion.md"]}
else:
   # Continuar con la lógica normal de RAG
   plan = rag_chain.invoke(...)
   return plan

3. Lenguaje Inclusivo: La instrucción de usar "lenguaje claro, inclusivo y no-diagnóstico" 1 debe incluirse en la plantilla de prompt del sistema del Coach RAG (ver sección III-B).


IV. Playbook del Producto (Rúbrica C - 25 pts): API y Despliegue




A. La API FastAPI


La API es la columna vertebral del producto y debe tener dos endpoints mínimos obligatorios 1:
   * POST /predict:
   * Recibe: Un JSON con el perfil del usuario. Este JSON debe ser validado usando la clase Pydantic PerfilUsuario (definida en III-A).
   * Procesa: (1) Ejecuta el pipeline de ingeniería de features (II-B). (2) Llama a .predict_proba() en el calibrated_model (II-C) para obtener el score.
   * Explica: Llama a la función get_prediction_drivers (II-D) para obtener los drivers SHAP locales.
   * Devuelve: {"score": float, "drivers": [...]}. El formato de drivers debe coincidir con shap_example_drivers.csv.1
   * POST /coach:
   * Recibe: Un JSON (ej. {"score": 0.65, "drivers": [...]}).
   * Procesa: (1) Ejecuta la lógica de guardrails y derivación (III-C). (2) Si está por debajo del umbral, formula una pregunta y la pasa al chain RAG (III-B).
   * Devuelve: Un JSON con el plan textual y las citas (ej. {"plan": "...", "citas": [...]}).


B. La App Streamlit y el Despliegue en HF Spaces (C1 - 10 pts)


El objetivo de 10 puntos es un "Formulario claro +... + deploy funcional en Spaces".1 El desafío técnico aquí es desplegar dos aplicaciones (FastAPI y Streamlit) en un único Hugging Face Space.13
La estrategia ganadora es usar un Docker Space 11:
   1. Crear el Space: En Hugging Face, crear un nuevo Space seleccionando "Docker" como SDK.
   2. Estructura del Repositorio: 1
/
├── Dockerfile
├── requirements.txt
├── api/
│   └── main.py       # App FastAPI
├── app/
│   └── app.py        # App Streamlit
├── src/              # Código ML, RAG, features
└── kb/               # Archivos Markdown para RAG

   3. requirements.txt: 1 Debe incluir todas las dependencias:
fastapi, uvicorn, streamlit, scikit-learn, xgboost, shap, fairlearn, langchain, langchain-openai, faiss-cpu, pydantic, fpdf2, markdown
   4. Dockerfile: Este archivo es la clave para ejecutar ambos servicios 11:
Dockerfile
FROM python:3.10

WORKDIR /code

COPY./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY. /code/

# Exponer ambos puertos: 7860 para FastAPI (default de HF Docker), 8501 para Streamlit
EXPOSE 7860
EXPOSE 8501

# Comando para lanzar ambos servicios en paralelo
# uvicorn en 0.0.0.0 en el puerto 7860
# streamlit en el puerto 8501
CMD ["bash", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 7860 & streamlit run app/app.py --server.port 8501 --server.address 0.0.0.0"]

   5. App Streamlit (app/app.py): Esta app (el frontend) hará llamadas HTTP a su propio backend FastAPI, que se ejecuta en http://localhost:7860.


C. Exportación a PDF y Enlace Compartible (C2 - 5 pts)


Se requiere "PDF descargable + enlace compartible funcional".1
      * Enlace Compartible: El despliegue en Hugging Face Spaces (IV-B) proporciona esto automáticamente.
      * PDF Descargable: La solución más robusta es generar el PDF en el backend (FastAPI).14
      1. Crear un nuevo endpoint en api/main.py: POST /coach/pdf.
      2. Este endpoint recibe el JSON del plan (o el texto) generado por /coach.
      3. Usar la biblioteca fpdf2 (ligera y pura en Python, ideal para contenedores).15
      4. Generar el PDF en memoria y devolverlo como una Response de FastAPI.14
Python
# En api/main.py
from fpdf import FPDF
from fastapi.responses import Response

@app.post("/coach/pdf")
async def get_plan_pdf(plan_data: PlanModel): # Usar un Pydantic model
   pdf = FPDF()
   pdf.add_page()
   pdf.set_font("Arial", size=12)
   pdf.multi_cell(0, 10, txt=plan_data.plan_text) # 
   pdf.multi_cell(0, 10, txt=f"Citas: {', '.join(plan_data.citas)}")

   # Guardar en buffer de bytes
   pdf_bytes = pdf.output(dest='S').encode('latin1')

   return Response(content=pdf_bytes, 
                   media_type='application/pdf',
                   headers={"Content-Disposition": "attachment; filename=plan_bienestar.pdf"})
La app Streamlit tendrá un st.download_button que llama a este endpoint para obtener el archivo.


D. Claridad para el Usuario (C3 - 10 pts)


La puntuación máxima (10 pts) requiere "Mensajes simples + inclusivos + explicación clara del score".1 Esto es diseño de UX y copywriting.
      * Traducción del Score: La app Streamlit no debe mostrar `$score = 0.7834$. Debe traducirlo:
      * if score > 0.75: st.error("Riesgo: Alto")
      * elif score > 0.5: st.warning("Riesgo: Moderado")
      * else: st.success("Riesgo: Bajo")
      * Explicación del Score: La app debe mostrar los drivers SHAP (de A4) de forma legible: "Tu riesgo aumenta principalmente debido a:,".


V. Fundamentos Críticos (Rúbrica D - 15 pts): Reproducibilidad y Equidad




A. Reproducibilidad (D1 - 6 pts, D2 - 5 pts)


Estos 11 puntos son "regalados" si se mantiene la disciplina desde el principio.
      * requirements.txt (D1): Ya cubierto en la sección IV-B.1
      * README.md (D2): El README.md debe ser completo, con instrucciones claras de instalación y ejecución local.1
      * Semillas Fijas (D1): Es obligatorio "fijar semillas en todo el código".1 Se debe crear un archivo src/config.py o similar.
Python
# src/config.py
import os
import random
import numpy as np

SEED = 42

def set_seeds():
   os.environ = str(SEED)
   random.seed(SEED)
   np.random.seed(SEED)

# En model.py:
# from src.config import SEED
# model_xgb = XGBClassifier(random_state=SEED,...)



B. Ganando el Desempate 2: Reporte y Mitigación de Equidad (D3 - 4 pts)


Este es el segundo criterio de desempate.1 La rúbrica exige un "Reporte completo... + análisis de gap + mitigaciones".1
         1. El Reporte (Análisis): El archivo fairness_analysis.csv 1 no es un ejemplo, es la plantilla exacta del reporte que se debe entregar.1 Se debe replicar esta tabla usando la biblioteca fairlearn.44 El script src/eval.py debe generar esta salida.
Python
# En src/eval.py
from fairlearn.metrics import MetricFrame, selection_rate
from sklearn.metrics import roc_auc_score, brier_score_loss

# Definir métricas
metrics = {
   'auroc': roc_auc_score,
   'brier': brier_score_loss,
   'prevalence': selection_rate, # 'prevalence' es la 'selection_rate' en y_true
   'n': lambda y_t, y_p: y_t.shape
}

# Calcular predicciones en el test set
y_pred_proba = calibrated_model.predict_proba(X_test)[:, 1]

# Crear el MetricFrame
mf = MetricFrame(metrics=metrics,
                y_true=y_test,
                y_pred=y_pred_proba,
                sensitive_features=X_test])

# El resultado se obtiene con mf.by_group
print(mf.by_group) # Esto genera la tabla [16, 47, 48, 49]

         2. El Gap (Análisis): El "gap absoluto" 1 se calcula fácilmente desde el MetricFrame:
gap_auroc = mf.difference(metric='auroc', method='max')
gap_brier = mf.difference(metric='brier', method='max')
         3. La Mitigación (Acción): Para ganar el desempate, no basta con reportar el gap, hay que mitigarlo. La forma más rápida en una hackathon es el post-procesamiento, que no requiere reentrenar el modelo.50 Se usará fairlearn.postprocessing.ThresholdOptimizer.17
Python
from fairlearn.postprocessing import ThresholdOptimizer

# 1. Definir el optimizador post-procesamiento
# constraints='equalized_odds' busca igualar tasas de verdaderos positivos y falsos positivos
post_processor = ThresholdOptimizer(
   estimator=calibrated_model, # El modelo ya calibrado
   constraints="equalized_odds", # o 'demographic_parity'
   objective="balanced_accuracy_score",
   prefit=True # ¡Importante! No reentrenar.
)

# 2. Ajustar los umbrales usando el set de calibración
post_processor.fit(X_calib, y_calib, sensitive_features=X_calib)

# 'post_processor' es ahora el modelo final para predicciones BINARIAS (ej..predict())
# ajustará los umbrales por grupo para reducir el gap.



C. Tabla 2: Plantilla Objetivo del Reporte de Equidad (para Rúbrica D3)


El script src/eval.py debe generar una salida que coincida con la estructura de fairness_analysis.csv.1 Este es el objetivo visual para el entregable D3.
subgroup
  n
  prevalence
  auroc
  auprc
  brier
  Sex_M
  ...
  ...
  ...
  ...
  ...
  Sex_F
  ...
  ...
  ...
  ...
  ...
  Age_18-44
  ...
  ...
  ...
  ...
  ...
  Age_45-59
  ...
  ...
  ...
  ...
  ...
  Age_60+
  ...
  ...
  ...
  ...
  ...
  Race_Mexican
  ...
  ...
  ...
  ...
  ...
  Race_Hispanic
  ...
  ...
  ...
  ...
  ...
  Race_White
  ...
  ...
  ...
  ...
  ...
  Race_Black
  ...
  ...
  ...
  ...
  ...
  Race_Asian
  ...
  ...
  ...
  ...
  ...
  

VI. El Pitch Final (Rúbrica E - 15 pts): La Narrativa de la Victoria


Estos 15 puntos se ganan en la presentación de 10 minutos.1 La demo debe ser fluida y seguir la narrativa estratégica.
Estructura de 10 Minutos 1:
            * (2 min) Problema y Motivación: "El riesgo cardiometabólico es una epidemia silenciosa. Las soluciones actuales son genéricas. Nuestro 'Coach de Bienestar Preventivo' ofrece estimación de riesgo personalizada y planes de acción éticos y accionables."
            * (3 min) Solución Técnica: "Construimos una arquitectura de IA Híbrida.
            * (Slide 1: ML) Nuestro motor de riesgo ML (A) no solo supera el 80% de $AUROC$ (A1), sino que está diseñado para ganar los desempates: optimizamos la Calibración (Brier < 0.12) con Regresión Isotónica (A2) y garantizamos la Equidad (D3) con mitigación de post-procesamiento.
            * (Slide 2: LLM) Nuestro Coach (B) usa un extractor JSON 100% válido (B1) y un RAG (B2) que garantiza cero alucinaciones, con 100% de citas a la base de conocimiento local, y guardrails de seguridad (B3)."
            * (3 min) Demo en Vivo (El "Camino Dorado"):
            1. (1 min) Mostrar la App Streamlit (C1). Ingresar datos de un usuario de riesgo.
            2. (1 min) Clic en "Predecir". Mostrar el score traducido (C3: "Riesgo Alto") y los drivers SHAP (A4: "Tu riesgo es alto principalmente por la interacción de tu IMC y tu edad").
            3. (1 min) Clic en "Obtener Plan". Mostrar la respuesta del Coach RAG (B2: "Aquí tienes un plan... [Fuente: /kb/sueno.md]") y el disclaimer (B3).
            4. (Bonus 30s) Clic en "Descargar PDF" (C2) y mostrar el archivo generado.
            * (1 min) Resultados: "Nuestro modelo, validado temporalmente (A3), y nuestro reporte de equidad (D3) están en el repositorio (D1, D2)."
            * (1 min) Impacto: "Esta solución está lista para escalar, es reproducible, ética y puede implementarse para ayudar a personas reales a gestionar su salud preventiva."


VII. Resumen: Checklist de Entregables Obligatorios y Plan de Acción de 27 Horas




A. Tabla 3: Checklist Final de Entregables


Usar esta tabla como control de calidad final antes de la entrega.1
Entregable
  Estado
  Notas Clave
  1. Repositorio GitHub (/src, /api, /app)
  [ ]
  ¿El README.md (D2) es claro y completo?
  2. API FastAPI (POST /predict, /coach)
  [ ]
  ¿Los endpoints (C1) están funcionales y documentados?
  3. App Demo Interactiva (Streamlit)
  [ ]
  ¿El deploy en HF Spaces (C1) con Docker funciona?
  4. Reporte Técnico (2-3 págs)
  [ ]
  ¿Incluye la tabla de Calibración (A2) y Equidad (D3)?
  5. Plan PDF Descargable (1-2 págs)
  [ ]
  ¿El endpoint (C2) genera el PDF correctamente?
  6. Bitácora de Prompts
  [ ]
  ¿Están los prompts del Extractor (B1) y del Coach RAG (B2)?
  7. Presentación Final (10 min)
  [ ]
  ¿Sigue la estructura de la Rúbrica E? ¿Demo ensayada?
  

B. Hoja de Ruta Sugerida de 27 Horas


La única forma de completar todos los entregables es mediante un trabajo paralelo intensivo. El cronograma sugerido 1 debe seguirse asignando roles claros desde la Hora 0:
            * Equipo ML (Rúbricas A, D3): Enfocados en src/features.py, src/model.py, src/eval.py. Tareas: Split temporal, feature engineering (II-B), entrenamiento de XGBoost, calibración isotónica (II-C) y generación del reporte de fairness (V-B).
            * Equipo LLM (Rúbrica B): Enfocados en src/prompts.py, src/rag.py. Tareas: Definir el Pydantic schema (III-A), implementar el Extractor JSON (III-A), construir el RAG local-only (III-B) y definir los prompts de guardrails (III-C).
            * Equipo Producto (Rúbricas C, D1, D2): Enfocados en api/main.py, app/app.py, Dockerfile. Tareas: Configurar el HF Docker Space (IV-B), construir los endpoints de FastAPI (IV-A), desarrollar la UI de Streamlit (IV-D), e implementar la generación de PDF (IV-C).
La integración de estos tres componentes será el mayor desafío y debe planificarse desde el inicio.
Obras citadas
            1. Desafio_Salud_NHANES_2025_duoc.pdf
            2. CalibratedClassifierCV — scikit-learn 1.7.2 documentation, fecha de acceso: noviembre 6, 2025, https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html
            3. 1.16. Probability calibration — scikit-learn 1.7.2 documentation, fecha de acceso: noviembre 6, 2025, https://scikit-learn.org/stable/modules/calibration.html
            4. shap.TreeExplainer — SHAP latest documentation, fecha de acceso: noviembre 6, 2025, https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html
            5. Control LLM output with LangChain's structured and Pydantic output parsers - Atamel.Dev, fecha de acceso: noviembre 6, 2025, https://atamel.dev/posts/2024/12-09_control_llm_output_langchain_structured_pydantic/
            6. Mastering Pydantic for LLM Workflows - Artificial Intelligence in Plain English, fecha de acceso: noviembre 6, 2025, https://ai.plainenglish.io/mastering-pydantic-for-llm-workflows-c6ed18fc79cc
            7. Structured model outputs - OpenAI API, fecha de acceso: noviembre 6, 2025, https://platform.openai.com/docs/guides/structured-outputs
            8. Building a Markdown Knowledge Ingestor for RAG with LangChain | by vishal khushlani, fecha de acceso: noviembre 6, 2025, https://medium.com/@vishalkhushlani123/building-a-markdown-knowledge-ingestor-for-rag-with-langchain-ba201515f6c4
            9. Basic Tutorial RAG with Llama-Index | by DanShw - Medium, fecha de acceso: noviembre 6, 2025, https://medium.com/@kofsitho/basic-tutorial-rag-with-llama-index-8927a5716dd1
            10. andrea-nuzzo/markdown-langchain-rag - GitHub, fecha de acceso: noviembre 6, 2025, https://github.com/andrea-nuzzo/markdown-langchain-rag
            11. Deploying Your FastAPI Applications on Huggingface Via Docker, fecha de acceso: noviembre 6, 2025, https://huggingface.co/blog/HemanthSai7/deploy-applications-on-huggingface-spaces
            12. Docker Spaces - Hugging Face, fecha de acceso: noviembre 6, 2025, https://huggingface.co/docs/hub/spaces-sdks-docker
            13. Streamlit, FastAPI Deployment Issue - Beginners - Hugging Face Forums, fecha de acceso: noviembre 6, 2025, https://discuss.huggingface.co/t/streamlit-fastapi-deployment-issue/86217
            14. How to generate and return a PDF file from in-memory buffer using FastAPI?, fecha de acceso: noviembre 6, 2025, https://stackoverflow.com/questions/76195784/how-to-generate-and-return-a-pdf-file-from-in-memory-buffer-using-fastapi
            15. Adding Text - fpdf2 - The py-pdf organization, fecha de acceso: noviembre 6, 2025, https://py-pdf.github.io/fpdf2/Text.html
            16. Get Started — Fairlearn 0.14.0.dev0 documentation, fecha de acceso: noviembre 6, 2025, https://fairlearn.org/main/quickstart.html
            17. fairlearn.postprocessing.ThresholdOptimizer, fecha de acceso: noviembre 6, 2025, https://fairlearn.org/v0.10/api_reference/generated/fairlearn.postprocessing.ThresholdOptimizer.html
            18. A Gentle Introduction to Probability Scoring Methods in Python - Machine Learning Mastery, fecha de acceso: noviembre 6, 2025, https://machinelearningmastery.com/how-to-score-probability-predictions-in-python/
            19. Understanding Model Calibration in Machine Learning | by Sahil Bansal - Medium, fecha de acceso: noviembre 6, 2025, https://medium.com/@sahilbansal480/understanding-model-calibration-in-machine-learning-6701814dbb3a
            20. xgboost - Optimising for Brier objective function directly gives worse Brier score than optimising with custom objective - what does it tell me?, fecha de acceso: noviembre 6, 2025, https://datascience.stackexchange.com/questions/71823/optimising-for-brier-objective-function-directly-gives-worse-brier-score-than-op
            21. How can I optimize boosted trees on Brier score for classification? - Stack Overflow, fecha de acceso: noviembre 6, 2025, https://stackoverflow.com/questions/52595782/how-can-i-optimize-boosted-trees-on-brier-score-for-classification
            22. Model calibration for classification tasks using Python | by Aayush Agrawal | Data Science at Microsoft | Medium, fecha de acceso: noviembre 6, 2025, https://medium.com/data-science-at-microsoft/model-calibration-for-classification-tasks-using-python-1a7093b57a46
            23. Probability Calibration - Python:Sklearn - Codecademy, fecha de acceso: noviembre 6, 2025, https://www.codecademy.com/resources/docs/sklearn/probability-calibration
            24. Brier Score: Understanding Model Calibration, fecha de acceso: noviembre 6, 2025, https://neptune.ai/blog/brier-score-and-model-calibration
            25. Probability Calibration Tutorial - Kaggle, fecha de acceso: noviembre 6, 2025, https://www.kaggle.com/code/kelixirr/probability-calibration-tutorial
            26. Shap Value for Single Record in Model Prediction - Wenlei Cao, fecha de acceso: noviembre 6, 2025, https://wenleicao.github.io/Shap_Value_for_Single_Record/
            27. langchain_core.output_parsers.pydantic.PydanticOutputParser — LangChain 0.2.17, fecha de acceso: noviembre 6, 2025, https://api.python.langchain.com/en/latest/output_parsers/langchain_core.output_parsers.pydantic.PydanticOutputParser.html
            28. How to Use Pydantic for LLMs: Schema, Validation & Prompts description, fecha de acceso: noviembre 6, 2025, https://pydantic.dev/articles/llm-intro
            29. Learn how to use JSON mode - Azure OpenAI, fecha de acceso: noviembre 6, 2025, https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/json-mode
            30. Introducing Structured Outputs in the API - OpenAI, fecha de acceso: noviembre 6, 2025, https://openai.com/index/introducing-structured-outputs-in-the-api/
            31. Structured output - Docs by LangChain, fecha de acceso: noviembre 6, 2025, https://docs.langchain.com/oss/python/langchain/structured-output
            32. langchain.chains.structured_output.base.create_structured_output_runnable, fecha de acceso: noviembre 6, 2025, https://api.python.langchain.com/en/latest/chains/langchain.chains.structured_output.base.create_structured_output_runnable.html
            33. Parsing LLM Structured Outputs in LangChain: A Comprehensive Guide - Medium, fecha de acceso: noviembre 6, 2025, https://medium.com/@juanc.olamendy/parsing-llm-structured-outputs-in-langchain-a-comprehensive-guide-f05ffa88261f
            34. langchain.chains.retrieval.create_retrieval_chain, fecha de acceso: noviembre 6, 2025, https://api.python.langchain.com/en/latest/chains/langchain.chains.retrieval.create_retrieval_chain.html
            35. RAG Hallucination: What is It and How to Avoid It, fecha de acceso: noviembre 6, 2025, https://www.k2view.com/blog/rag-hallucination/
            36. Tools to Detect & Reduce Hallucinations in a LangChain RAG Pipeline in Production, fecha de acceso: noviembre 6, 2025, https://traceloop.com/blog/tools-to-detect-reduce-hallucinations-in-a-langchain-rag-pipeline-in-production
            37. How to build RAG Applications that Reduce Hallucinations | AWS Builder Center, fecha de acceso: noviembre 6, 2025, https://builder.aws.com/content/2ddbSgLL6Ey1et3Cq2k2m6C2SvW/how-to-build-rag-applications-that-reduce-hallucinations
            38. How to return citations | 🦜️ Langchain, fecha de acceso: noviembre 6, 2025, https://js.langchain.com/docs/how_to/qa_citations/
            39. RetrievalQAWithSourcesChain — LangChain documentation, fecha de acceso: noviembre 6, 2025, https://python.langchain.com/api_reference/langchain/chains/langchain.chains.qa_with_sources.retrieval.RetrievalQAWithSourcesChain.html
            40. Streamlit to PDF: how to build & distribute PDF reports | by Niko Nelissen | Peliqan.io, fecha de acceso: noviembre 6, 2025, https://medium.com/peliqan-io/streamlit-to-pdf-f6f4a68fed3b
            41. Convert Text and Text File to PDF using Python - GeeksforGeeks, fecha de acceso: noviembre 6, 2025, https://www.geeksforgeeks.org/python/convert-text-and-text-file-to-pdf-using-python/
            42. Fairlearn, fecha de acceso: noviembre 6, 2025, https://fairlearn.org/
            43. fairlearn/fairlearn: A Python package to assess and improve fairness of machine learning models. - GitHub, fecha de acceso: noviembre 6, 2025, https://github.com/fairlearn/fairlearn
            44. Fairlearn: assessing and improving fairness of AI systems - GeeksforGeeks, fecha de acceso: noviembre 6, 2025, https://www.geeksforgeeks.org/machine-learning/fairlearn-assessing-and-improving-fairness-of-ai-systems/
            45. Machine learning fairness - Azure - Microsoft Learn, fecha de acceso: noviembre 6, 2025, https://learn.microsoft.com/en-us/azure/machine-learning/concept-fairness-ml?view=azureml-api-2
            46. A Unified Post-Processing Framework for Group Fairness in Classification - arXiv, fecha de acceso: noviembre 6, 2025, https://arxiv.org/html/2405.04025v2
            47. fairlearn.postprocessing.ThresholdOptimizer, fecha de acceso: noviembre 6, 2025, https://fairlearn.org/main/api_reference/generated/fairlearn.postprocessing.ThresholdOptimizer.html
            48. fairlearn.postprocessing package, fecha de acceso: noviembre 6, 2025, https://fairlearn.org/v0.4.6/api_reference/fairlearn.postprocessing.html
            49. Evaluate Model Fairness With FairLearn | by Rajat Roy - Medium, fecha de acceso: noviembre 6, 2025, https://iamrajatroy.medium.com/evaluate-model-fairness-with-fairlearn-97a8985074fd