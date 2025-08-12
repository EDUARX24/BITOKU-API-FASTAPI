from pydantic import BaseModel
from datetime import date

class ApfBase(BaseModel):
    nombreapf: str
    fechaApf: date

class ApfCreate(ApfBase):
    pass

class ApfOut(ApfBase):
    apf_id: int
    class Config:
        from_attributes = True
