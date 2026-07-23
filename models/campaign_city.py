from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class CampaignCity(Base, TimestampMixin):
    __tablename__ = "campaign_cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id")
    )

    state: Mapped[str] = mapped_column(String(100))

    district: Mapped[str] = mapped_column(String(100))

    city: Mapped[str] = mapped_column(String(100))

    pincode: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    planned_sqft: Mapped[float] = mapped_column()

    campaign = relationship("Campaign")
