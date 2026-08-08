import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.db.models  # noqa: F401
from app.api.router import api_router
from app.core.config import settings
from app.schemas.ApiResponse.response import ApiResponse


def configure_logging() -> None:
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("bitoku_api.log"),
            logging.StreamHandler(),
        ],
    )


def build_api_response(status_code: int, errors: list[str]) -> JSONResponse:
    payload = ApiResponse(
        statusCode=status_code,
        isSuccess=False,
        errorMessages=errors,
        successMessages=[],
        result=None,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


configure_logging()
logger = logging.getLogger(__name__)

# Instancia principal de la aplicación
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para la gestión de Bitoku.",
    version=settings.APP_VERSION,
    contact={
        "name": "Soporte de Bitoku",
        "email": "eduarfrancis11@gmail.com"
    },
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)

cors_origin_regex = settings.local_dev_cors_regex

if settings.BACKEND_CORS_ORIGINS or cors_origin_regex:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_origin_regex=cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, list):
        errors = [str(item) for item in detail]
    else:
        errors = [str(detail)]
    return build_api_response(exc.status_code, errors)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = [f"{'.'.join(str(i) for i in err['loc'])}: {err['msg']}" for err in exc.errors()]
    return build_api_response(status.HTTP_422_UNPROCESSABLE_ENTITY, error_messages)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while processing %s", request.url.path)
    if settings.ENV == "prod":
        errors = ["Error interno del servidor"]
    else:
        errors = [str(exc), type(exc).__name__]
    return build_api_response(status.HTTP_500_INTERNAL_SERVER_ERROR, errors)


app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def healthcheck():
    return {
        "status": "ok",
        "environment": settings.ENV,
        "version": settings.APP_VERSION,
    }

# Permite ejecutar con 'python app/main.py' directamente
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
