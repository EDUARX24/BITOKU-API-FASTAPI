from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from app.db.base import Base

class Expediente(Base):
    __tablename__ = "expediente"
    idExpediente = Column(Integer, primary_key=True, index=True)
    pacienteID = Column(Integer, ForeignKey("paciente.idPaciente"))
    doctorid = Column(Integer, ForeignKey("doctor.idDoctor"))
    id_app = Column(Integer, ForeignKey("app.app_id"))
    id_apf = Column(Integer, ForeignKey("apf.apf_id"))
    alimentacion = Column(String(60), nullable=False)
    horaSueño = Column(Text, nullable=False)
    actividadFisica = Column(Integer, nullable=False)
    descpAcFisica = Column(Text, nullable=False)
    alcohol = Column(Integer, nullable=False)
    descpAlcohol = Column(Text, nullable=False)
    fumar = Column(Integer, nullable=False)
    descpFumar = Column(Text, nullable=False)
    medicamento = Column(Integer, nullable=False)
    descpMedicamento = Column(Text, nullable=False)
    fechaExpediente = Column(Date, nullable=False)
    motivoConsulta = Column(Text, nullable=False)
    diagnostico = Column(Text, nullable=False)
