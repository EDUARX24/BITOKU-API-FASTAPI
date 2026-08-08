from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.enums import Sex, normalize_sex


class PacienteBase(BaseModel):
    nombrePaciente: str
    apellidoPaciente: str
    cedula: str
    telefono: int
    fechaNacimiento: date
    sexo: Sex

    @field_validator("sexo", mode="before")
    @classmethod
    def validate_sex(cls, value):
        normalized = normalize_sex(value)
        if normalized not in {sex.value for sex in Sex}:
            raise ValueError("Sexo inválido. Use Masculino, Femenino u Otro.")
        return normalized


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseModel):
    nombrePaciente: str | None = None
    apellidoPaciente: str | None = None
    cedula: str | None = None
    telefono: int | None = None
    fechaNacimiento: date | None = None
    sexo: Sex | None = None

    @field_validator("sexo", mode="before")
    @classmethod
    def validate_optional_sex(cls, value):
        if value is None:
            return value
        normalized = normalize_sex(value)
        if normalized not in {sex.value for sex in Sex}:
            raise ValueError("Sexo inválido. Use Masculino, Femenino u Otro.")
        return normalized


class PacienteOut(PacienteBase):
    idPaciente: int
    usuarioID: int
    model_config = ConfigDict(from_attributes=True)
