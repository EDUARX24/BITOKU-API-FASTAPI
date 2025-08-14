
# main.py: Punto de entrada de la aplicación FastAPI

# Importa todos los modelos para que SQLAlchemy registre las relaciones y cree las tablas correctamente
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
from app.api.v1.endpoints.auth import users

# Instancia principal de la aplicación
app = FastAPI()

# Registro de routers para endpoints de usuarios y autenticación
app.include_router(users.router, prefix="/api/auth", tags=["User"])
# app.include_router(users.router, prefix="/api/auth", tags=["Auth"])

# Permite ejecutar con 'python app/main.py' directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
