# back/app/schemas/analisis_schema.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# ---------------------------------------------------------------------------
# REQUISITO B1: JSON Schema de entrada (Tu archivo original está bien)
# ---------------------------------------------------------------------------
class AnalisisEntrada(BaseModel):
    """
    Representa los datos de entrada que el usuario entrega para el análisis
    de salud cardiometabólico.
    """
    fecha: Optional[date] = date.today()
    imc: Optional[float] = None
    circunferencia_cintura: Optional[float] = None
    presion_sistolica: Optional[float] = None
    colesterol_total: Optional[float] = None # ¡Cuidado! Asegúrate que esto no sea un "data leak" (Rúbrica 4)
    tabaquismo: Optional[bool] = None
    actividad_fisica: Optional[str] = None # Ej: "sedentario", "moderado", "activo"
    horas_sueno: Optional[float] = None
    
    # Datos demográficos (Necesarios para el ML)
    edad: Optional[int] = None 
    genero: Optional[str] = None # Ej: "M", "F"

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# REQUISITO A4: Respuesta del endpoint /predict
# (Este schema es NUEVO y CRÍTICO)
# ---------------------------------------------------------------------------
class PrediccionResultado(BaseModel):
    """
    Respuesta del endpoint /predict.
    Debe devolver el score y los drivers (explicabilidad).
    """
    score: float # El riesgo predicho (0.0 a 1.0)
    drivers: List[str] # Lista de las 3-5 features que más influyeron
    categoria_riesgo: str # "Bajo", "Moderado", "Alto"

    class Config:
        from_attributes = True

# ---------------------------------------------------------------------------
# REQUISITO B2: Entrada para el endpoint /coach
# (Este schema es NUEVO y CRÍTICO)
# ---------------------------------------------------------------------------
class CoachEntrada(BaseModel):
    """
    Datos de entrada para el endpoint /coach.
    Necesita el resultado de /predict y los datos del usuario
    para generar el plan RAG.
    """
    prediccion: PrediccionResultado
    datos_usuario: AnalisisEntrada


# ---------------------------------------------------------------------------
# REQUISITO B2: Respuesta del endpoint /coach
# (Modificado desde tu 'AnalisisResultado')
# ---------------------------------------------------------------------------
class CoachResultado(BaseModel):
    """
    Representa el resultado del coach (LLM + RAG) que se envía al frontend.
    Incluye el plan y las citas a la base de conocimiento.
    """
    plan_ia: str # El plan de acción (tu 'recomendacion_ia' renombrada)
    citas_kb: List[str] # Lista de fuentes de /kb usadas (REQUISITO B2)
    fuente_modelo: str = "NHANES_XGB_v1" # Esto está bien

    class Config:
        from_attributes = True

# ---------------------------------------------------------------------------
# (Tu 'AnalisisRegistro' para la BD, pero actualizado
# para guardar los nuevos campos de la rúbrica)
# ---------------------------------------------------------------------------
class AnalisisRegistro(BaseModel):
    """
    Estructura que se guarda en Supabase (tabla analisis_salud).
    Combina los datos de entrada + salida + metadatos.
    """
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    usuario_id: Optional[str] = None

    # Datos de entrada
    fecha: Optional[date] = None
    imc: Optional[float] = None
    circunferencia_cintura: Optional[float] = None
    presion_sistolica: Optional[float] = None
    colesterol_total: Optional[float] = None
    tabaquismo: Optional[bool] = None
    actividad_fisica: Optional[str] = None
    horas_sueno: Optional[float] = None
    edad: Optional[int] = None
    genero: Optional[str] = None

    # Datos de salida (predicción + coach)
    riesgo_predicho: Optional[float] = None
    categoria_riesgo: Optional[str] = None
    drivers: Optional[List[str]] = None # ¡Guardar los drivers!
    recomendacion_ia: Optional[str] = None # El plan
    citas_kb: Optional[List[str]] = None # ¡Guardar las citas!
    fuente_modelo: Optional[str] = "NHANES_XGB_v1"

    class Config:
        from_attributes = True