from sqlalchemy.orm import Session

from models.media_roll import MediaRoll


class MediaRollRepository:

    @staticmethod
    def create(
        db: Session,
        media_roll: MediaRoll,
    ):

        db.add(media_roll)
        db.flush()
        db.refresh(media_roll)

        return media_roll

    @staticmethod
    def get_all(
        db: Session,
    ):

        return (

            db.query(MediaRoll)

            .order_by(
                MediaRoll.id.desc()
            )

            .all()

        )

    @staticmethod
    def get_by_id(
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
