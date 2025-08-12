from pydantic import BaseModel
from typing import Optional

class ServiciosBase(BaseModel):
    nombreServicio: str
    descripcion: str
    costo: float

class ServiciosCreate(ServiciosBase):
    pass

class ServiciosOut(ServiciosBase):
    idServicios: int
    class Config:
        from_attributes = True
