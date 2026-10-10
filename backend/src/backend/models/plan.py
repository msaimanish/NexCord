from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    rationale: Mapped[str | None] = mapped_column(
        Text,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PROPOSED",
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    estimated_cost: Mapped[float | None]

    estimated_delay_minutes: Mapped[int | None]

    simulation_result: Mapped[dict | None] = mapped_column(
        JSON,
    )

    expected_state: Mapped[dict | None] = mapped_column(
        JSON,
    )

    approval_token_hash: Mapped[str | None] = mapped_column(
        String(128),
        unique=True,
    )

    approved_by_person_id: Mapped[int | None] = mapped_column(
        ForeignKey("people.id"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    actions: Mapped[list["PlanAction"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
    )