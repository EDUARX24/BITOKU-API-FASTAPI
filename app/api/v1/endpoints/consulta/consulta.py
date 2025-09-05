from fastapi import APIRouter, Depends, HTTPException, status, Security, Path
from sqlalchemy.orm import Session
from app.schemas import doctor, usuario
from app.schemas.consulta.consulta import ConsultaCreate, ConsultaOut
from app.schemas.ApiResponse.response import ApiResponse
from app.models.consulta.consulta import Consulta
from app.models.cons_serv.cons_serv import ConsServ
from app.models.citamedica.citamedica import CitaMedica
from app.models.doctor.doctor import Doctor
from app.api.deps import get_current_user, get_db

router = APIRouter()

#Endpoint para crear una consulta médica, solo para el rol doctor
@router.post("/consulta", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["Consulta"])
def crear_consulta(consulta_in: ConsultaCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Validar que solo los doctores puedan crear una consulta médica
    if current_user["rol"] != "doc":
        return ApiResponse(
            statusCode=403,
            isSuccess=False,
            errorMessages=["No tiene permisos para crear una consulta médica"],
            successMessages=[],
            result=None
        )

    # # Validar que exista la cita asociada
    # cita = db.query(Consulta).filter(Consulta.citaID == consulta_in.citaID).first()
    # if not cita:
    #     return ApiResponse(
    #         statusCode=404,
    #         isSuccess=False,
    #         errorMessages=["Cita no encontrada"],
    #         successMessages=[],
    #         result=None
    #     )

    # Validar que la cita no tenga ya una consulta asociada
    consulta_existente = db.query(Consulta).filter(Consulta.citaID == consulta_in.citaID).first()
    if consulta_existente:
        return ApiResponse(
            statusCode=409,
            isSuccess=False,
            errorMessages=["Ya existe una consulta para esta cita"],
            successMessages=[],
            result=None
        )

    # Validar que el doctor exista
    doctor = db.query(Doctor).filter(Doctor.usuarioID == current_user["idUsuario"]).first()
    if not doctor:
        return ApiResponse(
            statusCode=404,
            isSuccess=False,
            errorMessages=["Doctor no encontrado"],
            successMessages=[],
            result=None
        )

    # Validar que los campos requeridos estén presentes
    if not consulta_in.valoracion or not consulta_in.fechaConsulta:
        return ApiResponse(
            statusCode=400,
            isSuccess=False,
            errorMessages=["Valoración y fecha de consulta son requeridos"],
            successMessages=[],
            result=None
        )

    # Validar que la fecha de consulta no sea anterior a la fecha de la cita
    # (si tienes acceso a la fecha de la cita)
    cita_obj = db.query(CitaMedica).filter(CitaMedica.idCita == consulta_in.citaID).first()
    if cita_obj and consulta_in.fechaConsulta < cita_obj.fechaCita:
        return ApiResponse(
            statusCode=400,
            isSuccess=False,
            errorMessages=["La fecha de la consulta no puede ser anterior a la fecha de la cita"],
            successMessages=[],
            result=None
        )

    # Validar que los servicios existan y no estén duplicados
    servicios_ids = set()
    error_servicios = []
    for servicio_id in consulta_in.servicios:
        if servicio_id in servicios_ids:
            error_servicios.append(f"Servicio duplicado: {servicio_id}")
        else:
            servicio = db.query(ConsServ).filter(ConsServ.servicios == servicio_id).first()
            if not servicio:
                error_servicios.append(f"Servicio no encontrado: {servicio_id}")
            servicios_ids.add(servicio_id)
    if error_servicios:
        return ApiResponse(
            statusCode=400,
            isSuccess=False,
            errorMessages=error_servicios,
            successMessages=[],
            result=None
        )

    # Crear la consulta médica
    nueva_consulta = Consulta(
        doctorID=current_user["idUsuario"],
        citaID=consulta_in.citaID,
        valoracion=consulta_in.valoracion,
        fechaConsulta=consulta_in.fechaConsulta,
    )
    db.add(nueva_consulta)
    db.commit()
    db.refresh(nueva_consulta)
    consulta_out = ConsultaOut.model_validate(nueva_consulta, from_attributes=True)

    # Asociar los servicios a la consulta
    for servicio_id in consulta_in.servicios:
        cons_serv = ConsServ(
            consultaID=consulta_out.idConsulta,
            servicios=servicio_id
        )
        db.add(cons_serv)
    db.commit()

    return ApiResponse(
        statusCode=201,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Consulta médica creada exitosamente"],
        result=consulta_out
    )

#endpoint para listar todas las consultas medicas, solo para rol doctor y admin
@router.get("/consultas", response_model=ApiResponse, tags=["Consulta"])
def listar_consultas(pageSize: int = 0, pageNumber: int = 1, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Validar que solo los doctores y administradores puedan listar las consultas médicas
    if current_user["rol"] not in ["doc", "adm"]:
        return ApiResponse(
            statusCode=403,
            isSuccess=False,
            errorMessages=["No tiene permisos para listar consultas médicas"],
            successMessages=[],
            result=None
        )

    query = db.query(Consulta)

    # solo aplicar paginación si pageSize > 0
    if pageSize > 0:
        query = query.offset(pageSize * (pageNumber - 1)).limit(pageSize)

    consultas = query.all()
    consultas_out = [ConsultaOut.model_validate(consulta, from_attributes=True) for consulta in consultas]

    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=consultas_out
    )

#endpoint para obtener una consulta por id, solo para rol doctor y admin
@router.get("/consulta/{id_consulta}", response_model=ApiResponse, tags=["Consulta"])
def obtener_consulta(id_consulta: int = Path(..., gt=0), db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Validar que solo los doctores y administradores puedan obtener una consulta médica
    if current_user["rol"] not in ["doc", "adm"]:
        return ApiResponse(
            statusCode=403,
            isSuccess=False,
            errorMessages=["No tiene permisos para ver esta consulta médica"],
            successMessages=[],
            result=None
        )

    consulta = db.query(Consulta).filter(Consulta.idConsulta == id_consulta).first()
    if not consulta:
        return ApiResponse(
            statusCode=404,
            isSuccess=False,
            errorMessages=["Consulta no encontrada"],
            successMessages=[],
            result=None
        )

    consulta_out = ConsultaOut.model_validate(consulta, from_attributes=True)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=[],
        result=consulta_out
    )

#endpoint eliminar una consulta por id, solo para rol admin o doctor
@router.delete("/consulta/{id_consulta}", response_model=ApiResponse, tags=["Consulta"])
def eliminar_consulta(id_consulta: int = Path(..., gt=0), db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Validar que solo los doctores y administradores puedan eliminar una consulta médica
    if current_user["rol"] not in ["doc", "adm"]:
        return ApiResponse(
            statusCode=403,
            isSuccess=False,
            errorMessages=["No tiene permisos para eliminar esta consulta médica"],
            successMessages=[],
            result=None
        )

    consulta_out = db.query(Consulta).filter(Consulta.idConsulta == id_consulta).first()
    if not consulta_out:
        return ApiResponse(
            statusCode=404,
            isSuccess=False,
            errorMessages=["Consulta no encontrada"],
            successMessages=[],
            result=None
        )

    db.delete(consulta_out)
    db.commit()
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Consulta eliminada exitosamente"],
        result=consulta_out
    )

#ENDPOINT ACTUALIZAR CONSULTA, solo para rol doctor
@router.put("/consulta/{id_consulta}", response_model=ApiResponse, tags=["Consulta"])
def actualizar_consulta(id_consulta: int = Path(..., gt=0), consulta_in: ConsultaCreate = None, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):    
    # Validar que solo los doctores puedan actualizar una consulta médica
    if current_user["rol"] != "doc":
        return ApiResponse(
            statusCode=403,
            isSuccess=False,
            errorMessages=["No tiene permisos para actualizar esta consulta médica"],
            successMessages=[],
            result=None
        )

    consulta = db.query(Consulta).filter(Consulta.idConsulta == id_consulta).first()
    if not consulta:
        return ApiResponse(
            statusCode=404,
            isSuccess=False,
            errorMessages=["Consulta no encontrada"],
            successMessages=[],
            result=None
        )

    # Actualizar los campos de la consulta
    consulta.fechaConsulta = consulta_in.fechaConsulta
    consulta.valoracion = consulta_in.valoracion

    db.commit()
    db.refresh(consulta)

    consulta_out = ConsultaOut.model_validate(consulta, from_attributes=True)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Consulta actualizada exitosamente"],
        result=consulta_out
    )

#ENDPOINT ACTUALIZAR CONSULTA, solo para rol doctor PATCH
@router.patch("/consulta/{id_consulta}", response_model=ApiResponse, tags=["Consulta"])
def actualizar_parcial_consulta(id_consulta: int = Path(..., gt=0), consulta_in: ConsultaCreate = None, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Validar que solo los doctores puedan actualizar una consulta médica
    if current_user["rol"] != "doc":
        return ApiResponse(
            statusCode=403,
            isSuccess=False,
            errorMessages=["No tiene permisos para actualizar esta consulta médica"],
            successMessages=[],
            result=None
        )

    consulta = db.query(Consulta).filter(Consulta.idConsulta == id_consulta).first()
    if not consulta:
        return ApiResponse(
            statusCode=404,
            isSuccess=False,
            errorMessages=["Consulta no encontrada"],
            successMessages=[],
            result=None
        )

    # Actualizar los campos de la consulta si se proporcionan
    if consulta_in.fechaConsulta:
        consulta.fechaConsulta = consulta_in.fechaConsulta
    if consulta_in.valoracion:
        consulta.valoracion = consulta_in.valoracion

    db.commit()
    db.refresh(consulta)

    consulta_out = ConsultaOut.model_validate(consulta, from_attributes=True)
    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Consulta actualizada exitosamente"],
        result=consulta_out
    )