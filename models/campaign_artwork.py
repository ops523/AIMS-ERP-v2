from __future__ import annotations

from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.base import Base, TimestampMixin, UUIDMixin


class CampaignArtwork(Base, UUIDMixin, TimestampMixin):

    __tablename__ = "campaign_artworks"

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

    artwork_code: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        index=True
    )

    artwork_name: Mapped[str] = mapped_column(
        String(250)
    )

    file_name: Mapped[str] = mapped_column(
        String(300)
    )

    width_ft: Mapped[float] = mapped_column(
        Float
    )

    height_ft: Mapped[float] = mapped_column(
        Float
    )

    artwork_sqft: Mapped[float] = mapped_column(
        Float
    )

    assigned_walls: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    campaign_version = relationship(
        "CampaignVersion",
        back_populates="artworks"
    )
