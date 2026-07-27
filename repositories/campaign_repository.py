from sqlalchemy.orm import Session

from models.campaign import Campaign


class CampaignRepository:

    @staticmethod
    def get_all(db: Session):

        return (
            db.query(Campaign)
            .filter(Campaign.is_active == True)
            .order_by(Campaign.campaign_name)
            .all()
        )
