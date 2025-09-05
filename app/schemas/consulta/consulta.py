from pydantic import BaseModel
from datetime import date
from typing import Optional
from typing import List

class ConsultaBase(BaseModel):
    valoracion: str
    fechaConsulta: date
    citaID: int
    # doctorID: int

class ConsultaCreate(ConsultaBase):
    servicios: List[int]


class ConsultaOut(ConsultaBase):
    idConsulta: int
    class Config:
        from_attributes = True
