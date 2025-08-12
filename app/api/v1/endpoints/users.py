from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.models.usuario.usuario import Usuario
from app.db.session import SessionLocal
from app.api.deps import get_current_user
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/Users/Login")
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "supersecretkey"  # Cambia esto en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

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


# Esquema para login JSON
class LoginRequest(BaseModel):
	username: str
	password: str



@router.post("/Login", tags=["User"])
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
	user = db.query(Usuario).filter(Usuario.nombreUsuario == login_req.username).first()
	if not user or not verify_password(login_req.password, user.contrasenia):
		raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
	access_token = create_access_token(data={"sub": user.nombreUsuario})
	user_data = {
		"idUsuario": user.idUsuario,
		"nombreUsuario": user.nombreUsuario,
		"rol": user.rol
	}
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
def register_user(
	user: UsuarioCreate,
	db: Session = Depends(get_db),
	current_user: str = Security(get_current_user)
):
	db_user = db.query(Usuario).filter(Usuario.nombreUsuario == user.nombreUsuario).first()
	if db_user:
		raise HTTPException(status_code=400, detail="El usuario ya existe")
	hashed_password = get_password_hash(user.contrasenia)
	new_user = Usuario(
		nombreUsuario=user.nombreUsuario,
		contrasenia=hashed_password,
		rol=user.rol
	)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	return new_user

# Endpoint para listar todos los usuarios
@router.get("/List", response_model=list[UsuarioOut], tags=["User"])
def list_users(
	db: Session = Depends(get_db),
	current_user: str = Security(get_current_user)
):
	users = db.query(Usuario).all()
	return users

