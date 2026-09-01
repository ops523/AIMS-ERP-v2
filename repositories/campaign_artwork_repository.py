from sqlalchemy.orm import Session

from models.campaign_artwork import CampaignArtwork


class CampaignArtworkRepository:

    @staticmethod
    def get_by_version(
        db: Session,
        version_id: int,
    ):

        return (
            db.query(CampaignArtwork)
            .filter(
                CampaignArtwork.campaign_version_id
                == version_id
            )
            .order_by(
                CampaignArtwork.artwork_name
            )
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        artwork: CampaignArtwork,
    ):

        db.add(artwork)

        db.flush()

        return artwork