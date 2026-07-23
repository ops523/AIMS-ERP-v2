from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, UUIDMixin


class Campaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    campaign_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True
    )

    client_name: Mapped[str] = mapped_column(
        String(200),
        index=True
    )

    campaign_name: Mapped[str] = mapped_column(
        String(250)
    )

    brand_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    start_date: Mapped[date] = mapped_column(Date)

    end_date: Mapped[date] = mapped_column(Date)

    status: Mapped[str] = mapped_column(
        String(30),
        default="PLANNING"
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
