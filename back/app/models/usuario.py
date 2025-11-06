from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Usuario(BaseModel):
    """
    Representa el perfil extendido del usuario según la tabla 'profiles' en Supabase.
    No se usa SQLAlchemy, sino una estructura Pydantic compatible con Supabase SDK.
    """

    id: int
    created_at: datetime
    name: Optional[str] = None
    edad: Optional[float] = None
    genero: Optional[str] = None
    altura: Optional[float] = None
    peso: Optional[float] = None

    class Config:
        orm_mode = True
