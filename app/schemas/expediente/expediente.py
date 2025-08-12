from pydantic import BaseModel
from datetime import date
from typing import Optional

class ExpedienteBase(BaseModel):
    pacienteID: int
    doctorid: int
    id_app: int
    id_apf: int
    alimentacion: str
    horaSueño: str
    actividadFisica: int
    descpAcFisica: str
    alcohol: int
    descpAlcohol: str
    fumar: int
    descpFumar: str
    medicamento: int
    descpMedicamento: str
    fechaExpediente: date
    motivoConsulta: str
    diagnostico: str

class ExpedienteCreate(ExpedienteBase):
    pass

class ExpedienteOut(ExpedienteBase):
    idExpediente: int
    class Config:
        from_attributes = True
