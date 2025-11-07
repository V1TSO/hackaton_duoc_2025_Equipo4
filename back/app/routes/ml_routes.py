# app/routes/ml_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date
from app.schemas.analisis_schema import (
    AnalisisEntrada, 
    PrediccionResultado, 
    CoachEntrada, 
    CoachResultado,
    AnalisisRegistro
)
from app.services.ml_service import obtener_prediccion
from app.core.security import verify_supabase_token
from app.core.database import guardar_analisis, obtener_historial_analisis
from app.core.config import settings
from app.ml.rag_system import RAGCoachSystem
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

_rag_system = None

def get_rag_system():
    """Get or initialize RAG system."""
    global _rag_system
    if _rag_system is None:
        kb_dir = str(settings.KB_DIR)
        _rag_system = RAGCoachSystem(kb_dir=kb_dir, api_key=settings.OPENAI_API_KEY)
    return _rag_system

# ENDPOINT 1: /predict (Requisito A4, C1)
# Rápido, solo devuelve el score y los drivers.
def _build_prediction_response(pred: dict) -> PrediccionResultado:
    return PrediccionResultado(
        score=pred["score"],
        drivers=pred["drivers"],
        categoria_riesgo=pred["categoria_riesgo"],
        model_used=pred.get("model_used", "diabetes")
    )


@router.post(
    "/predict", 
    response_model=PrediccionResultado,
    summary="1. Obtener Riesgo y Drivers (ML) [Default: diabetes]",
    tags=["Health (ML & Coach)"]
)
async def predecir_riesgo(
    data: AnalisisEntrada, 
    usuario=Depends(verify_supabase_token)
):
    """Endpoint legacy que utiliza el modelo por defecto (diabetes)."""

    pred = obtener_prediccion(data, model_type=data.modelo or "diabetes")

    if "error" in pred:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=pred["error"]
        )

    return _build_prediction_response(pred)


@router.post(
    "/predict/{model_type}",
    response_model=PrediccionResultado,
    summary="1b. Obtener Riesgo y Drivers por modelo",
    tags=["Health (ML & Coach)"]
)
async def predecir_riesgo_por_modelo(
    model_type: str,
    data: AnalisisEntrada,
    usuario=Depends(verify_supabase_token)
):
    """Permite escoger explícitamente el modelo (diabetes|cardiovascular)."""

    model_key = model_type.lower()
    if model_key not in {"diabetes", "cardiovascular"}:
        raise HTTPException(status_code=400, detail="Modelo no soportado")

    pred = obtener_prediccion(data, model_type=model_key)

    if "error" in pred:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=pred["error"]
        )

    return _build_prediction_response(pred)

# ENDPOINT 2: /coach (Requisito B2, B3)
# Orquesta el RAG, genera el plan y guarda en la BD.
@router.post(
    "/coach", 
    response_model=CoachResultado,
    summary="2. Obtener Plan de Acción (RAG) y Guardar",
    tags=["Health (ML & Coach)"]
)
async def obtener_plan_coach(
    data: CoachEntrada, 
    usuario=Depends(verify_supabase_token)
):
    """
    Recibe los resultados de /predict y los datos del usuario.
    1. Genera un plan de acción personalizado usando RAG (LLM + /kb).
    2. Guarda el análisis completo (entrada + predicción + plan) en Supabase.
    3. Devuelve el plan y las citas al frontend.
    
    Cumple con el Entregable: POST /coach
    Cumple con la Rúbrica: B2 (RAG) y B3 (Guardrails)
    """
    
    # 1. Generar el plan con RAG
    rag_system = get_rag_system()
    
    user_profile = {
        'edad': data.datos_usuario.edad,
        'age': data.datos_usuario.edad,
        'genero': data.datos_usuario.genero,
        'sex': data.datos_usuario.genero,
        'imc': data.datos_usuario.imc,
        'circunferencia_cintura': data.datos_usuario.circunferencia_cintura,
        'altura_cm': data.datos_usuario.altura_cm,
        'peso_kg': data.datos_usuario.peso_kg,
        'horas_sueno': data.datos_usuario.horas_sueno,
        'tabaquismo': data.datos_usuario.tabaquismo,
        'actividad_fisica': data.datos_usuario.actividad_fisica,
        'presion_sistolica': data.datos_usuario.presion_sistolica,
        'colesterol_total': data.datos_usuario.colesterol_total,
        'glucosa_mgdl': data.datos_usuario.glucosa_mgdl,
        'hdl_mgdl': data.datos_usuario.hdl_mgdl,
        'ldl_mgdl': data.datos_usuario.ldl_mgdl,
        'trigliceridos_mgdl': data.datos_usuario.trigliceridos_mgdl,
        'modelo': data.datos_usuario.modelo
    }
    
    drivers_list = [{'feature': d, 'description': d} for d in data.prediccion.drivers]
    
    try:
        result = rag_system.generate_plan(
            user_profile=user_profile,
            risk_score=data.prediccion.score,
            top_drivers=drivers_list
        )
        
        plan_ia = result['plan']
        citas = result.get('sources', [])
        
    except Exception as e:
        logger.error(f"Error generando plan con RAG: {e}", exc_info=True)
        plan_ia = "Error generando plan personalizado. Por favor, intenta nuevamente."
        citas = []

    # 2. Preparar datos para guardar en Supabase
    datos_completos = AnalisisRegistro(
        usuario_id=usuario["id"],
        fecha=data.datos_usuario.fecha,
        imc=data.datos_usuario.imc,
        circunferencia_cintura=data.datos_usuario.circunferencia_cintura,
        altura_cm=data.datos_usuario.altura_cm,
        peso_kg=data.datos_usuario.peso_kg,
        presion_sistolica=data.datos_usuario.presion_sistolica,
        colesterol_total=data.datos_usuario.colesterol_total,
        tabaquismo=data.datos_usuario.tabaquismo,
        actividad_fisica=data.datos_usuario.actividad_fisica,
        horas_sueno=data.datos_usuario.horas_sueno,
        edad=data.datos_usuario.edad,
        genero=data.datos_usuario.genero,
        glucosa_mgdl=data.datos_usuario.glucosa_mgdl,
        hdl_mgdl=data.datos_usuario.hdl_mgdl,
        trigliceridos_mgdl=data.datos_usuario.trigliceridos_mgdl,
        ldl_mgdl=data.datos_usuario.ldl_mgdl,
        modelo=data.prediccion.model_used,
        
        # Datos de salida
        riesgo_predicho=data.prediccion.score,
        categoria_riesgo=data.prediccion.categoria_riesgo,
        drivers=data.prediccion.drivers,
        recomendacion_ia=plan_ia,
        citas_kb=citas,
        fuente_modelo=data.prediccion.model_used or "NHANES_XGB_v1",
        model_used=data.prediccion.model_used
    )

    # 3. Guardar resultado en Supabase
    db_data = datos_completos.model_dump(exclude_unset=True)
    db_data.pop("id", None)
    db_data.pop("created_at", None)

    resultado_db = guardar_analisis(
        usuario_id=usuario["id"],
        datos=db_data
    )
    
    if "error" in resultado_db:
        # Nota: El plan se entrega al usuario aunque falle la BD
        print(f"Error al guardar en Supabase: {resultado_db['error']}")

    # 4. Devolver el plan al frontend
    return CoachResultado(
        plan_ia=plan_ia,
        citas_kb=citas,
        fuente_modelo=data.prediccion.model_used or "NHANES_XGB_v1",
        model_used=data.prediccion.model_used
    )

# (Tu endpoint de Historial está bien, pero ahora debe estar
# en 'users_routes.py' o aquí, pero no en ambos.)
# Lo movemos a 'users_routes.py' para mantener 'ml_routes' limpio.

# MUEVE TUS ENDPOINTS /history y /details/{id} a `users_routes.py`
# para que este archivo solo se ocupe de /predict y /coach.