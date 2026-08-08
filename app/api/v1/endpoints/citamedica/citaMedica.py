from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.ApiResponse.response import ApiResponse
from app.schemas.citamedica.citamedica import CitaMedicaCreate, CitaMedicaUpdate
from app.services.citamedica_service import (
    citas_paciente_id_service,
    create_cita_medica_service,
    delete_cita_service,
    list_citas_service,
    update_cita_service,
)


router = APIRouter()


@router.post("/cita-medica", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["Cita Medica"])
def crear_cita_medica(
    cita_in: CitaMedicaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    cita_out = create_cita_medica_service(cita_in, db, current_user)
    return ApiResponse(
        statusCode=201,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Cita médica creada exitosamente"],
        result=cita_out,
    )


@router.get("/citas-paciente", response_model=ApiResponse, tags=["Cita Medica"])
def listar_citas(
    pageSize: int = Query(0, ge=0),
    pageNumber: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    citas_out = list_citas_service(pageSize, pageNumber, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Citas médicas obtenidas exitosamente"],
        result=citas_out,
    )


@router.get("/citas-paciente/{id_paciente}", response_model=ApiResponse, tags=["Cita Medica"])
def citas_paciente_id(
    id_paciente: int,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    citas_out = citas_paciente_id_service(id_paciente, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Citas médicas obtenidas exitosamente"],
        result=citas_out,
    )


@router.put("/cita-medica/{id_cita}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Cita Medica"])
def actualizar_cita(
    id_cita: int,
    cita_in: CitaMedicaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    cita_out = update_cita_service(id_cita, cita_in, db, current_user, partial=False)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Cita médica actualizada exitosamente"],
        result=cita_out,
    )


@router.patch("/cita-medica/{id_cita}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Cita Medica"])
def actualizar_cita_parcial(
    id_cita: int,
    cita_in: CitaMedicaUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    cita_out = update_cita_service(id_cita, cita_in, db, current_user, partial=True)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Cita médica actualizada exitosamente"],
        result=cita_out,
    )


@router.delete("/cita-medica/{id_cita}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Cita Medica"])
def eliminar_cita(
    id_cita: int,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    cita_out = delete_cita_service(id_cita, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Cita médica eliminada exitosamente"],
        result=cita_out,
    )
