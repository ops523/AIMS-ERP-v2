from __future__ import annotations

from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

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
        ForeignKey("production_items.id"),
        nullable=False,
        index=True,
    )

    campaign_artwork_id: Mapped[int] = mapped_column(
        ForeignKey("campaign_artworks.id"),
        nullable=False,
        index=True,
    )

    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
        nullable=False,
        index=True,
    )

    media_roll_id: Mapped[int] = mapped_column(
        ForeignKey("media_rolls.id"),
        nullable=False,
        index=True,
    )

    allocated_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    printed_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    wastage_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    balance_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="ALLOCATED",
        nullable=False,
        index=True,
    )

    # --------------------------------------------------
    # Relationships
    # --------------------------------------------------

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
        back_populates="allocations",
    )

    # --------------------------------------------------
    # Calculated helpers
    # --------------------------------------------------

    @property
    def consumed_sqft(self) -> float:
        """
        Backward-compatible alias.

        Older code may refer to consumed_sqft.
        The actual quantity printed/consumed against
        the allocation is represented by printed_sqft.
        """
        return self.printed_sqft

    @property
    def completion_percentage(self) -> float:
        if self.allocated_sqft <= 0:
            return 0.0

        return round(
            (self.printed_sqft / self.allocated_sqft) * 100,
            2,
        )
