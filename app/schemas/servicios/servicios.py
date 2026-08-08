from pydantic import BaseModel, ConfigDict, field_validator


class ServiciosBase(BaseModel):
    nombreServicio: str
    descripcion: str
    costo: float


class ServiciosCreate(ServiciosBase):
    pass


class ServiciosOut(ServiciosBase):
    idServicios: int
    model_config = ConfigDict(from_attributes=True)


class ServiciosUpdate(BaseModel):
    nombreServicio: str | None = None
    descripcion: str | None = None
    costo: float | None = None

    @field_validator("costo", mode="before")
    @classmethod
    def costo_must_be_numeric(cls, value):
        if value is None:
            return value
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("El costo debe ser un valor numérico") from exc
