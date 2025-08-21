from fastapi import APIRouter, Depends, HTTPException, status, Security, Path
from sqlalchemy.orm import Session
from app.schemas import usuario
from app.schemas.citamedica.citamedica import CitaMedicaCreate, CitaMedicaOut
from app.models.citamedica.citamedica import CitaMedica
from app.models.paciente.paciente import Paciente
from app.models.usuario.usuario import Usuario

from app.api.deps import get_current_user, get_db

router = APIRouter()


#endpoint crear cita medica, solo para el rol ptn
@router.post("/cita-medica", response_model=CitaMedicaOut, status_code=status.HTTP_201_CREATED, tags=["Cita Medica"])
def crear_cita_medica(cita_in: CitaMedicaCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    print(current_user)

    #agregar validacion que solo pacientes pueden agendar cita medica
    if current_user["rol"] != "ptn":
        raise HTTPException(status_code=403, detail="No tiene permisos para crear una cita médica")

    paciente = db.query(Paciente).filter(Paciente.usuarioID == current_user["idUsuario"]).first()
    print(current_user["idUsuario"])

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    #validar el rol ptn
    if current_user["rol"] != "ptn":
        raise HTTPException(status_code=403, detail="No tiene permisos para crear una cita médica")

    #verificar los campos que con requeridos de cita
    if cita_in.fechaCita is None or not cita_in.hora or cita_in.estado is None:
        raise HTTPException(status_code=400, detail="Fecha, hora y estado de la cita son requeridos")

    #verificar si ya existe una cita médica para el paciente en la misma fecha
    cita_existente = db.query(CitaMedica).filter(
        CitaMedica.pacienteID == paciente.idPaciente,
        CitaMedica.fechaCita == cita_in.fechaCita
    ).first()

    if cita_existente:
        raise HTTPException(status_code=400, detail="Ya existe una cita médica para el paciente en esta fecha")
    
    # Crear la cita
    nueva_cita = CitaMedica(
        pacienteID=paciente.idPaciente,
        fechaCita=cita_in.fechaCita,
        hora=cita_in.hora,
        estado=cita_in.estado
    )
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)

    return nueva_cita

#endpoints citas para pacientes
@router.get("/citas-paciente", response_model=list[CitaMedicaOut], tags=["Cita Medica"])
def  listar_citas(pageSize: int = 0, pageNumber: int = 1, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    paciente = db.query(Paciente).filter(Paciente.usuarioID == current_user["idUsuario"]).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    #listar todas las citas medicas con la paginacion
    query = db.query(CitaMedica).filter(CitaMedica.pacienteID == paciente.idPaciente)

    # solo aplicar paginación si pageSize > 0
    if pageSize > 0:
        query = query.offset(pageSize * (pageNumber - 1)).limit(pageSize)

    #consultar citas
    citas = query.all()
    
    return citas


#endpoint para las citas de un paciente - idPaciente
@router.get("/citas-paciente/{id_paciente}", response_model=list[CitaMedicaOut], tags=["Cita Medica"])
def  citas_paciente_id(id_paciente: int, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):

    #verificar el id del paciente sea valido o int
    if not isinstance(id_paciente, int):
        raise HTTPException(status_code=400, detail="ID de paciente inválido")

    paciente = db.query(Paciente).filter(Paciente.idPaciente == id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    

    citas = db.query(CitaMedica).filter(CitaMedica.pacienteID == paciente.idPaciente).all()

     #si el paciente no tiene citas medicas mostrar mensaje
    if not citas:
        raise HTTPException(status_code=404, detail="No se encontraron citas médicas para el paciente")

    return citas

#endpoint para actualizar cita medica
@router.put("/cita-medica/{id_cita}", response_model=CitaMedicaOut, status_code=status.HTTP_200_OK, tags=["Cita Medica"])
def actualizar_cita(id_cita: int, cita_in: CitaMedicaCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    #verificar que el usuario actual es un paciente
    if current_user["rol"] != "ptn":
        raise HTTPException(status_code=403, detail="No tiene permisos para actualizar una cita médica")

    #verificar que la cita existe
    cita = db.query(CitaMedica).filter(CitaMedica.idCita == id_cita).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita médica no encontrada")

    #verificar que la cita pertenece al paciente
    paciente = db.query(Paciente).filter(Paciente.idPaciente == cita.pacienteID).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if paciente.usuarioID != current_user["idUsuario"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para actualizar esta cita médica")

    #actualizar los campos de la cita
    cita.fechaCita = cita_in.fechaCita
    cita.hora = cita_in.hora
    cita.estado = cita_in.estado

    db.commit()
    db.refresh(cita)

    return cita

#endpoint para actualizar por patch
@router.patch("/cita-medica/{id_cita}", response_model=CitaMedicaOut, status_code=status.HTTP_200_OK, tags=["Cita Medica"])
def actualizar_cita_parcial(id_cita: int, cita_in: CitaMedicaCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    #verificar que el usuario actual es un paciente
    if current_user["rol"] != "ptn":
        raise HTTPException(status_code=403, detail="No tiene permisos para actualizar una cita médica")

    #verificar que la cita existe
    cita = db.query(CitaMedica).filter(CitaMedica.idCita == id_cita).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita médica no encontrada")

    #verificar que la cita pertenece al paciente
    paciente = db.query(Paciente).filter(Paciente.idPaciente == cita.pacienteID).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if paciente.usuarioID != current_user["idUsuario"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para actualizar esta cita médica")

    #actualizar los campos de la cita
    if cita_in.fechaCita:
        cita.fechaCita = cita_in.fechaCita
    if cita_in.hora:
        cita.hora = cita_in.hora
    if cita_in.estado:
        cita.estado = cita_in.estado

    db.commit()
    db.refresh(cita)

    return cita

#endpoint para eliminar las citas
@router.delete("/cita-medica/{id_cita}", status_code=status.HTTP_204_NO_CONTENT, tags=["Cita Medica"])
def eliminar_cita(id_cita: int, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    #verificar que el usuario actual es un paciente
    if current_user["rol"] != "ptn":
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar una cita médica")

    #verificar que la cita existe
    cita = db.query(CitaMedica).filter(CitaMedica.idCita == id_cita).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita médica no encontrada")

    #verificar que la cita pertenece al paciente
    paciente = db.query(Paciente).filter(Paciente.idPaciente == cita.pacienteID).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if paciente.usuarioID != current_user["idUsuario"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar esta cita médica")

    db.delete(cita)
    db.commit()

    return {"detail": "Cita médica eliminada"}