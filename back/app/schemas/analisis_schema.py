from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

#Entrada (lo que el usuario envía desde el frontend)
class AnalisisEntrada(BaseModel):
    """
    Representa los datos de entrada que el usuario entrega para el análisis
    de salud cardiometabólico. Estos se envían al modelo de ML (Colab).
    """
    fecha: Optional[date] = None
    imc: Optional[float] = None
    circunferencia_cintura: Optional[float] = None
    presion_sistolica: Optional[float] = None
    colesterol_total: Optional[float] = None
    tabaquismo: Optional[bool] = None
    actividad_fisica: Optional[str] = None
    horas_sueno: Optional[float] = None

    class Config:
        orm_mode = True

#Resultado (respuesta del modelo + IA)
class AnalisisResultado(BaseModel):
    """
    Representa el resultado del análisis que se envía al frontend.
    Incluye el riesgo calculado, la categoría y el mensaje del agente IA.
    """
    riesgo_predicho: float
    categoria_riesgo: str
    recomendacion_ia: str
    fuente_modelo: str = "NHANES_XGB_v1"

    class Config:
        orm_mode = True

#Registro completo (para guardar en Supabase)
class AnalisisRegistro(BaseModel):
    """
    Estructura que se guarda en Supabase (tabla analisis_salud).
    Combina los datos de entrada + salida + metadatos.
    """
    id: Optional[int]
    created_at: Optional[datetime]
    fecha: Optional[date]
    imc: Optional[float]
    circunferencia_cintura: Optional[float]
    presion_sistolica: Optional[float]
    colesterol_total: Optional[float]
    tabaquismo: Optional[bool]
    actividad_fisica: Optional[str]
    horas_sueno: Optional[float]
    riesgo_predicho: Optional[float]
    categoria_riesgo: Optional[str]
    recomendacion_ia: Optional[str]
    fuente_modelo: Optional[str]
    usuario_id: Optional[str]

    class Config:
        from_attributes = True
