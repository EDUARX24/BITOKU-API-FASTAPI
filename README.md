# Bitoku API

API FastAPI para gestión clínica.

## Requisitos

- Python 3.12+
- Virtualenv en `env`

## Variables de entorno

- `DATABASE_URL`
- `SECRET_KEY`
- `ENV`
- `APP_VERSION`
- `BACKEND_CORS_ORIGINS`
- `ENABLE_DOCS`

Ejemplo para Turso:

```env
DATABASE_URL="sqlite+libsql://development-bd-bitoku-eduarx24.aws-us-west-2.turso.io/?authToken=TU_TOKEN_DE_TURSO&secure=true"
SECRET_KEY=change-me
ENV=dev
APP_VERSION=1.0.0
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
ENABLE_DOCS=true
```

Si vas a usar SQLite local:

```env
DATABASE_URL=sqlite:///./app.db
```

## Ejecutar

```powershell
env\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Healthcheck

- `GET /health`

## Inicializar Turso

```powershell
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
env\Scripts\python.exe -c "from app.db.init_db import init_db; init_db()"
```

## Tests

```powershell
env\Scripts\python.exe -m pytest -q
```
