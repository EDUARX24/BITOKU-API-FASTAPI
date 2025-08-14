from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from app.schemas.paciente.paciente import PacienteCreate, PacienteOut
from app.models.paciente.paciente import Paciente
from app.models.usuario.usuario import Usuario
from app.api.deps import get_current_user, get_db

router = APIRouter()

@router.post("/paciente",response_model=PacienteOut,status_code=status.HTTP_201_CREATED,tags=["Paciente"])
def paciente(paciente_in: PacienteCreate,db: Session = Depends(get_db),current_username: str = Security(get_current_user)):
    # Buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.nombreUsuario == current_username).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que el usuario tenga rol paciente
    if usuario.rol != "ptn":
        raise HTTPException(status_code=403, detail="Solo los usuarios con rol 'paciente' pueden completar este perfil")
    
    # Verificar si ya existe un perfil de paciente para este usuario
    paciente_existente = db.query(Paciente).filter(Paciente.usuarioID == usuario.idUsuario).first()
    if paciente_existente:
        raise HTTPException(status_code=400, detail="El perfil de paciente ya está completo")
    # verificar los datos para paciente
    if not paciente_in.nombrePaciente or not paciente_in.apellidoPaciente:
        raise HTTPException(status_code=400, detail="Nombre y apellido son obligatorios")
    
    # Crear el perfil de paciente
    nuevo_paciente = Paciente(usuarioID=usuario.idUsuario,nombrePaciente=paciente_in.nombrePaciente,apellidoPaciente=paciente_in.apellidoPaciente,cedula=paciente_in.cedula,telefono=paciente_in.telefono,fechaNacimiento=paciente_in.fechaNacimiento,sexo=paciente_in.sexo)
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)
    return nuevo_paciente


@router.delete("/paciente",status_code=status.HTTP_200_OK,tags=["Paciente"])
def eliminar_paciente(db: Session = Depends(get_db), current_username: str = Security(get_current_user)):
    """
    Elimina el perfil de paciente asociado al usuario autenticado.
    Solo puede ser ejecutado por usuarios con rol 'ptn'.
    """
    # Buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.nombreUsuario == current_username).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Verificar que el usuario tenga rol paciente
    if usuario.rol != "ptn":
        raise HTTPException(status_code=403, detail="Solo los usuarios con rol 'paciente' pueden eliminar su perfil de paciente")
    # Buscar el perfil de paciente
    paciente = db.query(Paciente).filter(Paciente.usuarioID == usuario.idUsuario).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Perfil de paciente no encontrado")
    db.delete(paciente)
    db.commit()
    return {"detail": "Perfil de paciente eliminado correctamente"}

