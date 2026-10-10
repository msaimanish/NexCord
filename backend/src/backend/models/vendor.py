from __future__ import annotations

from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    vendor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    contact_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ACTIVE",
    )

    event_assignments: Mapped[list["EventVendor"]] = relationship(
        back_populates="vendor",
        cascade="all, delete-orphan",
    )

    reliability_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )