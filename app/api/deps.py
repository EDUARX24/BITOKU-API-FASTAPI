
# Dependencias y utilidades para autenticación JWT y acceso a base de datos
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError

# Clave secreta y algoritmo para firmar y verificar JWT
SECRET_KEY = "supersecretkey"  # Usa el mismo que en auth.py
ALGORITHM = "HS256"

# Esquema de autenticación tipo APIKey para usar JWT en el header Authorization
api_key_scheme = APIKeyHeader(
    name="Authorization",
    description="JWT Authorization header using the Bearer scheme.\n\nEnter 'Bearer' [space] and then your token in the text input below.\n\nExample: 'Bearer 12345abcdef'\n\nName: Authorization\nIn: header"
)


from app.models.usuario.usuario import Usuario
from app.db.session import SessionLocal

def get_current_user(token: str = Security(api_key_scheme)):
    """
    Extrae y valida el usuario autenticado a partir del token JWT enviado en el header Authorization.
    Retorna un dict con idUsuario, nombreUsuario y rol.
    """
    if token is None:
        raise HTTPException(status_code=401, detail="Token de autenticación requerido")
    if token.lower().startswith("bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        # Buscar usuario en la base de datos
        db = SessionLocal()
        user = db.query(Usuario).filter(Usuario.nombreUsuario == username).first()
        db.close()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return {
            "idUsuario": user.idUsuario,
            "nombreUsuario": user.nombreUsuario,
            "rol": user.rol
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Helpers para obtener la sesión de base de datos
from app.db.session import SessionLocal
from sqlalchemy.orm import Session

def get_db():
    """
    Provee una sesión de base de datos para cada request.
    Cierra la sesión automáticamente al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()