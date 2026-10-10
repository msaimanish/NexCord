from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PlanAction(Base):
    __tablename__ = "plan_actions"

    id: Mapped[int] = mapped_column(primary_key=True)

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("plans.id"),
        nullable=False,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    parameters: Mapped[dict | None] = mapped_column(
        JSON,
    )

    expected_result: Mapped[dict | None] = mapped_column(
        JSON,
    )

    compensation: Mapped[dict | None] = mapped_column(
        JSON,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    plan: Mapped["Plan"] = relationship(
        back_populates="actions",
    )