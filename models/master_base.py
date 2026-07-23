from __future__ import annotations

from sqlalchemy import (
    Integer,
    String,
    Boolean,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.base import Base, TimestampMixin


class MasterBase(Base, TimestampMixin):
    """
    Abstract base class for all master tables.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
