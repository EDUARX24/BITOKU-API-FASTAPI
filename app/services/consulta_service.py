import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.citamedica.citamedica import CitaMedica
from app.models.cons_serv.cons_serv import ConsServ
from app.models.consulta.consulta import Consulta
from app.models.doctor.doctor import Doctor
from app.models.servicios.servicios import Servicios
from app.schemas.consulta.consulta import ConsultaCreate, ConsultaOut, ConsultaUpdate


logger = logging.getLogger(__name__)


def _paginate(query, page_size: int, page_number: int):
    if page_size > 0:
        query = query.offset(page_size * (page_number - 1)).limit(page_size)
    return query


def _get_doctor_profile_for_user(db: Session, user_id: int) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.usuarioID == user_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor no encontrado")
    return doctor


def _query_consulta_for_actor(consulta_id: int, db: Session, current_user: dict):
    query = db.query(Consulta).filter(Consulta.idConsulta == consulta_id)
    if current_user["rol"] == "doc":
        doctor = _get_doctor_profile_for_user(db, current_user["idUsuario"])
        query = query.filter(Consulta.doctorID == doctor.idDoctor)
    return query


def _validate_servicio_ids(db: Session, servicio_ids: list[int]) -> None:
    seen: set[int] = set()
    duplicates: list[int] = []
    for servicio_id in servicio_ids:
        if servicio_id in seen:
            duplicates.append(servicio_id)
        else:
            seen.add(servicio_id)

    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[f"Servicio duplicado: {servicio_id}" for servicio_id in duplicates],
        )

    existing_ids = {
        row[0]
        for row in db.query(Servicios.idServicios)
        .filter(Servicios.idServicios.in_(servicio_ids))
        .all()
    }
    missing = [servicio_id for servicio_id in servicio_ids if servicio_id not in existing_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[f"Servicio no encontrado: {servicio_id}" for servicio_id in missing],
        )


def create_consulta_service(consulta_in: ConsultaCreate, db: Session, current_user: dict):
    if current_user["rol"] != "doc":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear una consulta médica",
        )

    doctor = _get_doctor_profile_for_user(db, current_user["idUsuario"])
    consulta_existente = db.query(Consulta).filter(Consulta.citaID == consulta_in.citaID).first()
    if consulta_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una consulta para esta cita",
        )

    cita = db.query(CitaMedica).filter(CitaMedica.idCita == consulta_in.citaID).first()
    if cita is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada")
    if consulta_in.fechaConsulta < cita.fechaCita:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de la consulta no puede ser anterior a la fecha de la cita",
        )

    _validate_servicio_ids(db, consulta_in.servicios)

    consulta = Consulta(
        doctorID=doctor.idDoctor,
        citaID=consulta_in.citaID,
        valoracion=consulta_in.valoracion,
        fechaConsulta=consulta_in.fechaConsulta,
    )
    db.add(consulta)
    db.flush()

    for servicio_id in consulta_in.servicios:
        db.add(ConsServ(consultaID=consulta.idConsulta, servicios=servicio_id))

    db.commit()
    db.refresh(consulta)
    logger.info("Consulta creada exitosamente: %s", consulta.idConsulta)
    return ConsultaOut.model_validate(consulta, from_attributes=True)


def list_consultas_service(page_size: int, page_number: int, db: Session, current_user: dict):
    if current_user["rol"] not in {"doc", "adm"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para listar consultas médicas",
        )

    query = db.query(Consulta)
    if current_user["rol"] == "doc":
        doctor = _get_doctor_profile_for_user(db, current_user["idUsuario"])
        query = query.filter(Consulta.doctorID == doctor.idDoctor)

    consultas = _paginate(query, page_size, page_number).all()
    return [ConsultaOut.model_validate(consulta, from_attributes=True) for consulta in consultas]


def get_consulta_service(consulta_id: int, db: Session, current_user: dict):
    if current_user["rol"] not in {"doc", "adm"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver esta consulta médica",
        )

    consulta = _query_consulta_for_actor(consulta_id, db, current_user).first()
    if consulta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consulta no encontrada")
    return ConsultaOut.model_validate(consulta, from_attributes=True)


def delete_consulta_service(consulta_id: int, db: Session, current_user: dict):
    if current_user["rol"] not in {"doc", "adm"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar esta consulta médica",
        )

    consulta = _query_consulta_for_actor(consulta_id, db, current_user).first()
    if consulta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consulta no encontrada")

    db.query(ConsServ).filter(ConsServ.consultaID == consulta.idConsulta).delete()
    consulta_out = ConsultaOut.model_validate(consulta, from_attributes=True)
    db.delete(consulta)
    db.commit()
    return consulta_out


def update_consulta_service(
    consulta_id: int,
    consulta_in: ConsultaUpdate,
    db: Session,
    current_user: dict,
    *,
    partial: bool,
):
    if current_user["rol"] != "doc":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar esta consulta médica",
        )

    consulta = _query_consulta_for_actor(consulta_id, db, current_user).first()
    if consulta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consulta no encontrada")

    if consulta_in is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar",
        )

    update_data = consulta_in.model_dump(exclude_unset=partial)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    nueva_fecha = update_data.get("fechaConsulta", consulta.fechaConsulta)
    cita = db.query(CitaMedica).filter(CitaMedica.idCita == consulta.citaID).first()
    if cita is not None and nueva_fecha < cita.fechaCita:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de la consulta no puede ser anterior a la fecha de la cita",
        )

    for field, value in update_data.items():
        setattr(consulta, field, value)

    db.commit()
    db.refresh(consulta)
    return ConsultaOut.model_validate(consulta, from_attributes=True)
