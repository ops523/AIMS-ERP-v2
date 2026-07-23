from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.campaign_version import CampaignVersion


class ImportBatchService:

    PREFIX = "IMP"

    @staticmethod
    def generate(db: Session):

        year = datetime.now().year

        count = (
            db.query(func.count(CampaignVersion.id))
            .scalar()
            or 0
        )

        return f"{ImportBatchService.PREFIX}-{year}-{count+1:06d}"
