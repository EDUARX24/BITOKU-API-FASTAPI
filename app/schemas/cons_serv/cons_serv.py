from pydantic import BaseModel

class ConsServBase(BaseModel):
    servicios: int
    consultaID: int

class ConsServCreate(ConsServBase):
    pass

class ConsServOut(ConsServBase):
    idCons_Serv: int
    class Config:
        from_attributes = True
