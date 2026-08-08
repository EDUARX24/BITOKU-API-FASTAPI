import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import AppointmentStatus
from app.models.citamedica.citamedica import CitaMedica
from app.models.consulta.consulta import Consulta
from app.models.paciente.paciente import Paciente
from app.schemas.citamedica.citamedica import CitaMedicaCreate, CitaMedicaOut, CitaMedicaUpdate


logger = logging.getLogger(__name__)


def _paginate(query, page_size: int, page_number: int):
    if page_size > 0:
        query = query.offset(page_size * (page_number - 1)).limit(page_size)
    return query


def _get_patient_profile_for_user(db: Session, user_id: int) -> Paciente:
    paciente = db.query(Paciente).filter(Paciente.usuarioID == user_id).first()
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return paciente


def _get_cita_owned_by_patient_or_404(id_cita: int, db: Session, current_user: dict):
    cita = db.query(CitaMedica).filter(CitaMedica.idCita == id_cita).first()
    if cita is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita médica no encontrada",
        )

    paciente = db.query(Paciente).filter(Paciente.idPaciente == cita.pacienteID).first()
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    if paciente.usuarioID != current_user["idUsuario"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a esta cita médica",
        )
    return cita, paciente


def _validate_cita_state(estado, motivo: str | None) -> None:
    normalized_reason = motivo.strip() if isinstance(motivo, str) else motivo
    if estado == AppointmentStatus.CANCELED and not normalized_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe indicar motivo de cancelación cuando la cita está cancelada.",
        )
    if estado != AppointmentStatus.CANCELED and normalized_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El motivo de cancelación solo aplica para citas canceladas.",
        )


def create_cita_medica_service(cita_in: CitaMedicaCreate, db: Session, current_user: dict):
    if current_user["rol"] != "ptn":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear una cita médica",
        )

    paciente = _get_patient_profile_for_user(db, current_user["idUsuario"])
    _validate_cita_state(cita_in.estado, cita_in.motivocancalacion)
    cita_existente = db.query(CitaMedica).filter(
        CitaMedica.pacienteID == paciente.idPaciente,
        CitaMedica.fechaCita == cita_in.fechaCita,
    ).first()
    if cita_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cita médica para el paciente en esta fecha",
        )

    cita = CitaMedica(
        pacienteID=paciente.idPaciente,
        **cita_in.model_dump(),
    )
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return CitaMedicaOut.model_validate(cita, from_attributes=True)


def list_citas_service(page_size: int, page_number: int, db: Session, current_user: dict):
    if current_user["rol"] not in {"adm", "doc"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a las citas médicas",
        )

    citas = _paginate(db.query(CitaMedica), page_size, page_number).all()
    return [CitaMedicaOut.model_validate(cita, from_attributes=True) for cita in citas]


def citas_paciente_id_service(id_paciente: int, db: Session, current_user: dict):
    if current_user["rol"] not in {"ptn", "adm", "doc"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver las citas",
        )

    paciente = db.query(Paciente).filter(Paciente.idPaciente == id_paciente).first()
    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado o no existe",
        )

    if current_user["rol"] == "ptn" and paciente.usuarioID != current_user["idUsuario"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver las citas de otro paciente",
        )

    citas = db.query(CitaMedica).filter(CitaMedica.pacienteID == paciente.idPaciente).all()
    return [CitaMedicaOut.model_validate(cita, from_attributes=True) for cita in citas]


def update_cita_service(
    id_cita: int,
    cita_in: CitaMedicaCreate | CitaMedicaUpdate,
    db: Session,
    current_user: dict,
    *,
    partial: bool,
):
    if current_user["rol"] != "ptn":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar una cita médica",
        )

    cita, paciente = _get_cita_owned_by_patient_or_404(id_cita, db, current_user)
    update_data = cita_in.model_dump(exclude_unset=partial)
    if partial and not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    nueva_fecha = update_data.get("fechaCita", cita.fechaCita)
    nuevo_estado = update_data.get("estado", cita.estado)
    nuevo_motivo = update_data.get("motivocancalacion", cita.motivocancalacion)
    _validate_cita_state(nuevo_estado, nuevo_motivo)
    cita_existente = db.query(CitaMedica).filter(
        CitaMedica.pacienteID == paciente.idPaciente,
        CitaMedica.fechaCita == nueva_fecha,
        CitaMedica.idCita != cita.idCita,
    ).first()
    if cita_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una cita médica para el paciente en esta fecha",
        )

    for field, value in update_data.items():
        setattr(cita, field, value)

    db.commit()
    db.refresh(cita)
    return CitaMedicaOut.model_validate(cita, from_attributes=True)


def delete_cita_service(id_cita: int, db: Session, current_user: dict):
    if current_user["rol"] != "ptn":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar una cita médica",
        )

    cita, _ = _get_cita_owned_by_patient_or_404(id_cita, db, current_user)
    consulta = db.query(Consulta).filter(Consulta.citaID == cita.idCita).first()
    if consulta is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una cita médica con consulta asociada",
        )

    cita_out = CitaMedicaOut.model_validate(cita, from_attributes=True)
    db.delete(cita)
    db.commit()
    logger.info("Cita médica eliminada exitosamente: %s", id_cita)
    return cita_out
