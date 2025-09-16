from fastapi import APIRouter, Depends, HTTPException, status, Security, Path
from sqlalchemy.orm import Session
from app.schemas import usuario
from app.schemas.citamedica.citamedica import CitaMedicaCreate, CitaMedicaOut
from app.schemas.ApiResponse.response import ApiResponse
from app.models.citamedica.citamedica import CitaMedica
from app.models.paciente.paciente import Paciente
from app.models.usuario.usuario import Usuario
from app.api.deps import get_current_user, get_db
import logging

router = APIRouter()


#endpoint crear cita medica, solo para el rol ptn
@router.post("/cita-medica", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["Cita Medica"])
def crear_cita_medica(cita_in: CitaMedicaCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    try:
        logger = logging.getLogger("cita_medica.crear_cita_medica")
        
        #agregar validacion que solo pacientes pueden agendar cita medica
        if current_user["rol"] != "ptn":
            logger.warning(f"Usuario sin permiso para crear cita médica: {current_user['idUsuario']} con rol {current_user['rol']}")
            raise HTTPException(status_code=403, detail="No tiene permisos para crear una cita médica")

        paciente = db.query(Paciente).filter(Paciente.usuarioID == current_user["idUsuario"]).first()
        logger.info(f"Usuario autenticado: {current_user['idUsuario']}, rol: {current_user['rol']}")

        if not paciente:
            logger.error(f"Paciente no encontrado para el usuario: {current_user['idUsuario']}")
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        #validar el rol ptn
        if current_user["rol"] != "ptn":
            logger.warning(f"Usuario sin permiso para crear cita médica: {current_user['idUsuario']} con rol {current_user['rol']}")
            raise HTTPException(status_code=403, detail="No tiene permisos para crear una cita médica")

        #verificar los campos que con requeridos de cita
        if cita_in.fechaCita is None or not cita_in.hora or cita_in.estado is None:
            logger.warning(f"Datos incompletos para crear cita médica: {cita_in}")
            raise HTTPException(status_code=400, detail="Fecha, hora y estado de la cita son requeridos")

        #verificar si ya existe una cita médica para el paciente en la misma fecha
        cita_existente = db.query(CitaMedica).filter(
            CitaMedica.pacienteID == paciente.idPaciente,
            CitaMedica.fechaCita == cita_in.fechaCita
        ).first()

        if cita_existente:
            logger.warning(f"Cita médica ya existente para el paciente {paciente.idPaciente} en la fecha {cita_in.fechaCita}")
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
        cita_out = CitaMedicaOut.model_validate(nueva_cita, from_attributes=True)

        return ApiResponse(
            statusCode=201,
            isSuccess=True,
            errorMessages=[],
            successMessages=["Cita médica creada exitosamente"],
            result=cita_out
        )
    except Exception as e:
        logging.error(f"Error al crear cita médica: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


#endpoints citas para pacientes
@router.get("/citas-paciente", response_model=ApiResponse, tags=["Cita Medica"])
def  listar_citas(pageSize: int = 0, pageNumber: int = 1, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    try:
        logger = logging.getLogger("cita_medica.listar_citas")

        #buscar usuario autenticado
        usuario = db.query(Usuario).filter(Usuario.idUsuario == current_user["idUsuario"]).first()
        if not usuario:
            logger.error(f"Usuario no encontrado: {current_user['idUsuario']}")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        #verificar rol adm - doc
        if usuario.rol not in ["adm", "doc"]:
            logger.warning(f"Usuario sin permiso para acceder a citas médicas: {current_user['idUsuario']} con rol {current_user['rol']}")
            raise HTTPException(status_code=403, detail="No tiene permisos para acceder a las citas médicas")

        query = db.query(CitaMedica)

        # solo aplicar paginación si pageSize > 0
        if pageSize > 0:
            query = query.offset(pageSize * (pageNumber - 1)).limit(pageSize)

        #consultar citas
        citas = query.all()

        citas_out = [CitaMedicaOut.model_validate(cita, from_attributes=True) for cita in citas]
        # Log de información
        logger.info(f"Citas médicas obtenidas exitosamente por el usuario: {current_user['idUsuario']}")
        return ApiResponse(
            statusCode=200,
            isSuccess=True,
            errorMessages=[],
            successMessages=["Citas médicas obtenidas exitosamente"],
            result=citas_out
        )
    except Exception as e:
        logging.error(f"Error al listar citas médicas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


#endpoint para las citas de un paciente - idPaciente
#podran verlas doctores,pacientes, doctores
@router.get("/citas-paciente/{id_paciente}", response_model=ApiResponse, tags=["Cita Medica"])
def  citas_paciente_id(id_paciente: int, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    try: 
        #logger de la funcion
        logger = logging.getLogger("cita_medica.citas_paciente_id")

        # Buscar el usuario autenticado
        usuario = db.query(Usuario).filter(Usuario.idUsuario == current_user["idUsuario"]).first()

        # Verificar que el usuario tenga rol adecuado
        if usuario.rol not in ["ptn", "adm", "doc"]:
            logger.warning(f"Usuario sin permiso para ver citas: {current_user['idUsuario']} con rol {current_user['rol']}")
            raise HTTPException(status_code=403, detail="No tiene permiso para ver las citas")
        
        paciente = db.query(Paciente).filter(Paciente.idPaciente == id_paciente).first()
        if not paciente:
            logger.error(f"Paciente no encontrado para el usuario: {current_user['idUsuario']}")
            raise HTTPException(status_code=404, detail="Paciente no encontrado o No Existe")
        

        citas = db.query(CitaMedica).filter(CitaMedica.pacienteID == paciente.idPaciente).all()
        #si el paciente no tiene citas medicas mostrar mensaje
        if not citas:
            logger.warning(f"No se encontraron citas médicas para el paciente: {paciente.idPaciente}")
            raise HTTPException(status_code=404, detail="No se encontraron citas médicas para el paciente")

        citas_out = [CitaMedicaOut.model_validate(cita, from_attributes=True) for cita in citas]

        logger.info(f"Citas médicas obtenidas exitosamente para el paciente: {paciente.idPaciente} por el usuario: {current_user['idUsuario']}")
        return ApiResponse(
            statusCode=200,
            isSuccess=True,
            errorMessages=[],
            successMessages=["Citas médicas obtenidas exitosamente"],
            result=citas_out
        )
    except Exception as e:
        logging.error(f"Error al listar citas médicas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

#endpoint para actualizar cita medica
@router.put("/cita-medica/{id_cita}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Cita Medica"])
def actualizar_cita(id_cita: int, cita_in: CitaMedicaCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    try:
        #logger de la funcion
        logger = logging.getLogger("cita_medica.actualizar_cita")
        #verificar que el usuario actual es un paciente
        if current_user["rol"] != "ptn":
            logger.warning(f"Usuario sin permiso para actualizar cita médica: {current_user['idUsuario']} con rol {current_user['rol']}")
            raise HTTPException(status_code=403, detail="No tiene permisos para actualizar una cita médica")

        #verificar que la cita existe
        cita = db.query(CitaMedica).filter(CitaMedica.idCita == id_cita).first()
        if not cita:
            logger.error(f"Cita médica no encontrada: {id_cita}")
            raise HTTPException(status_code=404, detail="Cita médica no encontrada")

        #verificar que la cita pertenece al paciente
        paciente = db.query(Paciente).filter(Paciente.idPaciente == cita.pacienteID).first()
        if not paciente:
            logger.error(f"Paciente no encontrado para la cita médica: {id_cita}")
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        if paciente.usuarioID != current_user["idUsuario"]:
            logger.warning(f"Usuario sin permiso para actualizar esta cita médica: {current_user['idUsuario']} con rol {current_user['rol']}")
            raise HTTPException(status_code=403, detail="No tiene permisos para actualizar esta cita médica")

        #actualizar los campos de la cita
        cita.fechaCita = cita_in.fechaCita
        cita.hora = cita_in.hora
        cita.estado = cita_in.estado

        db.commit()
        db.refresh(cita)

        cita_out = CitaMedicaOut.model_validate(cita, from_attributes=True)

        logger.info(f"Cita médica actualizada exitosamente: {id_cita} por el usuario: {current_user['idUsuario']}")
        return ApiResponse(
            statusCode=200,
            isSuccess=True,
            errorMessages=[],
            successMessages=["Cita médica actualizada exitosamente"],
            result=cita_out
        )
    except Exception as e:
        logging.error(f"Error al actualizar cita médica: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

#endpoint para actualizar por patch
@router.patch("/cita-medica/{id_cita}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Cita Medica"])
def actualizar_cita_parcial(id_cita: int, cita_in: CitaMedicaCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    try:
        logger = logging.getLogger("cita_medica.actualizar_cita_parcial")
        #verificar que el usuario actual es un paciente
        if current_user["rol"] != "ptn":
            logger.warning(f"Usuario sin permiso para actualizar cita médica: {current_user['idUsuario']} con rol {current_user['rol']}")   
            raise HTTPException(status_code=403, detail="No tiene permisos para actualizar una cita médica")

        #verificar que la cita existe
        cita = db.query(CitaMedica).filter(CitaMedica.idCita == id_cita).first()
        if not cita:
            logger.error(f"Cita médica no encontrada: {id_cita}")
            raise HTTPException(status_code=404, detail="Cita médica no encontrada")

        #verificar que la cita pertenece al paciente
        paciente = db.query(Paciente).filter(Paciente.idPaciente == cita.pacienteID).first()
        if not paciente:
            logger.error(f"Paciente no encontrado para la cita médica: {id_cita}")
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        if paciente.usuarioID != current_user["idUsuario"]:
            logger.warning(f"Usuario sin permiso para actualizar esta cita médica: {current_user['idUsuario']} con rol {current_user['rol']}")
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

        cita_out = CitaMedicaOut.model_validate(cita, from_attributes=True)

        # Log de información
        logger.info(f"Cita médica actualizada exitosamente: {id_cita} por el usuario: {current_user['idUsuario']}")
        return ApiResponse(
            statusCode=200,
            isSuccess=True,
            errorMessages=[],
            successMessages=["Cita médica actualizada exitosamente"],
            result=cita_out
        )
    except Exception as e:
        logging.error(f"Error al actualizar cita médica: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

#endpoint para eliminar las citas
@router.delete("/cita-medica/{id_cita}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Cita Medica"])
def eliminar_cita(id_cita: int, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    try:
        logger = logging.getLogger("cita_medica.eliminar_cita")
        #verificar que el usuario actual es un paciente
        if current_user["rol"] != "ptn":
            logger.warning(f"Usuario sin permiso para eliminar cita médica: {current_user['idUsuario']} con rol {current_user['rol']}")
            raise HTTPException(status_code=403, detail="No tiene permisos para eliminar una cita médica")

        #verificar que la cita existe
        cita = db.query(CitaMedica).filter(CitaMedica.idCita == id_cita).first()
        if not cita:
            logger.error(f"Cita médica no encontrada: {id_cita}")
            raise HTTPException(status_code=404, detail="Cita médica no encontrada")

        #verificar que la cita pertenece al paciente
        paciente = db.query(Paciente).filter(Paciente.idPaciente == cita.pacienteID).first()
        if not paciente:
            logger.error(f"Paciente no encontrado para la cita médica: {id_cita}")
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        if paciente.usuarioID != current_user["idUsuario"]:
            logger.warning(f"Usuario sin permiso para eliminar esta cita médica: {current_user['idUsuario']} con rol {current_user['rol']}")
            raise HTTPException(status_code=403, detail="No tiene permisos para eliminar esta cita médica")

        db.delete(cita)
        db.commit()

        cita_out = CitaMedicaOut.model_validate(cita, from_attributes=True)
        # Log de información
        logger.info(f"Cita médica eliminada exitosamente: {id_cita} por el usuario: {current_user['idUsuario']}")
        return ApiResponse(
            statusCode=204,
            isSuccess=True,
            errorMessages=[],
            successMessages=["Cita médica eliminada exitosamente"],
            result=cita_out
        )
    except Exception as e:
        logging.error(f"Error al eliminar cita médica: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")