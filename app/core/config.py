# Configuración principal del proyecto

#version deprecada
# from pydantic import BaseSettings

#nueva forma actual
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mi API con FastAPI"
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()