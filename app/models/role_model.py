from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_roles_slug"),
        UniqueConstraint("hierarchy", name="uq_roles_hierarchy"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False)
    hierarchy: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users = relationship("User", back_populates="role")
