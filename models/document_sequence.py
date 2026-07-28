from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.base import Base


class DocumentSequence(Base):

    __tablename__ = "document_sequences"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    document_type: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
    )

    prefix: Mapped[str] = mapped_column(
        String(10),
    )

    last_number: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
