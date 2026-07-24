from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.base import Base


class ActivityLog(Base):

    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    module: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    reference: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    activity: Mapped[str] = mapped_column(
        String(300),
    )

    performed_by: Mapped[str] = mapped_column(
        String(150),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
