from fastapi import Header, HTTPException, status
import requests
from app.core.config import settings

async def verify_supabase_token(authorization: str = Header(None)):
    """
    Verifica el JWT emitido por Supabase.
    Si es válido, retorna el objeto de usuario.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido"
        )

    token = authorization.split(" ")[1]

    try:
        res = requests.get(
            f"{settings.SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.SUPABASE_ANON_KEY,
            },
            timeout=5,
        )
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo verificar el token (Supabase no disponible)"
        )

    if res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    return res.json()
