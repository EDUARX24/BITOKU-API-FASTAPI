from pydantic import BaseModel
from datetime import date
from typing import Optional

class ConsultaBase(BaseModel):
    valoracion: str
    fechaConsulta: date
    citaID: int
    doctorID: int

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaOut(ConsultaBase):
    idConsulta: int
    class Config:
        from_attributes = True
