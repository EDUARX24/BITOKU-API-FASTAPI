# Endpoints relacionados con usuarios y autenticación JWT
from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.models.usuario.usuario import Usuario
from app.models.doctor.doctor import Doctor
from app.models.paciente.paciente import Paciente
from app.db.session import SessionLocal
from app.api.deps import get_current_user
from fastapi.security import OAuth2PasswordBearer

# Esquema de autenticación OAuth2 para documentación (no usado en endpoints, pero útil para Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/Users/Login")

# Instancia del router de usuarios
router = APIRouter()

# Contexto de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Claves y parámetros para JWT
SECRET_KEY = "supersecretkey"  # Cambia esto en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_db():
	"""
	Provee una sesión de base de datos para cada request.
	Cierra la sesión automáticamente al finalizar.
	"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

def get_password_hash(password: str) -> str:
	"""Genera el hash seguro de una contraseña usando bcrypt."""
	return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
	"""Verifica si la contraseña en texto plano coincide con el hash almacenado."""
	return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
	"""
	Crea un token JWT firmado con los datos y expiración indicada.
	"""
	to_encode = data.copy()
	expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt

# Esquema para login JSON
class LoginRequest(BaseModel):
	"""Modelo de entrada para el login de usuario."""
	username: str
	password: str


@router.post("/Login", tags=["User"])
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
	user = db.query(Usuario).filter(Usuario.nombreUsuario == login_req.username).first()
	if not user or not verify_password(login_req.password, user.contrasenia):
		raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
	access_token = create_access_token(data={"sub": user.nombreUsuario})

	# Verificar si el usuario tiene perfil de doctor o paciente usando la ORM
	has_doctor_profile = False
	has_paciente_profile = False
	if user.rol == "doctor":
		doctor = db.query(Doctor).filter(Doctor.usuarioID == user.idUsuario).first()
		has_doctor_profile = doctor is not None
	elif user.rol == "paciente":
		paciente = db.query(Paciente).filter(Paciente.usuarioID == user.idUsuario).first()
		has_paciente_profile = paciente is not None

	user_data = {
		"idUsuario": user.idUsuario,
		"nombreUsuario": user.nombreUsuario,
		"rol": user.rol
	}
	# Solo incluir la información adicional si el rol es doctor o paciente
	if user.rol == "doc":
		user_data["has_doctor_profile"] = has_doctor_profile
	elif user.rol == "ptn":
		user_data["has_paciente_profile"] = has_paciente_profile
	return {
		"statusCode": 200,
		"isSuccess": True,
		"errorMessages": [],
		"successMessages": [],
		"result": {
			"user": user_data,
			"token": access_token
		}
	}

@router.post("/Register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED, tags=["User"])
def register_user(user: UsuarioCreate, db: Session = Depends(get_db)):
	db_user = db.query(Usuario).filter(Usuario.nombreUsuario == user.nombreUsuario).first()
	if db_user:
		raise HTTPException(status_code=400, detail="El usuario ya existe")
	hashed_password = get_password_hash(user.contrasenia)
	
    #crear nuevo usurio
	new_user = Usuario(nombreUsuario=user.nombreUsuario,contrasenia=hashed_password,
		rol=user.rol
	)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	return new_user

# Endpoint para listar todos los usuarios registrados (requiere autenticación)
@router.get("/List", response_model=list[UsuarioOut], tags=["User"])
def list_users(
	db: Session = Depends(get_db),
	current_user: str = Security(get_current_user)
):
	"""
	Devuelve una lista de todos los usuarios registrados en la base de datos.
	Requiere autenticación mediante token Bearer.
	"""
	users = db.query(Usuario).all()
	return users
