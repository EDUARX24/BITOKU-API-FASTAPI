from sqlalchemy import Column, Integer, Date, String, SmallInteger, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class CitaMedica(Base):
    __tablename__ = "citamedica"
    __table_args__ = (
        UniqueConstraint("pacienteID", "fechaCita", name="uq_citamedica_paciente_fecha"),
    )
    idCita = Column(Integer, primary_key=True, index=True)
    pacienteID = Column(Integer, ForeignKey("paciente.idPaciente"), nullable=False, index=True)
    fechaCita = Column(Date, nullable=False, index=True)
    hora = Column(String(50), nullable=False)
    estado = Column(SmallInteger, nullable=False)
    motivocancalacion = Column(Text)
    paciente = relationship("Paciente")
