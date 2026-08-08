from fastapi import APIRouter, Depends, Path, Query, Security, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.ApiResponse.response import ApiResponse
from app.schemas.consulta.consulta import ConsultaCreate, ConsultaUpdate
from app.services.consulta_service import (
    create_consulta_service,
    delete_consulta_service,
    get_consulta_service,
    list_consultas_service,
    update_consulta_service,
)


router = APIRouter()


@router.post("/consulta", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["Consulta"])
def crear_consulta(
    consulta_in: ConsultaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    consulta_out = create_consulta_service(consulta_in, db, current_user)
    return ApiResponse(
        statusCode=201,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Consulta médica creada exitosamente"],
        result=consulta_out,
    )


@router.get("/consultas", response_model=ApiResponse, tags=["Consulta"])
def listar_consultas(
    pageSize: int = Query(0, ge=0),
    pageNumber: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    consultas_out = list_consultas_service(pageSize, pageNumber, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=consultas_out,
    )


@router.get("/consulta/{id_consulta}", response_model=ApiResponse, tags=["Consulta"])
def obtener_consulta(
    id_consulta: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    consulta_out = get_consulta_service(id_consulta, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=consulta_out,
    )


@router.delete("/consulta/{id_consulta}", response_model=ApiResponse, tags=["Consulta"])
def eliminar_consulta(
    id_consulta: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    consulta_out = delete_consulta_service(id_consulta, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Consulta eliminada exitosamente"],
        result=consulta_out,
    )


@router.put("/consulta/{id_consulta}", response_model=ApiResponse, tags=["Consulta"])
def actualizar_consulta(
    id_consulta: int = Path(..., gt=0),
    consulta_in: ConsultaUpdate = ...,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    consulta_out = update_consulta_service(id_consulta, consulta_in, db, current_user, partial=False)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Consulta actualizada exitosamente"],
        result=consulta_out,
    )


@router.patch("/consulta/{id_consulta}", response_model=ApiResponse, tags=["Consulta"])
def actualizar_parcial_consulta(
    id_consulta: int = Path(..., gt=0),
    consulta_in: ConsultaUpdate = ...,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    consulta_out = update_consulta_service(id_consulta, consulta_in, db, current_user, partial=True)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Consulta actualizada exitosamente"],
        result=consulta_out,
    )
