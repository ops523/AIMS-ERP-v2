from __future__ import annotations

from sqlalchemy import String

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.master_base import MasterBase


class Client(MasterBase):

    __tablename__ = "clients"

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

    brands = relationship(
        "Brand",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Client {self.code} - {self.name}>"
