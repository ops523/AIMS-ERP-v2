from sqlalchemy.orm import Session

from models.campaign import Campaign
from models.campaign_version import CampaignVersion

from repositories.campaign_repository import CampaignRepository

from services.campaign_code_service import CampaignCodeService
from services.import_batch_service import ImportBatchService


class CampaignService:

    @staticmethod
    def create_campaign(
        db: Session,
        campaign: Campaign
    ):

        campaign.campaign_code = CampaignCodeService.generate(db)

        CampaignRepository.create_campaign(
            db,
            campaign
        )

        version = CampaignVersion(

            campaign_id=campaign.id,

            version_no=1,

            version_name="V1",

            import_batch=ImportBatchService.generate(db)

        )

        CampaignRepository.create_version(
            db,
            version
        )

        db.commit()

        db.refresh(campaign)
        db.refresh(version)

        return campaign, version
