# app/routes/users_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_supabase_token
from app.core.database import obtener_perfil, actualizar_perfil, obtener_historial_analisis
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse

router = APIRouter()

#Endpoint: Obtener datos del usuario autenticado
@router.get("/me", response_model=UsuarioResponse)
async def obtener_usuario_actual(usuario=Depends(verify_supabase_token)):
    """
    Devuelve el perfil del usuario autenticado en Supabase.
    Si el perfil no existe, devuelve un error 404.
    """
    perfil = obtener_perfil(usuario["id"])
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el perfil del usuario en Supabase."
        )
    return perfil

#Endpoint: Actualizar datos del perfil
@router.put("/update", response_model=dict)
async def actualizar_datos_usuario(
    data: UsuarioCreate,
    usuario=Depends(verify_supabase_token)
):
    """
    Permite actualizar los datos básicos del perfil del usuario:
    nombre, edad, género, altura, peso, etc.
    """
    updated = actualizar_perfil(usuario["id"], data.dict(exclude_none=True))
    if isinstance(updated, dict) and "error" in updated:
        raise HTTPException(status_code=500, detail="Error al actualizar el perfil.")

    return {"message": "Perfil actualizado correctamente ✅"}

#Endpoint: Historial de análisis del usuario
@router.get("/history")
async def obtener_historial_usuario(usuario=Depends(verify_supabase_token)):
    """
    Devuelve el historial de análisis del usuario autenticado,
    ordenado por fecha descendente.
    """
    historial = obtener_historial_analisis(usuario["id"])
    if not historial:
        return {"message": "No se encontraron análisis previos para este usuario."}

    return {
        "usuario_id": usuario["id"],
        "cantidad": len(historial),
        "historial": historial
    }

#Endpoint: Eliminar perfil de usuario
@router.delete("/delete")
async def eliminar_perfil(usuario=Depends(verify_supabase_token)):
    """
    Elimina el perfil del usuario de la tabla 'profiles' en Supabase.
    (No borra su cuenta de Supabase Auth).
    """
    from app.core.database import get_supabase
    supabase = get_supabase()
    try:
        res = supabase.table("profiles").delete().eq("id", usuario["id"]).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="El perfil no fue encontrado o ya fue eliminado.")
        return {"message": "Perfil eliminado correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el perfil: {e}")

#Endpoint: Resetear toda la cuenta del usuario
@router.delete("/reset-account")
async def resetear_cuenta_completa(usuario=Depends(verify_supabase_token)):
    """
    Elimina TODOS los datos del usuario: mensajes, sesiones, assessments y análisis.
    Esta es una operación destructiva que resetea completamente la cuenta del usuario.
    La cuenta de autenticación en Supabase Auth NO se elimina.
    """
    from app.core.database import delete_all_user_data
    access_token = usuario.get("_access_token")
    
    result = delete_all_user_data(usuario["id"], access_token)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return {
        "message": "Cuenta reseteada correctamente. Todos tus datos han sido eliminados.",
        "deleted": result.get("deleted", {}),
        "total": result.get("total", 0)
    }
