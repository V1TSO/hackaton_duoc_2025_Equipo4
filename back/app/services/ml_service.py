import requests
from app.core.config import settings

def obtener_prediccion(data: dict):
    """Envía datos al modelo ML (Colab) y obtiene riesgo"""
    try:
        res = requests.post(settings.COLAB_URL, json=data, timeout=10)
        res.raise_for_status()
        return res.json()  # Ej: {"riesgo": 0.45}
    except Exception as e:
        return {"error": f"No se pudo obtener predicción: {e}"}
