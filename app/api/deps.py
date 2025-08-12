# Dependencias para autenticación JWT
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError

SECRET_KEY = "supersecretkey"  # Usa el mismo que en auth.py
ALGORITHM = "HS256"

api_key_scheme = APIKeyHeader(name="Authorization", description="JWT Authorization header using the Bearer scheme.\n\nEnter 'Bearer' [space] and then your token in the text input below.\n\nExample: 'Bearer 12345abcdef'\n\nName: Authorization\nIn: header")

from fastapi import Security
def get_current_user(token: str = Security(api_key_scheme)):
    if token is None:
        raise HTTPException(status_code=401, detail="Token de autenticación requerido")
    if token.lower().startswith("bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
from app.db.session import SessionLocal
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()