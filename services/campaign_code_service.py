from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.campaign import Campaign


class CampaignCodeService:

    PREFIX = "CMP"

    @staticmethod
    def generate(db: Session) -> str:

        year = datetime.now().year

        count = db.query(func.count(Campaign.id)).scalar() or 0

        number = count + 1

        return f"{CampaignCodeService.PREFIX}-{year}-{number:06d}"
