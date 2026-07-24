from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Integer,
    Float,
    String,
    ForeignKey,
    DateTime,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.base import Base, TimestampMixin


class InventoryTransaction(Base, TimestampMixin):

    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    media_roll_id: Mapped[int] = mapped_column(
        ForeignKey("media_rolls.id"),
        nullable=False,
        index=True,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    reference_module: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reference_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    campaign_id: Mapped[int | None] = mapped_column(
    ForeignKey("campaigns.id"),
    nullable=True,
    index=True,
    )

    printer_id: Mapped[int | None] = mapped_column(
    ForeignKey("printers.id"),
    nullable=True,
    index=True,
    )

    warehouse_id: Mapped[int | None] = mapped_column(
    ForeignKey("warehouses.id"),
    nullable=True,
    index=True,
    )

    qty_in: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    qty_out: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    balance_qty: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    performed_by: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    transaction_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    media_roll = relationship(
        "MediaRoll",
        back_populates="transactions",
    )
