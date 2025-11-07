from supabase import create_client, Client
from app.core.config import settings
import logging
import uuid
from typing import List

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
        # Asegurarnos que el usuario_id esté en el dict
        datos["usuario_id"] = usuario_id
        
        # Quitamos campos que Supabase genera
        datos.pop("id", None)
        datos.pop("created_at", None)

        res = supabase.table("analisis_salud").insert(datos).execute()
        
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

def get_or_create_session(user_id: str, session_id: str | None = None) -> dict:
    """
    Busca una sesión por ID. Si no existe o es nula, crea una nueva.
    """
    supabase = get_supabase()
    
    if session_id:
        try:
            res = supabase.table("chat_sessions").select("*").eq("id", session_id).eq("user_id", user_id).single().execute()
            if res.data:
                return res.data
        except Exception as e:
            logger.warning(f"No se encontró sesión {session_id}, creando una nueva: {e}")

    # No se encontró sesión o no se proveyó ID, crear una nueva
    try:
        new_session = {
            "user_id": user_id,
            "title": "Nueva Conversación" # El default de tu schema de BD
        }
        res = supabase.table("chat_sessions").insert(new_session).select("*").single().execute()
        if res.data:
            logger.info(f"Nueva sesión de chat creada: {res.data['id']}")
            return res.data
        else:
            raise Exception(f"No se pudo crear la sesión: {getattr(res, 'error', 'Error desconocido')}")
    except Exception as e:
        logger.error(f"Error crítico al crear sesión: {e}")
        return {"error": str(e)}

def get_messages_by_session(session_id: str) -> List[dict]:
    """
    Obtiene todo el historial de mensajes de una sesión, ordenado.
    """
    supabase = get_supabase()
    try:
        res = (
            supabase.table("chat_messages")
            .select("role, content") # Solo necesitamos rol y contenido para el LLM
            .eq("session_id", session_id)
            .order("created_at", desc=False) # El más antiguo primero
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.error(f"Error al obtener historial de mensajes: {e}")
        return []

def save_chat_message(session_id: str, role: str, content: str) -> dict:
    """
    Guarda un nuevo mensaje (de 'user' o 'assistant') en la BD.
    """
    supabase = get_supabase()
    try:
        message = {
            "session_id": session_id,
            "role": role,
            "content": content
        }
        res = supabase.table("chat_messages").insert(message).select("*").single().execute()
        if res.data:
            return res.data
        else:
            raise Exception(f"No se pudo guardar el mensaje: {getattr(res, 'error', 'Error desconocido')}")
    except Exception as e:
        logger.error(f"Error al guardar mensaje: {e}")
        return {"error": str(e)}

def link_assessment_to_session(session_id: str, assessment_id: str):
    """
    (Opcional pero recomendado) Vincula la predicción (assessment)
    con la sesión de chat que la generó.
    """
    supabase = get_supabase()
    try:
        supabase.table("chat_sessions").update({"assessment_id": assessment_id}).eq("id", session_id).execute()
        logger.info(f"Sesión {session_id} vinculada a assessment {assessment_id}")
    except Exception as e:
        logger.error(f"Error al vincular assessment: {e}")

def save_assessment(user_id: str, data: dict) -> dict:
    """
    Guarda el resultado de la predicción en la nueva tabla 'assessments'.
    """
    supabase = get_supabase()
    try:
        # 'data' debe contener: assessment_data, risk_score, risk_level, drivers
        data["user_id"] = user_id
        res = supabase.table("assessments").insert(data).select("*").single().execute()
        if res.data:
            logger.info(f"Nuevo assessment guardado: {res.data['id']}")
            return res.data
        else:
            raise Exception(f"No se pudo guardar el assessment: {getattr(res, 'error', 'Error desconocido')}")
    except Exception as e:
        logger.error(f"Error al guardar assessment: {e}")
        return {"error": str(e)}