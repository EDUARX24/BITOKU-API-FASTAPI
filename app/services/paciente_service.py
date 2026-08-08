import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.paciente.paciente import Paciente
from app.schemas.paciente.paciente import PacienteCreate, PacienteOut, PacienteUpdate


logger = logging.getLogger(__name__)


def _ensure_role(current_user: dict, allowed_roles: set[str], message: str) -> None:
    if current_user["rol"] not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def _paginate(query, page_size: int, page_number: int):
    if page_size > 0:
        query = query.offset(page_size * (page_number - 1)).limit(page_size)
    return query


def _get_paciente_or_404(
    paciente_id: int,
    db: Session,
    current_user: dict,
) -> Paciente:
    query = db.query(Paciente).filter(Paciente.idPaciente == paciente_id)
    if current_user["rol"] == "ptn":
        query = query.filter(Paciente.usuarioID == current_user["idUsuario"])

    paciente = query.first()
    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de paciente no encontrado",
        )
    return paciente


def create_paciente_service(
    paciente_in: PacienteCreate,
    db: Session,
    current_user: dict,
):
    _ensure_role(
        current_user,
        {"ptn"},
        "Solo los usuarios con rol paciente pueden completar este perfil",
    )

    existing = db.query(Paciente).filter(Paciente.usuarioID == current_user["idUsuario"]).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El perfil de paciente ya está completo",
        )

    nuevo_paciente = Paciente(
        usuarioID=current_user["idUsuario"],
        **paciente_in.model_dump(),
    )
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)

    logger.info("Perfil de paciente creado para usuario: %s", current_user["idUsuario"])
    return PacienteOut.model_validate(nuevo_paciente, from_attributes=True)


def list_pacientes_service(
    page_size: int,
    page_number: int,
    db: Session,
    current_user: dict,
):
    _ensure_role(
        current_user,
        {"adm", "doc"},
        "No tiene permiso para listar pacientes",
    )

    query = _paginate(db.query(Paciente), page_size, page_number)
    pacientes = query.all()
    logger.info("Pacientes listados por usuario: %s", current_user["idUsuario"])
    return [PacienteOut.model_validate(paciente, from_attributes=True) for paciente in pacientes]


def get_paciente_service(paciente_id: int, db: Session, current_user: dict):
    _ensure_role(
        current_user,
        {"ptn", "adm", "doc"},
        "No tiene permiso para ver el perfil de paciente",
    )
    paciente = _get_paciente_or_404(paciente_id, db, current_user)
    return PacienteOut.model_validate(paciente, from_attributes=True)


def delete_paciente_service(paciente_id: int, db: Session, current_user: dict):
    _ensure_role(
        current_user,
        {"adm", "doc"},
        "Solo los usuarios con rol doctor o admin pueden eliminar un perfil de paciente",
    )
    paciente = db.query(Paciente).filter(Paciente.idPaciente == paciente_id).first()
    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de paciente no encontrado",
        )

    paciente_out = PacienteOut.model_validate(paciente, from_attributes=True)
    db.delete(paciente)
    db.commit()
    logger.info("Perfil de paciente eliminado: %s", paciente_id)
    return paciente_out


def update_paciente_service(
    paciente_id: int,
    paciente_in: PacienteCreate | PacienteUpdate,
    db: Session,
    current_user: dict,
    *,
    partial: bool,
):
    _ensure_role(
        current_user,
        {"ptn", "adm", "doc"},
        "No tiene permiso para actualizar el perfil de paciente",
    )

    paciente = _get_paciente_or_404(paciente_id, db, current_user)
    update_data = paciente_in.model_dump(exclude_unset=partial)
    if partial and not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    for field, value in update_data.items():
        setattr(paciente, field, value)

    db.commit()
    db.refresh(paciente)
    logger.info("Perfil de paciente actualizado: %s", paciente_id)
    return PacienteOut.model_validate(paciente, from_attributes=True)


def export_pacientes_rows_service(
    page_size: int,
    page_number: int,
    db: Session,
    current_user: dict,
):
    _ensure_role(
        current_user,
        {"adm", "doc"},
        "No tiene permiso para exportar pacientes",
    )

    pacientes = _paginate(db.query(Paciente), page_size, page_number).all()
    return [
        {
            "ID": paciente.idPaciente,
            "Nombre": paciente.nombrePaciente,
            "Apellido": paciente.apellidoPaciente,
            "Fecha Nacimiento": paciente.fechaNacimiento,
            "Genero": paciente.sexo,
            "Telefono": paciente.telefono,
            "Cedula": paciente.cedula,
        }
        for paciente in pacientes
    ]
