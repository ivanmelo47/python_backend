import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Icon(Base):
    __tablename__ = "icons"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, index=True, nullable=False)
    type = Column(String(50), default="svg") # svg, img
    file_path = Column(String(255), nullable=True)
    svg_content = Column(Text, nullable=True)
    viewBox = Column(String(50), nullable=True)
    color_mode = Column(String(50), default="currentColor") # currentColor, original
    category = Column(String(50), index=True, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    creator = relationship("User", backref="created_icons")
