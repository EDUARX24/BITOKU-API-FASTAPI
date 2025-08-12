from sqlalchemy import Column, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Consulta(Base):
    __tablename__ = "consulta"
    idConsulta = Column(Integer, primary_key=True, index=True)
    valoracion = Column(Text, nullable=False)
    fechaConsulta = Column(Date, nullable=False)
    citaID = Column(Integer, ForeignKey("citamedica.idCita"))
    doctorID = Column(Integer, ForeignKey("doctor.idDoctor"))
    cita = relationship("CitaMedica")
    doctor = relationship("Doctor")
