import os
import logging
from app.schemas.ApiResponse.response import ApiResponse

def handle_api_exception(e: Exception, status_code: int = 500, generic_message: str = "Error interno del servidor") -> ApiResponse:
    """
    Maneja excepciones para endpoints, mostrando solo mensajes genéricos en producción
    y registrando el error internamente.
    """
    # Registrar el error internamente (puedes usar logging, Sentry, etc.)
    logging.error(f"Exception: {str(e)}", exc_info=True)

    # Detectar entorno de producción
    is_prod = os.getenv("ENV", "dev") == "prod"
    if is_prod:
        # Solo mostrar mensaje genérico
        error_messages = [generic_message]
    else:
        # Mostrar detalles en desarrollo
        error_messages = [str(e), type(e).__name__]

    return ApiResponse(
        statusCode=status_code,
        isSuccess=False,
        errorMessages=error_messages,
        successMessages=[],
        result=None
    )
