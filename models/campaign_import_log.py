from __future__ import annotations

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from datetime import datetime

from models.base import Base


class CampaignImportLog(Base):

    __tablename__ = "campaign_import_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    campaign_version_id: Mapped[int] = mapped_column(
        ForeignKey(
            "campaign_versions.id",
            ondelete="CASCADE"
        ),
        index=True
    )

    file_name: Mapped[str] = mapped_column(
        String(300)
    )

    imported_by: Mapped[str] = mapped_column(
        String(100)
    )

    total_rows: Mapped[int] = mapped_column(
        Integer
    )

    successful_rows: Mapped[int] = mapped_column(
        Integer
    )

    failed_rows: Mapped[int] = mapped_column(
        Integer
    )

    imported_on: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    campaign_version = relationship("CampaignVersion")
