from sqlalchemy.orm import Session

from models.media_roll import MediaRoll


class RollDetailsRepository:

    @staticmethod
    def get(
        db: Session,
        roll_id: int,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.id == roll_id
            )
            .first()
        )
