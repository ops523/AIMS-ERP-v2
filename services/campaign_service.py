from sqlalchemy.orm import Session

from models.campaign import Campaign
from models.campaign_version import CampaignVersion
from models.campaign_artwork import CampaignArtwork
from models.campaign_location import CampaignLocation

from repositories.campaign_repository import CampaignRepository

from services.campaign_code_service import CampaignCodeService
from services.activity_log_service import ActivityLogService


class CampaignService:

    @staticmethod
    def create_campaign(
        db: Session,
        campaign: Campaign,
        version: CampaignVersion,
        artworks: list[CampaignArtwork],
        locations: list[CampaignLocation],
    ):

        try:

            # ---------------------------------------
            # Generate Campaign Code
            # ---------------------------------------

            campaign.campaign_code = CampaignCodeService.generate(db)

            db.add(campaign)
            db.flush()

            # ---------------------------------------
            # Campaign Version
            # ---------------------------------------

            version.campaign_id = campaign.id

            db.add(version)
            db.flush()

            # ---------------------------------------
            # Artworks
            # ---------------------------------------

            for artwork in artworks:

                artwork.campaign_version_id = version.id

            db.add_all(artworks)

            # ---------------------------------------
            # Locations
            # ---------------------------------------

            for location in locations:

                location.campaign_version_id = version.id

            db.add_all(locations)

            # ---------------------------------------
            # Activity Log
            # ---------------------------------------

            ActivityLogService.log(
                db=db,
                module="Campaign",
                reference=campaign.campaign_code,
                activity="Campaign Created",
                performed_by="Admin",
            )

            # ---------------------------------------
            # Commit Once
            # ---------------------------------------

            db.commit()

            db.refresh(campaign)
            db.refresh(version)

            return campaign, version

        except Exception:

            db.rollback()

            raise
