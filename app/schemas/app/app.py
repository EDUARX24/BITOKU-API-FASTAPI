from pydantic import BaseModel
from datetime import date

class AppBase(BaseModel):
    nombreapp: str
    fechaApp: date

class AppCreate(AppBase):
    pass

class AppOut(AppBase):
    app_id: int
    class Config:
        from_attributes = True
