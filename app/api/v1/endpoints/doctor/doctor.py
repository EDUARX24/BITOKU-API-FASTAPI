from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from app.schemas.doctor.doctor import DoctorCreate, DoctorOut
from app.models.doctor.doctor import Doctor
from app.models.usuario.usuario import Usuario
from app.api.deps import get_current_user, get_db

router = APIRouter()

#crear endpoint crear doctor relacionado con un usuario
@router.post("/doctors", response_model=DoctorOut, status_code=status.HTTP_201_CREATED, tags=["Doctor"])
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    #buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.nombreUsuario == current_user).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    #verificar que solo los usuarios con rol doctor o usuario puedan crearlo
    if usuario.rol not in ["doc", "adm"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear un doctor")

    #verificar si ya existe un doctor relacionado con el usuario
    existing_doctor = db.query(Doctor).filter(Doctor.usuarioID == usuario.idUsuario).first()
    if existing_doctor:
        raise HTTPException(status_code=400, detail="Ya existe un doctor relacionado con este usuario")
    
    #verificar los datos para doctor
    if not doctor.nombreDoctor or not doctor.apellidoDoctor or not doctor.especialidad or not doctor.tlfDoctor or not doctor.horario or not doctor.sexo:
        raise HTTPException(status_code=400, detail="Todos los campos son obligatorios")
    #crear el nuevo doctor
    new_doctor = Doctor(usuarioID = usuario.idUsuario, nombreDoctor = doctor.nombreDoctor, apellidoDoctor = doctor.apellidoDoctor, especialidad = doctor.especialidad, tlfDoctor = doctor.tlfDoctor, horario = doctor.horario, sexo = doctor.sexo)
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

#endpoint eliminar doctor
@router.delete("/doctors/{idDoctor}", status_code=status.HTTP_200_OK, tags=["Doctor"])
def eliminar_doctor(idDoctor: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    #buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.nombreUsuario == current_user).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    #verificar que solo los usuarios con rol doctor o usuario puedan eliminarlo
    if usuario.rol not in ["doc", "adm"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar un doctor")

    #buscar el doctor a eliminar
    doctor = db.query(Doctor).filter(Doctor.idDoctor == idDoctor, Doctor.usuarioID == usuario.idUsuario).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")

    db.delete(doctor)
    db.commit()
    return {"detail": "Doctor eliminado exitosamente"}

#endpoint actualizar doctor
@router.put("/doctors/{idDoctor}", response_model=DoctorOut, status_code=status.HTTP_200_OK, tags=["Doctor"])
def actualizar_doctor(idDoctor: int, doctor: DoctorCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    #buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.nombreUsuario == current_user).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    #verificar que solo los usuarios con rol doctor o usuario puedan actualizarlo
    if usuario.rol not in ["doc", "adm"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar un doctor")

    #buscar el doctor a actualizar
    existing_doctor = db.query(Doctor).filter(Doctor.idDoctor == idDoctor, Doctor.usuarioID == usuario.idUsuario).first()
    if not existing_doctor:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")

    #actualizar los datos del doctor
    existing_doctor.nombreDoctor = doctor.nombreDoctor
    existing_doctor.apellidoDoctor = doctor.apellidoDoctor
    existing_doctor.especialidad = doctor.especialidad
    existing_doctor.tlfDoctor = doctor.tlfDoctor
    existing_doctor.horario = doctor.horario
    existing_doctor.sexo = doctor.sexo
    db.commit()
    db.refresh(existing_doctor)
    return existing_doctor

#endpoint listar doctor
@router.get("/doctors", response_model=list[DoctorOut], status_code=status.HTTP_200_OK, tags=["Doctor"])
def doctores(
    pageSize: int = 0,
    pageNumber: int = 1,
    db: Session = Depends(get_db),
    current_username: str = Security(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.nombreUsuario == current_username).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.rol != "adm":
        raise HTTPException(status_code=403, detail="No tiene permiso para listar doctores")

    query = db.query(Doctor)

    if pageSize > 0:
        query = query.offset(pageSize * (pageNumber - 1)).limit(pageSize)

    doctores = query.all()
    return doctores
