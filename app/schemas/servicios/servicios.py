from pydantic import BaseModel,validator
from typing import Optional, Any

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

class ServiciosUpdate(BaseModel):
    nombreServicio: Optional[str] = None
    descripcion: Optional[str] = None
    costo: Optional[Any] = None  # <-- aceptar cualquier cosa primero

    @validator("costo")
    def costo_must_be_numeric(cls, v):
        if v is None:
            return v
        try:
            return float(v)  # intenta convertir a float
        except (ValueError, TypeError):
            raise ValueError("El costo debe ser un valor numérico")