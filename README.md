# Bitoku API

API FastAPI para gestión clínica.

## Requisitos

- Python 3.12
- Virtualenv en `env`

## Variables de entorno

- `DATABASE_URL`
- `SECRET_KEY`
- `ENV`
- `APP_VERSION`
- `BACKEND_CORS_ORIGINS`
- `ENABLE_DOCS`

Ejemplo:

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=change-me
ENV=dev
APP_VERSION=1.0.0
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
ENABLE_DOCS=true
```

## Ejecutar

```powershell
env\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Healthcheck

- `GET /health`

## Migraciones

```powershell
$env:DATABASE_URL="sqlite:///./app.db"
env\Scripts\python.exe -m alembic upgrade head
```

## Tests

```powershell
env\Scripts\python.exe -m pytest -q
```
