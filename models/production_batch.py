from __future__ import annotations

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
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


class ProductionBatch(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "production_batches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    batch_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
    )

    printer_id: Mapped[int] = mapped_column(
        ForeignKey("printers.id"),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="DRAFT",
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ---------------------------------------
    # Relationships
    # ---------------------------------------

    printer = relationship(
        "Printer",
        back_populates="production_batches",
    )

    production_items = relationship(
        "ProductionItem",
        back_populates="production_batch",
        cascade="all, delete-orphan",
    )
    
    printing_sessions = relationship(
    "PrintingSession",
    back_populates="production_batch",
    cascade="all, delete-orphan",
    )
