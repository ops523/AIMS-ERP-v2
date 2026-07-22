from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, UUIDMixin


class Manufacturer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    manufacturer_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True
    )

    manufacturer_name: Mapped[str] = mapped_column(
        String(200),
        unique=True
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    website: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
