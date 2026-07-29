from __future__ import annotations

from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
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


class ProductionAllocation(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "production_allocations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    production_item_id: Mapped[int] = mapped_column(
        ForeignKey(
            "production_items.id"
        )
    )

    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey(
            "production_batches.id"
        )
    )

    media_roll_id: Mapped[int] = mapped_column(
        ForeignKey(
            "media_rolls.id"
        )
    )

    allocated_sqft: Mapped[float] = mapped_column(
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

    balance_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="ALLOCATED",
    )

    production_item = relationship(
        "ProductionItem",
        back_populates="allocations",
    )

    media_roll = relationship(
        "MediaRoll",
        back_populates="allocations",
    )

    production_batch = relationship(
    "ProductionBatch",
    back_populates="allocations",
    )

    campaign_artwork = relationship(
    "CampaignArtwork",
    )
