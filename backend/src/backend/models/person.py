from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
    )

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    event_assignments: Mapped[list["EventPerson"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )