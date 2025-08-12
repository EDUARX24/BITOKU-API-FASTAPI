from pydantic import BaseModel
from datetime import date
from typing import Optional

class CitaMedicaBase(BaseModel):
    pacienteID: int
    fechaCita: date
    hora: str
    estado: int
    motivocancalacion: Optional[str] = None

class CitaMedicaCreate(CitaMedicaBase):
    pass

class CitaMedicaOut(CitaMedicaBase):
    idCita: int
    class Config:
        from_attributes = True
