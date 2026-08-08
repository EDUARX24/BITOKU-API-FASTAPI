from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.enums import normalize_role
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.usuario.usuario import Usuario

bearer_scheme = HTTPBearer(auto_error=False)


def get_db():
    """Provee una sesión DB por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Extrae y valida el usuario autenticado a partir del bearer token."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if isinstance(subject, str) and subject.isdigit():
        user = db.query(Usuario).filter(Usuario.idUsuario == int(subject)).first()
    else:
        user = db.query(Usuario).filter(Usuario.nombreUsuario == str(subject)).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "idUsuario": user.idUsuario,
        "nombreUsuario": user.nombreUsuario,
        "rol": normalize_role(user.rol),
    }
