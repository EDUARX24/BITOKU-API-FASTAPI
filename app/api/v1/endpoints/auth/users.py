# Endpoints relacionados con usuarios y autenticación JWT
from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.ApiResponse.response import ApiResponse
from app.schemas.usuario import LoginRequest, UsuarioCreate
from app.services.user_service import (
    list_users_service,
    login_user,
    register_user_service,
)


router = APIRouter()


@router.post("/Login", tags=["User"], response_model=ApiResponse)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(login_req, db)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=result,
    )


@router.post("/Register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["User"])
def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    new_user_data = register_user_service(user, db)
    return ApiResponse(
        statusCode=201,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Usuario creado exitosamente"],
        result=new_user_data,
    )


@router.get("/List", response_model=ApiResponse, tags=["User"])
def list_users(
    pageSize: int = Query(0, ge=0),
    pageNumber: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user),
):
    users_out = list_users_service(pageSize, pageNumber, db, current_user)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=users_out,
    )
