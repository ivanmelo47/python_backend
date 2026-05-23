import uuid as uuid_lib
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid_lib.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Timestamps de la sesión
    logged_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    logged_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Hash del refresh token actual (SHA-256). NULL = sesión revocada.
    refresh_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Datos del cliente
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Coordenadas geográficas (opcionales, las enviará el frontend)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(11, 8), nullable=True)

    user = relationship("User", back_populates="sessions")
