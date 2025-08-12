from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Doctor(Base):
    __tablename__ = "doctor"
    idDoctor = Column(Integer, primary_key=True, index=True)
    usuarioID = Column(Integer, ForeignKey("usuario.idUsuario"))
    nombreDoctor = Column(String(45), nullable=False)
    apellidoDoctor = Column(String(45), nullable=False)
    tlfDoctor = Column(Integer, nullable=False)
    especialidad = Column(String(45), nullable=False)
    horario = Column(String(45))
    sexo = Column(String(30), nullable=False)
    usuario = relationship("Usuario", back_populates="doctores")
