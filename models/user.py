from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="Operator",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
