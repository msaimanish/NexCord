from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EventPerson(Base):
    __tablename__ = "event_people"

    id: Mapped[int] = mapped_column(primary_key=True)

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
    )

    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"),
        nullable=False,
    )

    assignment_role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    person: Mapped["Person"] = relationship(
        back_populates="event_assignments",
    )