from pydantic import BaseModel
from typing import Optional

class UsuarioCreate(BaseModel):
    """
    Esquema para crear o actualizar un perfil de usuario.
    Se usa al registrar datos adicionales después del login con Supabase.
    """
    name: Optional[str]
    edad: Optional[float]
    genero: Optional[str]
    altura: Optional[float]
    peso: Optional[float]


class UsuarioResponse(BaseModel):
    """
    Esquema de salida para devolver datos del usuario al frontend.
    """
    id: int
    name: Optional[str]
    edad: Optional[float]
    genero: Optional[str]
    altura: Optional[float]
    peso: Optional[float]

    class Config:
        from_attributes = True
