# app/routes/debug_routes.py

from fastapi import APIRouter
from app.core.database import get_supabase

router = APIRouter()

@router.get("/supabase")
def debug_supabase():
    """
    Verifica la conexión con Supabase intentando leer la tabla profiles.
    Solo para desarrollo.
    """
    client = get_supabase()
    try:
        res = client.table("profiles").select("id").limit(1).execute()
        return {
            "status": "ok",
            "rows_en_profiles": len(res.data) if res.data else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }
