# Importa todos los modelos para que SQLAlchemy registre las relaciones correctamente
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.models.doctor import Doctor
from app.models.citamedica import CitaMedica
from app.models.servicios import Servicios
from app.models.consulta import Consulta
from app.models.cons_serv import ConsServ
from app.models.receta import Receta
from app.models.app import App
from app.models.apf import Apf
from app.models.expediente import Expediente

from fastapi import FastAPI
from app.api.v1.endpoints import users, auth

app = FastAPI()

app.include_router(users.router, prefix="/api/auth", tags=["User"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
