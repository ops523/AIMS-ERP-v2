from sqlalchemy.orm import Session

from models.campaign import Campaign
from models.campaign_version import CampaignVersion


class CampaignRepository:

    @staticmethod
    def create_campaign(db: Session, campaign: Campaign):

        db.add(campaign)
        db.flush()

        return campaign

    @staticmethod
    def create_version(db: Session, version: CampaignVersion):

        db.add(version)
        db.flush()

        return version

    @staticmethod
    def get_all(db: Session):

        return (
            db.query(Campaign)
            .order_by(Campaign.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, campaign_id: int):

        return (
            db.query(Campaign)
            .filter(Campaign.id == campaign_id)
            .first()
        )
