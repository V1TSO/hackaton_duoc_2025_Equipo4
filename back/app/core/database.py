from supabase import create_client, Client
from app.core.config import settings
import logging
import uuid
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_supabase_client: Client | None = None


def get_supabase(access_token: Optional[str] = None) -> Client:
    """
    Retorna un cliente Supabase. Si se proporciona access_token,
    crea un cliente con ese token para respetar RLS policies.
    """
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_ANON_KEY
    
    if not url or not key:
        raise RuntimeError("Supabase no está configurado. Configure SUPABASE_URL y SUPABASE_ANON_KEY")
    
    if access_token:
        # Create a client with the user's JWT token for RLS
        client = create_client(url, key)
        client.postgrest.auth(access_token)
        return client
    
    # Use singleton for service role operations
    global _supabase_client
    if _supabase_client is None:
        try:
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
            .execute()
        )
        if getattr(res, "error", None):
            logger.error(f"Error Supabase al obtener perfil: {res.error}")
            return None
        return res.data[0] if res.data and len(res.data) > 0 else None
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

def get_or_create_session(user_id: str, session_id: str | None = None, access_token: Optional[str] = None) -> dict:
    """
    Busca una sesión por ID. Si no existe o es nula, crea una nueva.
    """
    supabase = get_supabase(access_token)
    
    if session_id:
        try:
            res = supabase.table("chat_sessions").select("*").eq("id", session_id).eq("user_id", user_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.warning(f"No se encontró sesión {session_id}, creando una nueva: {e}")

    # No se encontró sesión o no se proveyó ID, crear una nueva
    try:
        new_session = {
            "user_id": user_id,
            "title": "Nueva Conversación" # El default de tu schema de BD
        }
        res = supabase.table("chat_sessions").insert(new_session).execute()
        if res.data and len(res.data) > 0:
            logger.info(f"Nueva sesión de chat creada: {res.data[0]['id']}")
            return res.data[0]
        else:
            raise Exception(f"No se pudo crear la sesión: {getattr(res, 'error', 'Error desconocido')}")
    except Exception as e:
        logger.error(f"Error crítico al crear sesión: {e}")
        return {"error": str(e)}

def get_messages_by_session(session_id: str, access_token: Optional[str] = None) -> List[dict]:
    """
    Obtiene todo el historial de mensajes de una sesión, ordenado.
    """
    supabase = get_supabase(access_token)
    try:
        res = (
            supabase.table("chat_messages")
            .select("*") # Seleccionar todos los campos para el schema ChatMessage
            .eq("session_id", session_id)
            .order("created_at", desc=False) # El más antiguo primero
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.error(f"Error al obtener historial de mensajes: {e}")
        return []

def save_chat_message(session_id: str, role: str, content: str, access_token: Optional[str] = None) -> dict:
    """
    Guarda un nuevo mensaje (de 'user' o 'assistant') en la BD.
    """
    supabase = get_supabase(access_token)
    try:
        message = {
            "session_id": session_id,
            "role": role,
            "content": content
        }
        res = supabase.table("chat_messages").insert(message).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        else:
            raise Exception(f"No se pudo guardar el mensaje: {getattr(res, 'error', 'Error desconocido')}")
    except Exception as e:
        logger.error(f"Error al guardar mensaje: {e}")
        return {"error": str(e)}

def link_assessment_to_session(session_id: str, assessment_id: str, access_token: Optional[str] = None):
    """
    (Opcional pero recomendado) Vincula la predicción (assessment)
    con la sesión de chat que la generó.
    """
    supabase = get_supabase(access_token)
    try:
        supabase.table("chat_sessions").update({"assessment_id": assessment_id}).eq("id", session_id).execute()
        logger.info(f"Sesión {session_id} vinculada a assessment {assessment_id}")
    except Exception as e:
        logger.error(f"Error al vincular assessment: {e}")

def delete_chat_session(session_id: str, user_id: str, access_token: Optional[str] = None) -> dict:
    """
    Elimina una sesión de chat y todos sus mensajes asociados.
    Solo puede eliminar sesiones del usuario autenticado.
    """
    supabase = get_supabase(access_token)
    try:
        # Primero verificar que la sesión pertenece al usuario
        session_check = supabase.table("chat_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
        if not session_check.data or len(session_check.data) == 0:
            return {"error": "Sesión no encontrada o no autorizada"}
        
        # Eliminar todos los mensajes de la sesión
        supabase.table("chat_messages").delete().eq("session_id", session_id).execute()
        logger.info(f"Mensajes de la sesión {session_id} eliminados")
        
        # Eliminar la sesión
        supabase.table("chat_sessions").delete().eq("id", session_id).execute()
        logger.info(f"Sesión {session_id} eliminada")
        
        return {"success": True, "message": "Sesión eliminada correctamente"}
    except Exception as e:
        logger.error(f"Error al eliminar sesión: {e}")
        return {"error": str(e)}

def delete_all_user_data(user_id: str, access_token: Optional[str] = None) -> dict:
    """
    Elimina TODOS los datos del usuario: mensajes, sesiones, assessments y análisis.
    Esta es una operación destructiva que resetea completamente la cuenta del usuario.
    """
    supabase = get_supabase(access_token)
    try:
        deleted_counts = {
            "messages": 0,
            "sessions": 0,
            "assessments": 0,
            "analisis": 0
        }
        
        # 1. Obtener todas las sesiones del usuario para eliminar mensajes
        sessions_res = supabase.table("chat_sessions").select("id").eq("user_id", user_id).execute()
        session_ids = [s["id"] for s in (sessions_res.data or [])]
        
        # 2. Eliminar todos los mensajes de las sesiones del usuario
        if session_ids:
            messages_res = supabase.table("chat_messages").delete().in_("session_id", session_ids).execute()
            deleted_counts["messages"] = len(messages_res.data or [])
            logger.info(f"Eliminados {deleted_counts['messages']} mensajes del usuario {user_id}")
        
        # 3. Eliminar todas las sesiones del usuario
        sessions_res = supabase.table("chat_sessions").delete().eq("user_id", user_id).execute()
        deleted_counts["sessions"] = len(sessions_res.data or [])
        logger.info(f"Eliminadas {deleted_counts['sessions']} sesiones del usuario {user_id}")
        
        # 4. Eliminar todos los assessments del usuario
        assessments_res = supabase.table("assessments").delete().eq("user_id", user_id).execute()
        deleted_counts["assessments"] = len(assessments_res.data or [])
        logger.info(f"Eliminados {deleted_counts['assessments']} assessments del usuario {user_id}")
        
        # 5. Eliminar todos los análisis del usuario (si existe la tabla)
        try:
            analisis_res = supabase.table("analisis_salud").delete().eq("usuario_id", user_id).execute()
            deleted_counts["analisis"] = len(analisis_res.data or [])
            logger.info(f"Eliminados {deleted_counts['analisis']} análisis del usuario {user_id}")
        except Exception as e:
            logger.warning(f"No se pudo eliminar de analisis_salud (puede que no exista): {e}")
        
        total_deleted = sum(deleted_counts.values())
        logger.info(f"✅ Reset completo de cuenta: {total_deleted} registros eliminados para usuario {user_id}")
        
        return {
            "success": True,
            "message": "Todos los datos han sido eliminados correctamente",
            "deleted": deleted_counts,
            "total": total_deleted
        }
    except Exception as e:
        logger.error(f"Error al eliminar todos los datos del usuario: {e}")
        return {"error": str(e)}

def save_assessment(user_id: str, data: dict, access_token: Optional[str] = None) -> dict:
    """
    Guarda el resultado de la predicción en la nueva tabla 'assessments'.
    """
    supabase = get_supabase(access_token)
    try:
        assessment_payload = dict(data)
        raw_assessment_data = assessment_payload.get("assessment_data", {}) or {}
        
        # Extraer plan_text y citations de raw_assessment_data (donde realmente están)
        plan_text = raw_assessment_data.pop("plan_text", None)
        citations = raw_assessment_data.pop("citations", None)
        model_used_from_data = raw_assessment_data.pop("model_used", None)
        
        # Enriquecer assessment_data con plan_text y citations
        enriched_assessment_data = {
            **raw_assessment_data,
            "plan_text": plan_text,
            "citations": citations or [],
        }

        # El model_used puede venir del nivel superior o de assessment_data
        model_used = assessment_payload.pop("model_used", None) or model_used_from_data
        if model_used:
            enriched_assessment_data.setdefault("model_used", model_used)
        
        logger.info(f"Guardando assessment con plan_text: {plan_text is not None and len(plan_text) > 0 if plan_text else False}, citations: {len(citations) if citations else 0}")

        risk_level = assessment_payload.get("risk_level")
        if risk_level is not None:
            risk_mapping = {
                "Bajo": "low",
                "Moderado": "moderate",
                "Alto": "high",
                "low": "low",
                "moderate": "moderate",
                "high": "high",
            }
            normalized_risk = risk_mapping.get(risk_level, str(risk_level).lower())
            assessment_payload["risk_level"] = normalized_risk
            logger.info(f"Normalized risk_level from '{risk_level}' to '{normalized_risk}'")
 
        assessment_payload["assessment_data"] = enriched_assessment_data
        assessment_payload["user_id"] = user_id
        
        # Convertir drivers (DriverExplicacion) a diccionarios si son objetos Pydantic
        if "drivers" in assessment_payload:
            drivers = assessment_payload["drivers"]
            if drivers and len(drivers) > 0:
                # Verificar si el primer driver es un objeto (tiene método model_dump o dict)
                first_driver = drivers[0]
                if hasattr(first_driver, 'model_dump'):
                    # Es un modelo Pydantic v2
                    assessment_payload["drivers"] = [d.model_dump() for d in drivers]
                elif hasattr(first_driver, 'dict'):
                    # Es un modelo Pydantic v1
                    assessment_payload["drivers"] = [d.dict() for d in drivers]
                elif isinstance(first_driver, dict):
                    # Ya es un diccionario
                    pass
                else:
                    # Intentar convertir a dict de otra forma
                    try:
                        assessment_payload["drivers"] = [dict(d) for d in drivers]
                    except:
                        logger.warning(f"No se pudo convertir drivers a diccionarios: {type(first_driver)}")
        
        # Log final antes de guardar
        final_plan_text = enriched_assessment_data.get("plan_text")
        final_citations = enriched_assessment_data.get("citations", [])
        logger.info(f"💾 Guardando en BD - plan_text: {final_plan_text is not None and len(final_plan_text) > 0 if final_plan_text else False} ({len(final_plan_text) if final_plan_text else 0} chars), citations: {len(final_citations)}")
        
        res = supabase.table("assessments").insert(assessment_payload).execute()
        if res.data and len(res.data) > 0:
            saved_assessment_data = res.data[0].get("assessment_data", {})
            saved_plan_text = saved_assessment_data.get("plan_text") if isinstance(saved_assessment_data, dict) else None
            logger.info(f"✅ Assessment guardado ID: {res.data[0]['id']}, plan_text guardado: {saved_plan_text is not None and len(saved_plan_text) > 0 if saved_plan_text else False}")
            return res.data[0]
        else:
            raise Exception(f"No se pudo guardar el assessment: {getattr(res, 'error', 'Error desconocido')}")
    except Exception as e:
        logger.error(f"Error al guardar assessment: {e}")
        return {"error": str(e)}