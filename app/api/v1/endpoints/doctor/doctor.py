from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.ApiResponse.response import ApiResponse
from app.schemas.doctor.doctor import DoctorCreate, DoctorUpdate
from app.services.doctor_service import (
    create_doctor_service,
    delete_doctor_service,
    get_doctor_service,
    list_doctores_service,
    update_doctor_service,
)


router = APIRouter()


@router.post("/doctors", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["Doctor"])
def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    doctor_out = create_doctor_service(doctor, db, current_user)
    return ApiResponse(
        statusCode=201,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Doctor creado exitosamente"],
        result=doctor_out,
    )


@router.get("/doctors/{idDoctor}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def get_doctor(
    idDoctor: int,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    doctor_out = get_doctor_service(idDoctor, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=doctor_out,
    )


@router.delete("/doctors/{idDoctor}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def eliminar_doctor(
    idDoctor: int,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    doctor_out = delete_doctor_service(idDoctor, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Doctor eliminado exitosamente"],
        result=doctor_out,
    )


@router.put("/doctors/{idDoctor}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def actualizar_doctor(
    idDoctor: int,
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    doctor_out = update_doctor_service(idDoctor, doctor, db, current_user, partial=False)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Doctor actualizado exitosamente"],
        result=doctor_out,
    )


@router.patch("/doctors/{idDoctor}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def actualizar_doctor_parcial(
    idDoctor: int,
    doctor: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    doctor_out = update_doctor_service(idDoctor, doctor, db, current_user, partial=True)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Doctor actualizado exitosamente"],
        result=doctor_out,
    )


@router.get("/doctors", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def doctores(
    pageSize: int = Query(0, ge=0),
    pageNumber: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    doctores_out = list_doctores_service(pageSize, pageNumber, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=doctores_out,
    )
