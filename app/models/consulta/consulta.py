from sqlalchemy import Column, Integer, Text, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class Consulta(Base):
    __tablename__ = "consulta"
    __table_args__ = (
        UniqueConstraint("citaID", name="uq_consulta_citaID"),
    )
    idConsulta = Column(Integer, primary_key=True, index=True)
    valoracion = Column(Text, nullable=False)
    fechaConsulta = Column(Date, nullable=False)
    citaID = Column(Integer, ForeignKey("citamedica.idCita"), nullable=False, index=True)
    doctorID = Column(Integer, ForeignKey("doctor.idDoctor"), nullable=False, index=True)
    cita = relationship("CitaMedica")
    doctor = relationship("Doctor")
