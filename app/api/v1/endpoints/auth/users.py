# Endpoints relacionados con usuarios y autenticación JWT
from fastapi import APIRouter, Depends, HTTPException, status, Security
from app.utils.error_handler import handle_api_exception
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.schemas.ApiResponse.response import ApiResponse
from app.api.deps import get_current_user, get_db
from fastapi.security import OAuth2PasswordBearer
from app.services.user_service import login_user, register_user_service, list_users_service

# Esquema de autenticación OAuth2 para documentación (no usado en endpoints, pero útil para Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/Users/Login")

# Instancia del router de usuarios
router = APIRouter()

# Esquema para login JSON
class LoginRequest(BaseModel):
	"""Modelo de entrada para el login de usuario."""
	username: str
	password: str

@router.post("/Login", tags=["User"], response_model=ApiResponse)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
	try:
		result = login_user(login_req, db)
		return ApiResponse(
			statusCode=200,
			isSuccess=True,
			errorMessages=[],
			successMessages=[],
			result=result
		)
	except Exception as e:
		return handle_api_exception(e, status_code=400, generic_message="Error al iniciar sesión")
	
#endpoint para crear un usuario
@router.post("/Register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["User"])
def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):
	try:
		new_user_data = register_user_service(user, db)
		return ApiResponse(
			statusCode=201,
			isSuccess=True,
			errorMessages=[],
			successMessages=["Usuario creado exitosamente"],
			result=new_user_data
		)
	except Exception as e:
		return handle_api_exception(e, status_code=400, generic_message="Error al registrar usuario")

# Endpoint para listar todos los usuarios registrados (requiere autenticación)
@router.get("/List", response_model=ApiResponse, tags=["User"])
def list_users(pageSize: int = 0, pageNumber: int = 1,
	db: Session = Depends(get_db),
	current_user: dict = Security(get_current_user)
):
	try:
		users_out = list_users_service(pageSize, pageNumber, db, current_user)
		return ApiResponse(
			statusCode=200,
			isSuccess=True,
			errorMessages=[],
			successMessages=[],
			result=users_out
		)
	except Exception as e:
		return handle_api_exception(e, status_code=403, generic_message="Error al listar usuarios")