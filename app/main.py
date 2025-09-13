import logging
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

from fastapi import FastAPI, Request, status
from app.schemas.ApiResponse.response import ApiResponse
from app.api.v1.endpoints.auth import users
from app.api.v1.endpoints.paciente import paciente
from app.api.v1.endpoints.doctor import doctor
from app.api.v1.endpoints.citamedica import citaMedica
from app.api.v1.endpoints.servicios import servicios
from app.api.v1.endpoints.consulta import consulta

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Configuración profesional de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("bitoku_api.log"),
        logging.StreamHandler()
    ]
)

# Instancia principal de la aplicación
app = FastAPI(
    title="Bitoku API",
    description="API para la gestión de Bitoku.",
    version="1.0.0",
    contact={
        "name": "Soporte de Bitoku",
        "email": "eduarfrancis11@gmail.com"
    }
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Mapear errores de Pydantic a mensajes legibles
    error_messages = [f"{'.'.join(str(i) for i in err['loc'])}: {err['msg']}" for err in exc.errors()]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse(
            statusCode=422,
            isSuccess=False,
            errorMessages=error_messages,
            successMessages=[],
            result=None
        ).dict()
    )


# Registro de routers de los endpoints
app.include_router(users.router, prefix="/api/auth", tags=["User"])
app.include_router(paciente.router, prefix="/api/ptn", tags=["Paciente"])
app.include_router(doctor.router, prefix="/api/doc", tags=["Doctor"])
app.include_router(citaMedica.router, prefix="/api/cita", tags=["Cita Medica"])
app.include_router(servicios.router, prefix="/api/servicios", tags=["Servicios"])
app.include_router(consulta.router, prefix="/api/consulta", tags=["Consulta"])

# Permite ejecutar con 'python app/main.py' directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
