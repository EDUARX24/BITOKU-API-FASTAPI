
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Usuario(Base):
    """
    Modelo SQLAlchemy para la tabla 'usuario'.
    Representa a los usuarios del sistema, con relaciones a pacientes y doctores.
    """
    __tablename__ = "usuario"
    idUsuario = Column(Integer, primary_key=True, index=True)
    nombreUsuario = Column(String(45), nullable=False)
    contrasenia = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False)
    pacientes = relationship("Paciente", back_populates="usuario")
    doctores = relationship("Doctor", back_populates="usuario")
