from sqlalchemy import func
from sqlalchemy.orm import Session

from models.client import Client


class ClientCodeService:

    PREFIX = "CLI"

    @staticmethod
    def generate(db: Session) -> str:

        count = db.query(
            func.count(Client.id)
        ).scalar() or 0

        return f"{ClientCodeService.PREFIX}-{count + 1:06d}"
