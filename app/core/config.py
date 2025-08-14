
# Configuración principal del proyecto usando Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Variables de configuración global para la app.
    Se cargan desde variables de entorno o el archivo .env.
    """
    PROJECT_NAME: str = "Mi API con FastAPI"
    DATABASE_URL: str

    class Config:
        env_file = ".env"  # Archivo de entorno para variables sensibles

# Instancia global de settings para importar en toda la app
settings = Settings()