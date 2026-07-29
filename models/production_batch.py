from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base
from models.base import TimestampMixin
from models.base import UUIDMixin


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
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PLANNED",
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------
    # Relationships
    # --------------------------------------------------

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

    allocations = relationship(
    "ProductionAllocation",
    back_populates="production_batch",
    cascade="all, delete-orphan",
    )

    @property
    def total_planned_sqft(self):

        return sum(
            item.planned_sqft
            for item in self.production_items
        )

    @property
    def total_printed_sqft(self):

        return sum(
            item.printed_sqft
            for item in self.production_items
        )

    @property
    def total_wastage_sqft(self):

        return sum(
            item.wastage_sqft
            for item in self.production_items
        )

    @property
    def completion_percentage(self):

        planned = self.total_planned_sqft

        if planned == 0:
            return 0

        return round(
            (self.total_printed_sqft / planned) * 100,
            2,
        )
