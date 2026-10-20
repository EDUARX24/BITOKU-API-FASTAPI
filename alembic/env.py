import os
import sys
import urllib.parse
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.base import Base
from app.db.models import *

target_metadata = Base.metadata


def get_engine_args():
    raw_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")
    connect_args = {}

    # Asegurar que conserve siempre el dialecto válido sqlite+libsql://
    if raw_url.startswith("sqlite+https://"):
        raw_url = raw_url.replace("sqlite+https://", "sqlite+libsql://", 1)

    # Extraer el token si viniera en la query string
    if "?" in raw_url:
        base_url, query_str = raw_url.split("?", 1)
        params = urllib.parse.parse_qs(query_str)
        if not auth_token:
            auth_token = params.get("authToken", params.get("auth_token", [None]))[0]

        # Garantizar que secure=true permanezca en la URL para evitar el 308 redirect
        final_url = f"{base_url}?secure=true"
    else:
        final_url = f"{raw_url}?secure=true"

    if auth_token:
        # Solo auth_token se pasa al conector DBAPI
        connect_args["auth_token"] = auth_token

    return final_url, connect_args


def run_migrations_offline() -> None:
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
    url, connect_args = get_engine_args()

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