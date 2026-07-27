from sqlalchemy.orm import Session

from models.campaign_version import CampaignVersion


class CampaignVersionRepository:

    @staticmethod
    def get_by_campaign(
        db: Session,
        campaign_id: int,
    ):

        return (
            db.query(CampaignVersion)
            .filter(
                CampaignVersion.campaign_id == campaign_id
            )
            .order_by(CampaignVersion.id.desc())
            .all()
        )
