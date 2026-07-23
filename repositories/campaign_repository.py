from sqlalchemy.orm import Session
from models.campaign import Campaign
from models.campaign_version import CampaignVersion
from models.campaign_location import CampaignLocation

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
        @staticmethod
    def add_locations(
        db: Session,
        locations: list
    ):

        db.add_all(locations)

    @staticmethod
    def count_locations(
        db: Session,
        version_id: int
    ):

        return (

            db.query(CampaignLocation)

            .filter(

                CampaignLocation.campaign_version_id == version_id

            )

            .count()

        )    
