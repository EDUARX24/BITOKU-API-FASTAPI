import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import UserRole, normalize_role
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.doctor.doctor import Doctor
from app.models.paciente.paciente import Paciente
from app.models.usuario.usuario import Usuario
from app.schemas.usuario import LoginRequest, UsuarioCreate, UsuarioOut


logger = logging.getLogger(__name__)
ALLOWED_ROLES = {role.value for role in UserRole}


def _normalize_and_validate_role(role: str) -> str:
    normalized_role = normalize_role(role)
    if normalized_role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Use adm, doc o ptn.",
        )
    return normalized_role


def login_user(login_req: LoginRequest, db: Session):
    user = db.query(Usuario).filter(Usuario.nombreUsuario == login_req.username).first()
    if user is None or not verify_password(login_req.password, user.contrasenia):
        logger.warning("Intento de login fallido para usuario: %s", login_req.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    normalized_role = normalize_role(user.rol)
    user_data = {
        "idUsuario": user.idUsuario,
        "nombreUsuario": user.nombreUsuario,
        "rol": normalized_role,
    }

    if normalized_role == "doc":
        user_data["has_doctor_profile"] = (
            db.query(Doctor).filter(Doctor.usuarioID == user.idUsuario).first() is not None
        )
    elif normalized_role == "ptn":
        user_data["has_paciente_profile"] = (
            db.query(Paciente).filter(Paciente.usuarioID == user.idUsuario).first() is not None
        )

    logger.info("Login exitoso para usuario: %s", login_req.username)
    return {
        "user": user_data,
        "token": create_access_token({"sub": str(user.idUsuario)}),
    }


def register_user_service(user: UsuarioCreate, db: Session):
    username = user.nombreUsuario.strip()
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario es requerido",
        )

    db_user = db.query(Usuario).filter(Usuario.nombreUsuario == username).first()
    if db_user:
        logger.warning("Intento de registro con usuario ya existente: %s", username)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario ya existe",
        )

    new_user = Usuario(
        nombreUsuario=username,
        contrasenia=get_password_hash(user.contrasenia),
        rol=_normalize_and_validate_role(user.rol),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("Usuario registrado exitosamente: %s", username)
    return UsuarioOut.model_validate(new_user, from_attributes=True)


def list_users_service(pageSize: int, pageNumber: int, db: Session, current_user: dict):
    if current_user["rol"] != "adm":
        logger.warning("Usuario sin permisos intentó listar usuarios: %s", current_user)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a esta información",
        )

    query = db.query(Usuario)
    if pageSize > 0:
        query = query.offset(pageSize * (pageNumber - 1)).limit(pageSize)

    users = query.all()
    logger.info(
        "Usuarios listados por: %s (total: %s)",
        current_user["nombreUsuario"],
        len(users),
    )
    return [UsuarioOut.model_validate(user, from_attributes=True) for user in users]
