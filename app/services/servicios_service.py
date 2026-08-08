from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.servicios.servicios import Servicios
from app.schemas.servicios.servicios import ServiciosCreate, ServiciosOut, ServiciosUpdate


def _paginate(query, page_size: int, page_number: int):
    if page_size > 0:
        query = query.offset(page_size * (page_number - 1)).limit(page_size)
    return query


def _get_servicio_or_404(servicio_id: int, db: Session) -> Servicios:
    servicio = db.query(Servicios).filter(Servicios.idServicios == servicio_id).first()
    if servicio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    return servicio


def _require_roles(current_user: dict, allowed_roles: set[str], message: str) -> None:
    if current_user["rol"] not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def create_servicio_service(servicio_in: ServiciosCreate, db: Session, current_user: dict):
    _require_roles(current_user, {"doc", "adm"}, "No tiene permisos para crear un servicio")

    servicio_existente = (
        db.query(Servicios)
        .filter(Servicios.nombreServicio == servicio_in.nombreServicio.strip())
        .first()
    )
    if servicio_existente is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El servicio ya existe")

    servicio = Servicios(
        nombreServicio=servicio_in.nombreServicio.strip(),
        descripcion=servicio_in.descripcion.strip(),
        costo=servicio_in.costo,
    )
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return ServiciosOut.model_validate(servicio, from_attributes=True)


def list_servicios_service(page_size: int, page_number: int, db: Session, current_user: dict):
    _require_roles(current_user, {"doc", "ptn", "adm"}, "No tiene permisos para ver los servicios")
    servicios = _paginate(db.query(Servicios), page_size, page_number).all()
    return [ServiciosOut.model_validate(servicio, from_attributes=True) for servicio in servicios]


def get_servicio_service(servicio_id: int, db: Session, current_user: dict):
    _require_roles(current_user, {"doc", "adm"}, "No tiene permisos para ver el servicio")
    servicio = _get_servicio_or_404(servicio_id, db)
    return ServiciosOut.model_validate(servicio, from_attributes=True)


def update_servicio_service(
    servicio_id: int,
    servicio_in: ServiciosUpdate,
    db: Session,
    current_user: dict,
):
    _require_roles(current_user, {"doc", "adm"}, "No tiene permisos para actualizar el servicio")
    servicio = _get_servicio_or_404(servicio_id, db)

    update_data = servicio_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    if "nombreServicio" in update_data:
        new_name = update_data["nombreServicio"].strip()
        existing = (
            db.query(Servicios)
            .filter(
                Servicios.nombreServicio == new_name,
                Servicios.idServicios != servicio.idServicios,
            )
            .first()
        )
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El servicio ya existe")
        update_data["nombreServicio"] = new_name

    if "descripcion" in update_data and update_data["descripcion"] is not None:
        update_data["descripcion"] = update_data["descripcion"].strip()

    for field, value in update_data.items():
        setattr(servicio, field, value)

    db.commit()
    db.refresh(servicio)
    return ServiciosOut.model_validate(servicio, from_attributes=True)


def delete_servicio_service(servicio_id: int, db: Session, current_user: dict):
    _require_roles(current_user, {"doc", "adm"}, "No tiene permisos para eliminar el servicio")
    servicio = _get_servicio_or_404(servicio_id, db)
    db.delete(servicio)
    db.commit()
