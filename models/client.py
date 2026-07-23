from __future__ import annotations

from sqlalchemy import (
    String,
    Boolean,
    Integer,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.base import Base
from models.mixins import TimestampMixin


class Client(Base, TimestampMixin):

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    client_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
    )

    client_name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
    )

    gst_number: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    brands = relationship(
        "Brand",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    def __repr__(self):

        return f"<Client {self.client_code} - {self.client_name}>"
