from sqlalchemy import Column, Integer, String, Text, DECIMAL
from app.db.base import Base

class Servicios(Base):
    __tablename__ = "servicios"
    idServicios = Column(Integer, primary_key=True, index=True)
    nombreServicio = Column(String(45), nullable=False)
    descripcion = Column(Text, nullable=False)
    costo = Column(DECIMAL, nullable=False)
