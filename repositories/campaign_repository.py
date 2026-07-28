from sqlalchemy.orm import Session

from models.campaign import Campaign
from models.campaign_version import CampaignVersion
from models.campaign_artwork import CampaignArtwork
from models.campaign_location import CampaignLocation


class CampaignRepository:

    # ---------------------------------------------------
    # Campaign
    # ---------------------------------------------------

    @staticmethod
    def create_campaign(
        db: Session,
        campaign: Campaign,
    ) -> Campaign:

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        return campaign

    @staticmethod
    def get(
        db: Session,
        campaign_id: int,
    ):

        return (
            db.query(Campaign)
            .filter(Campaign.id == campaign_id)
            .first()
        )

    @staticmethod
    def get_all(db: Session):

        return (
            db.query(Campaign)
            .order_by(Campaign.created_at.desc())
            .all()
        )

    @staticmethod
    def update(db: Session):

        db.commit()

    @staticmethod
    def delete(
        db: Session,
        campaign: Campaign,
    ):

        db.delete(campaign)
        db.commit()

    # ---------------------------------------------------
    # Campaign Version
    # ---------------------------------------------------

    @staticmethod
    def create_version(
        db: Session,
        version: CampaignVersion,
    ) -> CampaignVersion:

        db.add(version)
        db.commit()
        db.refresh(version)

        return version

    # ---------------------------------------------------
    # Artwork
    # ---------------------------------------------------

    @staticmethod
    def create_artworks(
        db: Session,
        artworks: list[CampaignArtwork],
    ):

        db.add_all(artworks)
        db.commit()

    # ---------------------------------------------------
    # Locations
    # ---------------------------------------------------

    @staticmethod
    def create_locations(
        db: Session,
        locations: list[CampaignLocation],
    ):

        db.add_all(locations)
        db.commit()
