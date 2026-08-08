import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.doctor.doctor import Doctor
from app.schemas.doctor.doctor import DoctorCreate, DoctorOut, DoctorUpdate


logger = logging.getLogger(__name__)


def _paginate(query, page_size: int, page_number: int):
    if page_size > 0:
        query = query.offset(page_size * (page_number - 1)).limit(page_size)
    return query


def _require_doctor_or_admin(current_user: dict, message: str) -> None:
    if current_user["rol"] not in {"doc", "adm"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def _get_doctor_query_for_actor(doctor_id: int, db: Session, current_user: dict):
    query = db.query(Doctor).filter(Doctor.idDoctor == doctor_id)
    if current_user["rol"] == "doc":
        query = query.filter(Doctor.usuarioID == current_user["idUsuario"])
    return query


def create_doctor_service(doctor_in: DoctorCreate, db: Session, current_user: dict):
    _require_doctor_or_admin(current_user, "No tienes permiso para crear un doctor")

    existing_doctor = db.query(Doctor).filter(Doctor.usuarioID == current_user["idUsuario"]).first()
    if existing_doctor is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un doctor relacionado con este usuario",
        )

    doctor = Doctor(usuarioID=current_user["idUsuario"], **doctor_in.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    logger.info("Doctor creado exitosamente para usuario %s", current_user["idUsuario"])
    return DoctorOut.model_validate(doctor, from_attributes=True)


def get_doctor_service(doctor_id: int, db: Session, current_user: dict):
    _require_doctor_or_admin(current_user, "No tienes permiso para obtener un doctor")
    doctor = _get_doctor_query_for_actor(doctor_id, db, current_user).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor no encontrado")
    return DoctorOut.model_validate(doctor, from_attributes=True)


def delete_doctor_service(doctor_id: int, db: Session, current_user: dict):
    _require_doctor_or_admin(current_user, "No tienes permiso para eliminar un doctor")
    doctor = _get_doctor_query_for_actor(doctor_id, db, current_user).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor no encontrado")

    doctor_out = DoctorOut.model_validate(doctor, from_attributes=True)
    db.delete(doctor)
    db.commit()
    logger.info("Doctor eliminado exitosamente: %s", doctor_id)
    return doctor_out


def update_doctor_service(
    doctor_id: int,
    doctor_in: DoctorCreate | DoctorUpdate,
    db: Session,
    current_user: dict,
    *,
    partial: bool,
):
    _require_doctor_or_admin(current_user, "No tienes permiso para actualizar un doctor")
    doctor = _get_doctor_query_for_actor(doctor_id, db, current_user).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor no encontrado")

    update_data = doctor_in.model_dump(exclude_unset=partial)
    if partial and not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    for field, value in update_data.items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)
    logger.info("Doctor actualizado exitosamente: %s", doctor_id)
    return DoctorOut.model_validate(doctor, from_attributes=True)


def list_doctores_service(page_size: int, page_number: int, db: Session, current_user: dict):
    if current_user["rol"] != "adm":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para listar doctores",
        )

    doctores = _paginate(db.query(Doctor), page_size, page_number).all()
    return [DoctorOut.model_validate(doctor, from_attributes=True) for doctor in doctores]
