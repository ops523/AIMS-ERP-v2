from __future__ import annotations

from sqlalchemy import (
    Integer,
    Float,
    String,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.base import (
    Base,
    UUIDMixin,
    TimestampMixin,
)


class PrintingSession(
    Base,
    UUIDMixin,
    TimestampMixin,
):

    __tablename__ = "printing_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
        index=True,
    )

    printer_id: Mapped[int] = mapped_column(
        ForeignKey("printers.id"),
        index=True,
    )

    session_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    operator_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    shift: Mapped[str] = mapped_column(
        String(30),
        default="DAY",
    )

    planned_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    printed_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    wastage_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="IN_PROGRESS",
    )

    remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    production_batch = relationship(
        "ProductionBatch",
        back_populates="printing_sessions",
    )

    printer = relationship(
        "Printer",
    )
