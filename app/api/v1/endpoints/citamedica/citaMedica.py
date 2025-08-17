from fastapi import APIRouter, Depends, HTTPException, status, Security
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