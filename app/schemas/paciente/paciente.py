from pydantic import BaseModel
from datetime import date

class PacienteBase(BaseModel):
    nombrePaciente: str
    apellidoPaciente: str
    cedula: str
    telefono: int
    fechaNacimiento: date
    sexo: str

class PacienteCreate(PacienteBase):
    usuarioID: int

class PacienteOut(PacienteBase):
    idPaciente: int
    usuarioID: int
    class Config:
        from_attributes = True
