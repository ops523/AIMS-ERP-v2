from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, UUIDMixin


class Supplier(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    supplier_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True
    )

    supplier_name: Mapped[str] = mapped_column(
        String(200),
        index=True
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    mobile: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    gst_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    pincode: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
