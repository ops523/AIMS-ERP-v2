from __future__ import annotations

from sqlalchemy import Boolean
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base
from models.base import TimestampMixin
from models.base import UUIDMixin


class Printer(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "printers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    printer_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
    )

    printer_name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    mobile: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    print_capacity_day: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    night_shift_capacity: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    # ----------------------------------------------------
    # Relationships
    # ----------------------------------------------------

    production_batches = relationship(
        "ProductionBatch",
        back_populates="printer",
        cascade="all, save-update",
    )

    user = relationship(
        "User",
        back_populates="printer",
        uselist=False,
    )

    # Keep this commented until ProductionRoll is created.
    # production_rolls = relationship(
    #     "ProductionRoll",
    #     back_populates="printer",
    #     cascade="all, save-update",
    # )
