from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from models.base import Base, TimestampMixin, UUIDMixin


class MediaProduct(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "media_products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    product_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True
    )

    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id")
    )

    product_name: Mapped[str] = mapped_column(
        String(200)
    )

    width_ft: Mapped[float] = mapped_column(
        Float
    )

    gsm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    finish: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    standard_length_m: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    manufacturer = relationship(
        "Manufacturer"
    )
