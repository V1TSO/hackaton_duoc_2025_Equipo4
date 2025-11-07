import requests
import logging
from app.core.config import settings
from app.schemas.analisis_schema import AnalisisEntrada

logger = logging.getLogger(__name__)

def obtener_prediccion(data: AnalisisEntrada) -> dict:
    """
    Envía datos al modelo ML (Colab) y obtiene riesgo + drivers.
    Cumple con el requisito A4 (Explicabilidad).
    """
    
    # Convertimos el schema de Pydantic a un dict simple para la API de Colab
    data_dict = data.model_dump(mode='json', exclude_none=True)

    try:
        res = requests.post(settings.COLAB_URL, json=data_dict, timeout=10)
        res.raise_for_status()
        
        # EL ENDPOINT DE COLAB DEBE DEVOLVER ESTO:
        # Ej: {"riesgo": 0.45, "drivers": ["imc", "tabaquismo"]}
        ml_response = res.json() 

        # ---------------------------------------------------------------------------
        # REQUISITO A4: Extraer score y drivers
        # ---------------------------------------------------------------------------
        if "riesgo" not in ml_response or "drivers" not in ml_response:
            logger.error(f"Respuesta de Colab incompleta: {ml_response}")
            raise ValueError("La API de ML no devolvió 'riesgo' y 'drivers'")
            
        score = float(ml_response.get("riesgo"))
        drivers = list(ml_response.get("drivers", []))
        
        # Definir categoría (esto podría venir del modelo, pero está bien hacerlo aquí)
        if score < 0.33:
            categoria = "Bajo"
        elif score < 0.66:
            categoria = "Moderado"
        else:
            categoria = "Alto"

        return {
            "score": score,
            "drivers": drivers,
            "categoria_riesgo": categoria
        }
    
    except requests.exceptions.Timeout:
        logger.error("Timeout al conectar con el servicio de ML (Colab)")
        return {"error": "El servicio de predicción tardó mucho en responder."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al conectar con Colab: {e}")
        return {"error": "No se pudo obtener la predicción del modelo de ML."}
    except Exception as e:
        logger.error(f"Error procesando predicción: {e}")
        return {"error": f"Error inesperado en el servicio de ML: {e}"}