from fastapi import APIRouter, Depends, HTTPException, status, Security, Path
from sqlalchemy.orm import Session
from app.schemas.ApiResponse.response import ApiResponse
from app.schemas.servicios import ServiciosCreate, ServiciosOut, ServiciosUpdate
from app.models.servicios import Servicios

from app.api.deps import get_current_user, get_db

router = APIRouter()

@router.post("/servicios", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["Servicios"])
def crear_servicio(servicio_in: ServiciosCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Verificar que el usuario actual es un doctor o admin
    if current_user["rol"] != "doc" and current_user["rol"] != "adm":
        raise HTTPException(status_code=403, detail="No tiene permisos para crear un servicio")

    # Validar los campos requeridos
    if not servicio_in.nombreServicio or not servicio_in.descripcion or not servicio_in.costo:
        raise HTTPException(status_code=400, detail="Todos los campos son requeridos")
    
    #validar que ya exista un servicio
    servicio_existente = db.query(Servicios).filter(Servicios.nombreServicio == servicio_in.nombreServicio).first()
    if servicio_existente:
        raise HTTPException(status_code=409, detail="El servicio ya existe")
    
    #crear el servicio
    add_servicio = Servicios(
        nombreServicio=servicio_in.nombreServicio,
        descripcion=servicio_in.descripcion,
        costo=servicio_in.costo,
    )
    db.add(add_servicio)
    db.commit()
    db.refresh(add_servicio)
    servicio_out = ServiciosOut.model_validate(add_servicio, from_attributes=True)

    #retorna el servicio creado
    return ApiResponse(
        statusCode=201,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicio creado exitosamente"],
        result=servicio_out
    )


#ENDPOINT PARA OBTENER TODOS LOS SERVICIOS 
@router.get("/servicios", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Servicios"])
def obtener_servicios(pageSize: int = 0, pageNumber: int = 1,db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Verificar que el usuario actual es un doctor, paciente o admin
    if current_user["rol"] not in ["doc", "ptn", "adm"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver los servicios")

    query = db.query(Servicios)

    #aplicar la paginacion
    if pageSize > 0:
        query = query.limit(pageSize)
    if pageNumber > 1:
        query = query.offset((pageNumber - 1) * pageSize)

    servicios = query.all()
    servicios_out = [ServiciosOut.model_validate(servicio, from_attributes=True) for servicio in servicios]

    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicios obtenidos exitosamente"],
        result=servicios_out
    )

#ENDPOINT OBTENER SERVICIO POR ID
@router.get("/servicios/{servicio_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Servicios"])
def obtener_servicio(servicio_id: int, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Verificar que el usuario actual es un doctor, admin
    if current_user["rol"] not in ["doc", "adm"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver el servicio")

    servicio = db.query(Servicios).filter(Servicios.idServicios == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    servicio_out = ServiciosOut.model_validate(servicio, from_attributes=True)

    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicio obtenido exitosamente"],
        result=servicio_out
    )

#ENDPOINT PARA ACTUALIZAR SERVICIO PATCH
@router.patch("/servicios/{servicio_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Servicios"])
def actualizar_servicio(servicio_id: int, servicio_in: ServiciosUpdate, db: Session = Depends(get_db),current_user: dict = Security(get_current_user)):
    # Verificar permisos
    if current_user["rol"] not in ["doc", "adm"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para actualizar el servicio")

    # Buscar servicio
    servicio = db.query(Servicios).filter(Servicios.idServicios == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    # Tomar solo los campos enviados
    update_data = servicio_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(servicio, key, value)

    db.commit()
    db.refresh(servicio)

    servicio_out = ServiciosOut.model_validate(servicio, from_attributes=True)

    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicio actualizado exitosamente"],
        result=servicio_out
    )

#ENDPOINT ELIMINAR SERVICIO
@router.delete("/servicios/{servicio_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK, tags=["Servicios"])
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db), current_user: dict = Security(get_current_user)):
    # Verificar permisos
    if current_user["rol"] not in ["doc", "adm"]:
        raise HTTPException(status_code=403, detail="No tiene permisos para eliminar el servicio")

    # Buscar servicio
    servicio = db.query(Servicios).filter(Servicios.idServicios == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    db.delete(servicio)
    db.commit()

    return ApiResponse(
        statusCode=200,
        isSuccess=True,
        errorMessages=[],
        successMessages=["Servicio eliminado exitosamente"],
        result=None
    )
