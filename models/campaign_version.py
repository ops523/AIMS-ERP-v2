from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class CampaignVersion(Base, TimestampMixin):

    __tablename__ = "campaign_versions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE")
    )

    version_no: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    version_name: Mapped[str] = mapped_column(
        String(20),
        default="V1"
    )

    import_batch: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        index=True
    )

    total_locations: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    total_walls: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    total_sqft: Mapped[float] = mapped_column(
        default=0
    )

    campaign = relationship(
        "Campaign",
        back_populates="versions"
    )

    locations = relationship(
        "CampaignLocation",
        back_populates="campaign_version",
        cascade="all, delete-orphan"
    )

    artworks = relationship(
        "CampaignArtwork",
        back_populates="campaign_version",
        cascade="all, delete-orphan"
    )
