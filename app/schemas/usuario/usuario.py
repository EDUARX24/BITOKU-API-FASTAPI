from pydantic import BaseModel, ConfigDict, field_validator

from app.core.enums import UserRole, normalize_role


class UsuarioBase(BaseModel):
    """Esquema base para usuario (nombre y rol)."""

    nombreUsuario: str
    rol: UserRole

    @field_validator("rol", mode="before")
    @classmethod
    def validate_role(cls, value):
        normalized = normalize_role(value)
        if normalized not in {role.value for role in UserRole}:
            raise ValueError("Rol inválido. Use adm, doc o ptn.")
        return normalized


class UsuarioCreate(UsuarioBase):
    """Esquema para crear usuario (incluye contraseña)."""

    contrasenia: str


class UsuarioOut(UsuarioBase):
    """Esquema de salida para usuario (incluye id)."""

    idUsuario: int
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str
