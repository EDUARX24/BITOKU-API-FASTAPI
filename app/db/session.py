
from urllib.parse import parse_qs, urlsplit

import libsql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

class LibsqlConnectionProxy:
    def __init__(self, connection):
        self._connection = connection

    def create_function(self, *args, **kwargs):
        return None

    def __getattr__(self, name):
        return getattr(self._connection, name)


def create_libsql_connection():
    parsed_url = urlsplit(settings.DATABASE_URL)
    query = parse_qs(parsed_url.query)
    token = query.get("authToken", [None])[0]

    if not parsed_url.hostname or not token:
        raise ValueError("DATABASE_URL de Turso debe incluir host y authToken")

    connection = libsql.connect(
        f"https://{parsed_url.hostname}",
        auth_token=token,
    )
    return LibsqlConnectionProxy(connection)


if settings.DATABASE_URL.startswith("sqlite+libsql://"):
    engine = create_engine(
        "sqlite://",
        creator=create_libsql_connection,
        pool_pre_ping=True,
    )
elif settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
else:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionLocal: fábrica de sesiones para usar en dependencias FastAPI
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)
