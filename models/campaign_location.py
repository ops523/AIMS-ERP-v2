from __future__ import annotations

from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.base import Base, TimestampMixin


class CampaignLocation(Base, TimestampMixin):

    __tablename__ = "campaign_locations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    campaign_version_id: Mapped[int] = mapped_column(
        ForeignKey(
            "campaign_versions.id",
            ondelete="CASCADE"
        ),
        index=True
    )

    state: Mapped[str] = mapped_column(
        String(100),
        index=True
    )

    district: Mapped[str] = mapped_column(
        String(100),
        index=True
    )

    town: Mapped[str] = mapped_column(
        String(150)
    )

    pincode: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    wall_width_ft: Mapped[float] = mapped_column(
        Float
    )

    wall_height_ft: Mapped[float] = mapped_column(
        Float
    )

    wall_sqft: Mapped[float] = mapped_column(
        Float
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    total_sqft: Mapped[float] = mapped_column(
        Float
    )

    wall_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    campaign_version = relationship(
        "CampaignVersion",
        back_populates="locations"
    )
