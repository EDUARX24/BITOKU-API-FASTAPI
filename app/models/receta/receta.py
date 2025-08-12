from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class Receta(Base):
    __tablename__ = "receta"
    idReceta = Column(Integer, primary_key=True, index=True)
    consultaID = Column(Integer, ForeignKey("consulta.idConsulta"))
    medicamento = Column(String(80), nullable=False)
    presentacion = Column(String(15), nullable=False)
    dosis = Column(String(45), nullable=False)
    duracion = Column(String(45), nullable=False)
    cantidad = Column(Integer, nullable=False)
