from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from app.schemas.doctor.doctor import DoctorCreate, DoctorOut
from app.models.doctor.doctor import Doctor
from app.models.usuario.usuario import Usuario
from app.schemas.ApiResponse.response import ApiResponse
from app.api.deps import get_current_user, get_db
import logging

router = APIRouter()

#crear endpoint crear doctor relacionado con un usuario
@router.post("/doctors", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["Doctor"])
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Configurar el logger
    logger = logging.getLogger("doctor.create_doctor")

    #buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.idUsuario == current_user["idUsuario"]).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado: {current_user['idUsuario']}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    #verificar que solo los usuarios con rol doctor o usuario puedan crearlo
    if usuario.rol not in ["doc", "adm"]:
        logger.warning(f"Usuario sin permiso para crear doctor: {usuario.idUsuario} con rol {usuario.rol}")
        raise HTTPException(status_code=403, detail="No tienes permiso para crear un doctor")

    #verificar si ya existe un doctor relacionado con el usuario
    existing_doctor = db.query(Doctor).filter(Doctor.usuarioID == usuario.idUsuario).first()
    if existing_doctor:
        logger.warning(f"Intento de crear doctor duplicado para usuario: {usuario.idUsuario}")
        raise HTTPException(status_code=400, detail="Ya existe un doctor relacionado con este usuario")
    
    #verificar los datos para doctor
    if not doctor.nombreDoctor or not doctor.apellidoDoctor or not doctor.especialidad or not doctor.tlfDoctor or not doctor.horario or not doctor.sexo:
        logger.warning(f"Datos incompletos para crear doctor: {doctor}")
        raise HTTPException(status_code=400, detail="Todos los campos son obligatorios")
    
    #crear el nuevo doctor
    new_doctor = Doctor(usuarioID = usuario.idUsuario, nombreDoctor = doctor.nombreDoctor, apellidoDoctor = doctor.apellidoDoctor, especialidad = doctor.especialidad, tlfDoctor = doctor.tlfDoctor, horario = doctor.horario, sexo = doctor.sexo)

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    #orm - schema
    doctor_out = DoctorOut.model_validate(new_doctor, from_attributes=True)

    logger.info(f"Doctor creado exitosamente: {doctor_out}")
    return ApiResponse(
        statusCode=201,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Doctor creado exitosamente"],
        result=doctor_out
    )

#endpoint get doctor por id y que sea el autenticado
@router.get("/doctors/{idDoctor}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def get_doctor(idDoctor: int, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Configurar el logger
    logger = logging.getLogger("doctor.get_doctor")

    #buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.idUsuario == current_user["idUsuario"]).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado: {current_user['idUsuario']}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.rol not in ["doc", "adm"]:
        logger.warning(f"Usuario sin permiso para obtener doctor: {usuario.idUsuario} con rol {usuario.rol}")
        raise HTTPException(status_code=403, detail="No tienes permiso para obtener un doctor")
    
    # Query base
    query = db.query(Doctor).filter(Doctor.idDoctor == idDoctor)

    # Si es doctor, solo puede ver su propio registro
    if usuario.rol == "doc":
        query = query.filter(Doctor.usuarioID == usuario.idUsuario)

    doctor = query.first()
    if not doctor:
        logger.warning(f"Doctor no encontrado: {idDoctor}")
        raise HTTPException(status_code=404, detail="Doctor no encontrado")

    doctor_out = DoctorOut.model_validate(doctor, from_attributes=True)

    logger.info(f"Doctor obtenido exitosamente: {doctor_out}")
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=doctor_out
    )


#endpoint eliminar doctor
@router.delete("/doctors/{idDoctor}",response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def eliminar_doctor(idDoctor: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Configurar el logger
    logger = logging.getLogger("doctor.eliminar_doctor")
    #buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.idUsuario == current_user["idUsuario"]).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado: {current_user['idUsuario']}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    #verificar que solo los usuarios con rol doctor o usuario puedan eliminarlo
    if usuario.rol not in ["doc", "adm"]:
        logger.warning(f"Usuario sin permiso para eliminar doctor: {usuario.idUsuario} con rol {usuario.rol}")
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar un doctor")

    #buscar el doctor a eliminar
    doctor = db.query(Doctor).filter(Doctor.idDoctor == idDoctor, Doctor.usuarioID == usuario.idUsuario).first()
    if not doctor:
        logger.warning(f"Doctor no encontrado: {idDoctor} con nombre de usuario {usuario.nombreUsuario}")
        raise HTTPException(status_code=404, detail="Doctor no encontrado")

    db.delete(doctor)
    db.commit()
    doctor_out = DoctorOut.model_validate(doctor, from_attributes=True)

    logger.info(f"Doctor eliminado exitosamente: {doctor_out}")
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Doctor eliminado exitosamente"],
        result=doctor_out
    )

#endpoint actualizar doctor
@router.put("/doctors/{idDoctor}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def actualizar_doctor(idDoctor: int, doctor: DoctorCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Configurar el logger
    logger = logging.getLogger("doctor.actualizar_doctor")
    #buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.idUsuario == current_user["idUsuario"]).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado: {current_user['idUsuario']}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    #verificar que solo los usuarios con rol doctor o usuario puedan actualizarlo
    if usuario.rol not in ["doc", "adm"]:
        logger.warning(f"Usuario sin permiso para actualizar doctor: {usuario.idUsuario} con rol {usuario.rol}")
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar un doctor")

    #buscar el doctor a actualizar
    existing_doctor = db.query(Doctor).filter(Doctor.idDoctor == idDoctor, Doctor.usuarioID == usuario.idUsuario).first()
    if not existing_doctor:
        logger.warning(f"Doctor no encontrado: {idDoctor} con nombre de usuario {usuario.nombreUsuario}")
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

    doctor_out = DoctorOut.model_validate(existing_doctor, from_attributes=True)

    logger.info(f"Doctor actualizado exitosamente: {doctor_out}")
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Doctor actualizado exitosamente"],
        result=doctor_out
    )

#endpoint listar doctor
@router.get("/doctors", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Doctor"])
def doctores(pageSize: int = 0,pageNumber: int = 1,db: Session = Depends(get_db),current_user: dict = Security(get_current_user)):
    logger = logging.getLogger("doctor.doctores")

    #buscar el usuario autenticado
    usuario = db.query(Usuario).filter(Usuario.idUsuario == current_user["idUsuario"]).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado: {current_user['idUsuario']}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.rol != "adm":
        logger.warning(f"Usuario sin permiso para listar doctores: {usuario.idUsuario} con rol {usuario.rol}")
        raise HTTPException(status_code=403, detail="No tiene permiso para listar doctores")

    query = db.query(Doctor)

    if pageSize > 0:
        query = query.offset(pageSize * (pageNumber - 1)).limit(pageSize)

    doctores = query.all()
    doctores_out = [DoctorOut.model_validate(doctor, from_attributes=True) for doctor in doctores]
    #logger info
    logger.info(f"Doctores listados exitosamente: {len(doctores_out)} doctores encontrados")
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=doctores_out
    )