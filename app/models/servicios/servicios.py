from sqlalchemy import Column, Integer, String, Text, DECIMAL, UniqueConstraint
from app.db.base import Base

class Servicios(Base):
    __tablename__ = "servicios"
    __table_args__ = (
        UniqueConstraint("nombreServicio", name="uq_servicios_nombreServicio"),
    )
    idServicios = Column(Integer, primary_key=True, index=True)
    nombreServicio = Column(String(45), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    costo = Column(DECIMAL, nullable=False)
