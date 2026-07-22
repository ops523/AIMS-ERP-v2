from __future__ import annotations

from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from models.base import Base, TimestampMixin, UUIDMixin


class MediaRoll(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "media_rolls"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    asset_id: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True
    )

    roll_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id")
    )

    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("media_products.id")
    )

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id")
    )

    manufacturer_roll_no: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    purchase_order: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    invoice_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    invoice_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    ordered_length_m: Mapped[float] = mapped_column(
        Float
    )

    actual_length_m: Mapped[float] = mapped_column(
        Float
    )

    width_ft: Mapped[float] = mapped_column(
        Float
    )

    total_sqft: Mapped[float] = mapped_column(
        Float
    )

    available_sqft: Mapped[float] = mapped_column(
        Float
    )

    qr_code: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="AVAILABLE"
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    supplier = relationship("Supplier")
    manufacturer = relationship("Manufacturer")
    product = relationship("MediaProduct")
    warehouse = relationship("Warehouse")
