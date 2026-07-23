from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDMixin
from utils.enums import CampaignStatus, Priority


class Campaign(Base, UUIDMixin, TimestampMixin):

    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    campaign_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True
    )

    client_name: Mapped[str] = mapped_column(
        String(200),
        index=True
    )

    agency_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    brand_name: Mapped[str] = mapped_column(
        String(200)
    )

    campaign_name: Mapped[str] = mapped_column(
        String(250)
    )

    campaign_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    priority: Mapped[Priority] = mapped_column(
        Enum(Priority),
        default=Priority.MEDIUM
    )

    start_date: Mapped[date] = mapped_column(Date)

    end_date: Mapped[date] = mapped_column(Date)

    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus),
        default=CampaignStatus.PLANNING
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    versions = relationship(
        "CampaignVersion",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
