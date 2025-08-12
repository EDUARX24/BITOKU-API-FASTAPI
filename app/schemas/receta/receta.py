from pydantic import BaseModel

class RecetaBase(BaseModel):
    consultaID: int
    medicamento: str
    presentacion: str
    dosis: str
    duracion: str
    cantidad: int

class RecetaCreate(RecetaBase):
    pass

class RecetaOut(RecetaBase):
    idReceta: int
    class Config:
        from_attributes = True
