from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.base import Base
from models.base import TimestampMixin


class SystemSetting(
    Base,
    TimestampMixin,
):

    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    setting_key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    setting_value: Mapped[str] = mapped_column(
        Text,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
