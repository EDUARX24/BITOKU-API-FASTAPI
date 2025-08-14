
from pydantic import BaseModel

class UsuarioBase(BaseModel):
    """Esquema base para usuario (nombre y rol)."""
    nombreUsuario: str
    rol: str

class UsuarioCreate(UsuarioBase):
    """Esquema para crear usuario (incluye contraseña)."""
    contrasenia: str

class UsuarioOut(UsuarioBase):
    """Esquema de salida para usuario (incluye id)."""
    idUsuario: int
    class Config:
        from_attributes = True
