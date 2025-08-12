from pydantic import BaseModel

class UsuarioBase(BaseModel):
    nombreUsuario: str
    rol: str

class UsuarioCreate(UsuarioBase):
    contrasenia: str

class UsuarioOut(UsuarioBase):
    idUsuario: int
    class Config:
        from_attributes = True
