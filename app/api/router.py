from fastapi import APIRouter

from app.api.v1.endpoints.auth import users
from app.api.v1.endpoints.citamedica import citaMedica
from app.api.v1.endpoints.consulta import consulta
from app.api.v1.endpoints.doctor import doctor
from app.api.v1.endpoints.paciente import paciente
from app.api.v1.endpoints.servicios import servicios


api_router = APIRouter()
api_router.include_router(users.router, prefix="/api/auth", tags=["User"])
api_router.include_router(paciente.router, prefix="/api/ptn", tags=["Paciente"])
api_router.include_router(doctor.router, prefix="/api/doc", tags=["Doctor"])
api_router.include_router(citaMedica.router, prefix="/api/cita", tags=["Cita Medica"])
api_router.include_router(servicios.router, prefix="/api/servicios", tags=["Servicios"])
api_router.include_router(consulta.router, prefix="/api/consulta", tags=["Consulta"])
