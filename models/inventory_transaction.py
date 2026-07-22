from __future__ import annotations

from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from models.base import Base, TimestampMixin


class InventoryTransaction(Base, TimestampMixin):
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    media_roll_id: Mapped[int] = mapped_column(
        ForeignKey("media_rolls.id")
    )

    transaction_type: Mapped[str] = mapped_column(
        String(50)
    )

    quantity_sqft: Mapped[float] = mapped_column(
        Float
    )

    balance_sqft: Mapped[float] = mapped_column(
        Float
    )

    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    media_roll = relationship("MediaRoll")
