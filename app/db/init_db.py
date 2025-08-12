from app.db.session import engine
from app.db.base import Base
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

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
