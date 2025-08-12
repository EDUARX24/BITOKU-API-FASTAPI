from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Paciente(Base):
    __tablename__ = "paciente"
    idPaciente = Column(Integer, primary_key=True, index=True)
    usuarioID = Column(Integer, ForeignKey("usuario.idUsuario"))
    nombrePaciente = Column(String(70), nullable=False)
    apellidoPaciente = Column(String(70), nullable=False)
    cedula = Column(String(45), nullable=False)
    telefono = Column(Integer, nullable=False)
    fechaNacimiento = Column(Date, nullable=False)
    sexo = Column(String(30), nullable=False)
    usuario = relationship("Usuario", back_populates="pacientes")
