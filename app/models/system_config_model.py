from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)
    type = Column(String(50), default="string")
    description = Column(Text, nullable=True)
