from supabase import create_client, Client
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """
    Retorna una instancia singleton del cliente Supabase.
    """
    global _supabase_client
    if _supabase_client is None:
        try:
            url = settings.SUPABASE_URL
            key = settings.SUPABASE_ANON_KEY
            _supabase_client = create_client(url, key)
        except Exception as e:
            logger.error(f"Error al conectar con Supabase: {e}")
            raise RuntimeError("No se pudo crear el cliente Supabase")
    return _supabase_client


#analisis_salud
def guardar_analisis(usuario_id: str, datos: dict):
    supabase = get_supabase()
    try:
        data = {
            "usuario_id": usuario_id,
            "fecha": datos.get("fecha"),
            "imc": datos.get("imc"),
            "circunferencia_cintura": datos.get("circunferencia_cintura"),
            "presion_sistolica": datos.get("presion_sistolica"),
            "colesterol_total": datos.get("colesterol_total"),
            "tabaquismo": datos.get("tabaquismo"),
            "actividad_fisica": datos.get("actividad_fisica"),
            "horas_sueno": datos.get("horas_sueno"),
            "riesgo_predicho": datos.get("riesgo_predicho"),
            "categoria_riesgo": datos.get("categoria_riesgo"),
            "recomendacion_ia": datos.get("recomendacion_ia"),
            "fuente_modelo": datos.get("fuente_modelo", "NHANES_XGB_v1"),
        }
        res = supabase.table("analisis_salud").insert(data).execute()
        if getattr(res, "error", None):
            logger.error(f"Error Supabase al guardar análisis: {res.error}")
            return {"error": str(res.error)}
        logger.info("✅ Análisis guardado correctamente en Supabase.")
        return res.data
    except Exception as e:
        logger.error(f"Error al guardar análisis: {e}")
        return {"error": str(e)}


def obtener_historial_analisis(usuario_id: str):
    supabase = get_supabase()
    try:
        res = (
            supabase.table("analisis_salud")
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("fecha", desc=True)
            .execute()
        )
        if getattr(res, "error", None):
            logger.error(f"Error Supabase al obtener historial: {res.error}")
            return []
        return res.data or []
    except Exception as e:
        logger.error(f"Error al obtener historial de análisis: {e}")
        return []


#profiles
def obtener_perfil(usuario_id: str):
    supabase = get_supabase()
    try:
        res = (
            supabase.table("profiles")
            .select("*")
            .eq("id", usuario_id)
            .single()
            .execute()
        )
        if getattr(res, "error", None):
            logger.error(f"Error Supabase al obtener perfil: {res.error}")
            return None
        return res.data
    except Exception as e:
        logger.error(f"Error al obtener perfil del usuario: {e}")
        return None


def actualizar_perfil(usuario_id: str, datos: dict):
    supabase = get_supabase()
    try:
        res = (
            supabase.table("profiles")
            .update(datos)
            .eq("id", usuario_id)
            .execute()
        )
        if getattr(res, "error", None):
            logger.error(f"Error Supabase al actualizar perfil: {res.error}")
            return {"error": str(res.error)}
        return res.data
    except Exception as e:
        logger.error(f"Error al actualizar perfil: {e}")
        return {"error": str(e)}


#mensajes_agente
def guardar_mensaje_agente(usuario_id: str, rol: str, contenido: str, analisis_id: int | None = None):
    supabase = get_supabase()
    try:
        data = {
            "usuario_id": usuario_id,
            "rol": rol,
            "contenido": contenido,
        }
        if analisis_id is not None:
            data["analisis_id"] = analisis_id

        res = supabase.table("mensajes_agente").insert(data).execute()
        if getattr(res, "error", None):
            logger.error(f"Error Supabase al guardar mensaje agente: {res.error}")
            return {"error": str(res.error)}
        return res.data
    except Exception as e:
        logger.error(f"Error al guardar mensaje del agente: {e}")
        return {"error": str(e)}
