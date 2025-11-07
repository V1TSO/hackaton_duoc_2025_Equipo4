import logging
from app.schemas.analisis_schema import AnalisisEntrada
from app.ml.predictor import predict_risk

logger = logging.getLogger(__name__)

def obtener_prediccion(data: AnalisisEntrada, model_type: str | None = None) -> dict:
    """
    Obtiene predicción de riesgo usando el modelo ML local.
    Cumple con el requisito A4 (Explicabilidad).
    """
    
    try:
        height_cm = data.altura_cm
        weight_kg = data.peso_kg
        
        selected_model = (model_type or data.modelo or "diabetes").lower()

        if data.imc is not None:
            bmi = data.imc
        elif height_cm is not None and weight_kg is not None:
            try:
                bmi = weight_kg / ((height_cm / 100) ** 2)
            except ZeroDivisionError:
                bmi = None
        else:
            bmi = None
        
        waist_cm = data.circunferencia_cintura
        
        sleep_hours = data.horas_sueno
        
        smokes_cig_day = None
        if data.tabaquismo is not None:
            smokes_cig_day = 10 if data.tabaquismo else 0
        
        days_mvpa_week = None
        if data.actividad_fisica is not None:
            activity_map = {
                "sedentario": 0,
                "ligero": 2,
                "moderado": 4,
                "activo": 6,
                "muy_activo": 7
            }
            days_mvpa_week = activity_map.get(data.actividad_fisica.lower(), 0)
        
        result = predict_risk(
            age=data.edad,
            sex=data.genero,
            height_cm=height_cm,
            weight_kg=weight_kg,
            waist_cm=waist_cm,
            sleep_hours=sleep_hours,
            smokes_cig_day=smokes_cig_day,
            days_mvpa_week=days_mvpa_week,
            bmi=bmi,
            systolic_bp=data.presion_sistolica,
            total_cholesterol=data.colesterol_total,
            model_type=selected_model,
            glucosa_mgdl=data.glucosa_mgdl,
            hdl_mgdl=data.hdl_mgdl,
            trigliceridos_mgdl=data.trigliceridos_mgdl,
            ldl_mgdl=data.ldl_mgdl
        )
        
        drivers_list = [d['feature'] for d in result['drivers']]
        
        return {
            "score": result["score"],
            "drivers": drivers_list,
            "categoria_riesgo": result["risk_level"],
            "model_used": result.get("model_used", selected_model)
        }
    
    except Exception as e:
        logger.error(f"Error procesando predicción: {e}", exc_info=True)
        return {"error": f"Error inesperado en el servicio de ML: {e}"}