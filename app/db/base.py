# Base para modelos ORM
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Importa todos los modelos para que Base los registre
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.models.doctor import Doctor
from app.models.citamedica import CitaMedica
from app.models.servicios import Servicios
from app.models.consulta import Consulta
from app.models.cons_serv import ConsServ
from app.models.receta import Receta
from app.models.app import App
from app.models.apf import Apf
from app.models.expediente import Expediente