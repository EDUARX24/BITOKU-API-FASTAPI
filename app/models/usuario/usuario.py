from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuario"
    idUsuario = Column(Integer, primary_key=True, index=True)
    nombreUsuario = Column(String(45), nullable=False)
    contrasenia = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False)
    pacientes = relationship("Paciente", back_populates="usuario")
    doctores = relationship("Doctor", back_populates="usuario")
