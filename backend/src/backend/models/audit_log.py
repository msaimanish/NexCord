from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    actor_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    actor_id: Mapped[int | None] = mapped_column(
        Integer,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entity_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    before_state: Mapped[dict | None] = mapped_column(
        JSON,
    )

    after_state: Mapped[dict | None] = mapped_column(
        JSON,
    )

    extra_data: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )