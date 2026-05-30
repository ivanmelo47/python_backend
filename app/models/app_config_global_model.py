from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from app.db.base import Base

class AppConfigGlobal(Base):
    __tablename__ = "app_config_globals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme: Mapped[str] = mapped_column(String(50), default="dark")
    color_palette: Mapped[str] = mapped_column(String(100), default="default")
    app_scale: Mapped[int] = mapped_column(Integer, default=100)
    items_per_page: Mapped[int] = mapped_column(Integer, default=10)
    table_configs: Mapped[dict] = mapped_column(JSON, nullable=True)
    table_view_mode: Mapped[str] = mapped_column(String(50), default="list")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = relationship("User", backref=backref("config", uselist=False))
