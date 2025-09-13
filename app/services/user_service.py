
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.models.usuario.usuario import Usuario
from app.models.doctor.doctor import Doctor
from app.models.paciente.paciente import Paciente
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.schemas.ApiResponse.response import ApiResponse
from jose import jwt

SECRET_KEY = "supersecretkey"  # Cambia esto en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()
	expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt

def login_user(login_req, db: Session):
	user = db.query(Usuario).filter(Usuario.nombreUsuario == login_req.username).first()
	if not user or not verify_password(login_req.password, user.contrasenia):
		raise Exception("Usuario o contraseña incorrectos")
	access_token = create_access_token(data={"sub": user.nombreUsuario})

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
	if user.rol == "doc":
		user_data["has_doctor_profile"] = has_doctor_profile
	elif user.rol == "ptn":
		user_data["has_paciente_profile"] = has_paciente_profile
	return {
		"user": user_data,
		"token": access_token
	}

def register_user_service(user: UsuarioCreate, db: Session):
	db_user = db.query(Usuario).filter(Usuario.nombreUsuario == user.nombreUsuario).first()
	if db_user:
		raise Exception("El usuario ya existe")
	hashed_password = get_password_hash(user.contrasenia)
	new_user = Usuario(nombreUsuario=user.nombreUsuario, contrasenia=hashed_password, rol=user.rol)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	new_user_data = UsuarioOut.model_validate(new_user, from_attributes=True)
	return new_user_data

def list_users_service(pageSize: int, pageNumber: int, db: Session, current_user: dict):
	if current_user["rol"] != "adm":
		raise Exception("No tiene permisos para acceder a esta información")
	query = db.query(Usuario)
	if pageSize > 0:
		query = query.offset(pageSize * (pageNumber - 1)).limit(pageSize)
	users = query.all()
	users_out = [UsuarioOut.model_validate(user, from_attributes=True) for user in users]
	return users_out
