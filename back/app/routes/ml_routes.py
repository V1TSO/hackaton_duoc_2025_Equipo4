# app/routes/ml_routes.py
from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from app.schemas.analisis_schema import AnalisisEntrada, AnalisisResultado
from app.services.ml_service import obtener_prediccion
from app.agents.openai_agent import generar_consejo_salud
from app.core.security import verify_supabase_token
from app.core.database import guardar_analisis, obtener_historial_analisis, get_supabase

router = APIRouter()

#Endpoint principal: /predict
@router.post("/predict", response_model=AnalisisResultado)
async def analizar_salud(data: AnalisisEntrada, usuario=Depends(verify_supabase_token)):
    """
    Envía los datos del usuario al modelo ML (Colab), obtiene el riesgo estimado
    y genera una recomendación personalizada con el agente IA.
    Luego guarda el resultado completo en Supabase.
    """
    # Llamada al modelo de Machine Learning (Colab)
    pred = obtener_prediccion(data.dict())
    if "error" in pred:
        return AnalisisResultado(
            riesgo_predicho=0.0,
            categoria_riesgo="Desconocido",
            recomendacion_ia=pred["error"],
        )

    riesgo = pred.get("riesgo", 0.5)
    categoria = "Bajo" if riesgo < 0.33 else "Moderado" if riesgo < 0.66 else "Alto"
    recomendacion = generar_consejo_salud(riesgo)

    # Guardar resultado en Supabase
    guardar_analisis(
        usuario_id=usuario["id"],
        datos={
            "fecha": date.today(),
            "imc": data.imc,
            "circunferencia_cintura": data.circunferencia_cintura,
            "presion_sistolica": data.presion_sistolica,
            "colesterol_total": data.colesterol_total,
            "tabaquismo": data.tabaquismo,
            "actividad_fisica": data.actividad_fisica,
            "horas_sueno": data.horas_sueno,
            "riesgo_predicho": riesgo,
            "categoria_riesgo": categoria,
            "recomendacion_ia": recomendacion,
        },
    )

    return AnalisisResultado(
        riesgo_predicho=riesgo,
        categoria_riesgo=categoria,
        recomendacion_ia=recomendacion,
    )

#Endpoint de historial: /history
@router.get("/history")
async def obtener_historial(usuario=Depends(verify_supabase_token)):
    """
    Devuelve todos los análisis guardados del usuario autenticado.
    Los resultados se obtienen directamente desde Supabase.
    """
    historial = obtener_historial_analisis(usuario["id"])
    if not historial:
        return {"message": "No se encontraron análisis previos para este usuario."}

    return {
        "usuario_id": usuario["id"],
        "cantidad": len(historial),
        "historial": historial,
    }

#Endpoint de detalle: /details/{id}
@router.get("/details/{id}")
async def obtener_detalle_analisis(id: int, usuario=Depends(verify_supabase_token)):
    """
    Devuelve un análisis específico por ID.
    Incluye los campos originales del análisis y la recomendación IA.
    """
    supabase = get_supabase()
    try:
        res = (
            supabase.table("analisis_salud")
            .select("*")
            .eq("id", id)
            .eq("usuario_id", usuario["id"])
            .single()
            .execute()
        )

        if not res.data:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el análisis con ID {id} para este usuario.",
            )

        return res.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalle: {e}")
