from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class OperationalObservation(Base):
    __tablename__ = "operational_observations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    occupancy_ratio: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    queue_length: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    event_delay_minutes: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    vendor_delay_minutes: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    equipment_failure_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )