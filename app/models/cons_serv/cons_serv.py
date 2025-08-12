from sqlalchemy import Column, Integer, ForeignKey
from app.db.base import Base

class ConsServ(Base):
    __tablename__ = "cons_serv"
    idCons_Serv = Column(Integer, primary_key=True, index=True)
    servicios = Column(Integer, ForeignKey("servicios.idServicios"))
    consultaID = Column(Integer, ForeignKey("consulta.idConsulta"))
