from sqlalchemy import Column, Integer, String, Date
from app.db.base import Base

class Apf(Base):
    __tablename__ = "apf"
    apf_id = Column(Integer, primary_key=True, index=True)
    nombreapf = Column(String(45), nullable=False)
    fechaApf = Column(Date, nullable=False)
