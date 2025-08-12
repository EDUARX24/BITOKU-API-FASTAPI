from sqlalchemy import Column, Integer, String, Date
from app.db.base import Base

class App(Base):
    __tablename__ = "app"
    app_id = Column(Integer, primary_key=True, index=True)
    nombreapp = Column(String(45), nullable=False)
    fechaApp = Column(Date, nullable=False)
