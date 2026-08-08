from pydantic import BaseModel, ConfigDict, field_validator

from app.core.enums import Sex, normalize_sex


class DoctorBase(BaseModel):
    nombreDoctor: str
    apellidoDoctor: str
    tlfDoctor: int
    especialidad: str
    horario: str | None = None
    sexo: Sex

    @field_validator("sexo", mode="before")
    @classmethod
    def validate_sex(cls, value):
        normalized = normalize_sex(value)
        if normalized not in {sex.value for sex in Sex}:
            raise ValueError("Sexo inválido. Use Masculino, Femenino u Otro.")
        return normalized


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    nombreDoctor: str | None = None
    apellidoDoctor: str | None = None
    tlfDoctor: int | None = None
    especialidad: str | None = None
    horario: str | None = None
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


class DoctorOut(DoctorBase):
    idDoctor: int
    usuarioID: int
    model_config = ConfigDict(from_attributes=True)
