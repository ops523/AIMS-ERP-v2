from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, UUIDMixin


class Printer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "printers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    printer_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True
    )

    printer_name: Mapped[str] = mapped_column(
        String(200),
        unique=True
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    mobile: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    print_capacity_day: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    night_shift_capacity: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
