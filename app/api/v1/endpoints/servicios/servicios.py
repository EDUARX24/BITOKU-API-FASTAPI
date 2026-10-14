from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.ApiResponse.response import ApiResponse
from app.schemas.servicios import ServiciosCreate, ServiciosUpdate
from app.services.servicios_service import (
    create_servicio_service,
    delete_servicio_service,
    get_servicio_service,
    list_servicios_service,
    update_servicio_service,
)


router = APIRouter()


@router.post("/servicios", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["Servicios"])
def crear_servicio(
    servicio_in: ServiciosCreate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    servicio_out = create_servicio_service(servicio_in, db, current_user)
    return ApiResponse(
        statusCode=201,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicio creado exitosamente"],
        result=servicio_out,
    )


@router.get("/servicios", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Servicios"])
def obtener_servicios(
    pageSize: int = Query(0, ge=0),
    pageNumber: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    servicios_out = list_servicios_service(pageSize, pageNumber, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicios obtenidos exitosamente"],
        result=servicios_out,
    )


@router.get("/servicios/{servicio_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Servicios"])
def obtener_servicio(servicio_id: int,db: Session = Depends(get_db),current_user: dict = Security(get_current_user),):
    servicio_out = get_servicio_service(servicio_id, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicio obtenido exitosamente"],
        result=servicio_out,
    )


@router.patch("/servicios/{servicio_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Servicios"])
def actualizar_servicio(
    servicio_id: int,
    servicio_in: ServiciosUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    servicio_out = update_servicio_service(servicio_id, servicio_in, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicio actualizado exitosamente"],
        result=servicio_out,
    )


@router.delete("/servicios/{servicio_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Servicios"])
def eliminar_servicio(
    servicio_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    delete_servicio_service(servicio_id, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicio eliminado exitosamente"],
        result=None,
    )
