from pydantic import BaseModel

class DoctorBase(BaseModel):
    nombreDoctor: str
    apellidoDoctor: str
    tlfDoctor: int
    especialidad: str
    horario: str | None = None
    sexo: str

class DoctorCreate(DoctorBase):
    usuarioID: int

class DoctorOut(DoctorBase):
    idDoctor: int
    usuarioID: int
    class Config:
        from_attributes = True
