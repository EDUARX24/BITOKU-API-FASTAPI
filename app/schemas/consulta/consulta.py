from datetime import date

from pydantic import BaseModel, ConfigDict


class ConsultaBase(BaseModel):
    valoracion: str
    fechaConsulta: date
    citaID: int


class ConsultaCreate(ConsultaBase):
    servicios: list[int]


class ConsultaUpdate(BaseModel):
    valoracion: str | None = None
    fechaConsulta: date | None = None


class ConsultaOut(ConsultaBase):
    idConsulta: int
    doctorID: int
    model_config = ConfigDict(from_attributes=True)
