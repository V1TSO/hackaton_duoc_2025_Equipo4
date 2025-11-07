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
from app.agents.openai_agent import generar_plan_con_rag # Importamos el nuevo agente RAG
from app.core.security import verify_supabase_token
from app.core.database import guardar_analisis, obtener_historial_analisis

router = APIRouter()

# ENDPOINT 1: /predict (Requisito A4, C1)
# Rápido, solo devuelve el score y los drivers.
@router.post(
    "/predict", 
    response_model=PrediccionResultado,
    summary="1. Obtener Riesgo y Drivers (ML)",
    tags=["Health (ML & Coach)"]
)
async def predecir_riesgo(
    data: AnalisisEntrada, 
    usuario=Depends(verify_supabase_token)
):
    """
    Envía los datos del usuario al modelo ML (Colab).
    Responde con el score de riesgo (0-1), la categoría
    y los 'drivers' (factores clave) de la predicción.
    
    Cumple con el Entregable: POST /predict
    Cumple con la Rúbrica: A4 (Explicabilidad)
    """
    
    # 1. Llamada al modelo de Machine Learning (Colab)
    pred = obtener_prediccion(data)
    
    if "error" in pred:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=pred["error"]
        )

    return PrediccionResultado(
        score=pred["score"],
        drivers=pred["drivers"],
        categoria_riesgo=pred["categoria_riesgo"]
    )

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
    plan_ia, citas = generar_plan_con_rag(
        prediccion=data.prediccion,
        datos=data.datos_usuario
    )

    # 2. Preparar datos para guardar en Supabase
    datos_completos = AnalisisRegistro(
        usuario_id=usuario["id"],
        fecha=data.datos_usuario.fecha,
        imc=data.datos_usuario.imc,
        circunferencia_cintura=data.datos_usuario.circunferencia_cintura,
        presion_sistolica=data.datos_usuario.presion_sistolica,
        colesterol_total=data.datos_usuario.colesterol_total,
        tabaquismo=data.datos_usuario.tabaquismo,
        actividad_fisica=data.datos_usuario.actividad_fisica,
        horas_sueno=data.datos_usuario.horas_sueno,
        edad=data.datos_usuario.edad,
        genero=data.datos_usuario.genero,
        
        # Datos de salida
        riesgo_predicho=data.prediccion.score,
        categoria_riesgo=data.prediccion.categoria_riesgo,
        drivers=data.prediccion.drivers,
        recomendacion_ia=plan_ia,
        citas_kb=citas
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
        citas_kb=citas
    )

# (Tu endpoint de Historial está bien, pero ahora debe estar
# en 'users_routes.py' o aquí, pero no en ambos.)
# Lo movemos a 'users_routes.py' para mantener 'ml_routes' limpio.

# MUEVE TUS ENDPOINTS /history y /details/{id} a `users_routes.py`
# para que este archivo solo se ocupe de /predict y /coach.