import os
import sys
import urllib.parse
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.base import Base
from app.db.models import *  # carga todos los modelos

target_metadata = Base.metadata


def get_engine_args():
    """Extrae la URL base y construye los connect_args necesarios para Turso/libsql."""
    raw_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")
    connect_args = {}
    clean_url = raw_url

    # Soporte por si el token todavía viene en query params dentro de DATABASE_URL
    if raw_url and "?" in raw_url:
        clean_url, query_str = raw_url.split("?", 1)
        params = urllib.parse.parse_qs(query_str)
        if not auth_token:
            auth_token = params.get("authToken", params.get("auth_token", [None]))[0]

    # Inyectar credenciales si se detecta un token
    if auth_token:
        connect_args["auth_token"] = auth_token
        connect_args["secure"] = True

    return clean_url, connect_args


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url, _ = get_engine_args()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url, connect_args = get_engine_args()

    # Se usa create_engine en lugar de engine_from_config para inyectar connect_args
    connectable = create_engine(
        url,
        connect_args=connect_args,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()