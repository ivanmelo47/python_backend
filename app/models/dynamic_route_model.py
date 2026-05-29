import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class DynamicRoute(Base):
    __tablename__ = "dynamic_routes"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(Integer, ForeignKey("dynamic_routes.id", ondelete="CASCADE"), nullable=True)
    path = Column(String(255), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    component_path = Column(String(255), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_id = Column(Integer, ForeignKey("icons.id", ondelete="SET NULL"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    icon_color_mode = Column(String(50), default="currentColor") # currentColor or original
    min_hierarchy = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    meta = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    parent = relationship("DynamicRoute", remote_side=[id], backref="children")
    icon = relationship("Icon")
    role = relationship("Role")
