from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class Doctor(Base):
    __tablename__ = "doctor"
    __table_args__ = (
        UniqueConstraint("usuarioID", name="uq_doctor_usuarioID"),
    )
    idDoctor = Column(Integer, primary_key=True, index=True)
    usuarioID = Column(Integer, ForeignKey("usuario.idUsuario"), nullable=False, index=True)
    nombreDoctor = Column(String(45), nullable=False, index=True)
    apellidoDoctor = Column(String(45), nullable=False, index=True)
    tlfDoctor = Column(Integer, nullable=False)
    especialidad = Column(String(45), nullable=False, index=True)
    horario = Column(String(45))
    sexo = Column(String(30), nullable=False)
    usuario = relationship("Usuario", back_populates="doctores")
