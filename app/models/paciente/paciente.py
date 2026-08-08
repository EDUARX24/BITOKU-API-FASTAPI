from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class Paciente(Base):
    __tablename__ = "paciente"
    __table_args__ = (
        UniqueConstraint("usuarioID", name="uq_paciente_usuarioID"),
        UniqueConstraint("cedula", name="uq_paciente_cedula"),
    )
    idPaciente = Column(Integer, primary_key=True, index=True)
    usuarioID = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False, index=True)
    nombrePaciente = Column(String(70), nullable=False, index=True)
    apellidoPaciente = Column(String(70), nullable=False, index=True)
    cedula = Column(String(45), nullable=False, index=True)
    telefono = Column(Integer, nullable=False)
    fechaNacimiento = Column(Date, nullable=False)
    sexo = Column(String(30), nullable=False)
    usuario = relationship("Usuario", back_populates="pacientes")
