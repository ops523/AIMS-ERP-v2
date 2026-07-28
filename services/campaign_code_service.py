from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.campaign import Campaign


class CampaignCodeService:

    PREFIX = "CMP"

    @staticmethod
    def generate(db: Session):

        year = datetime.now().year

        count = (
            db.query(func.count(Campaign.id))
            .scalar()
            or 0
        )

        return f"CMP-{year}-{count + 1:06d}"
