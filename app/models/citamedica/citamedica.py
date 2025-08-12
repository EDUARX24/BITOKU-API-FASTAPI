from sqlalchemy import Column, Integer, Date, String, SmallInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class CitaMedica(Base):
    __tablename__ = "citamedica"
    idCita = Column(Integer, primary_key=True, index=True)
    pacienteID = Column(Integer, ForeignKey("paciente.idPaciente"))
    fechaCita = Column(Date, nullable=False)
    hora = Column(String(50), nullable=False)
    estado = Column(SmallInteger, nullable=False)
    motivocancalacion = Column(Text)
    paciente = relationship("Paciente")
