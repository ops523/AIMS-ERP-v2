from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

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

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id"),
    )

    printer_id: Mapped[int] = mapped_column(
        ForeignKey("printers.id"),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="OPEN",
    )

    remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    campaign = relationship("Campaign")

    printer = relationship("Printer")
