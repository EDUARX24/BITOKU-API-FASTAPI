
# Configuración de la sesión de base de datos para SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crea el engine de SQLAlchemy según el tipo de base de datos
# Para SQLite se requiere 'check_same_thread=False' para evitar errores en entornos multihilo
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.DATABASE_URL)

# SessionLocal: fábrica de sesiones para usar en dependencias FastAPI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)