from sqlalchemy.orm import Session

from repositories.base_repository import BaseRepository

from models.media_roll_history import MediaRollHistory


class MediaRollHistoryRepository(
    BaseRepository[MediaRollHistory]
):

    model = MediaRollHistory

    @classmethod
    def get_history(
        cls,
        db: Session,
        media_roll_id: int,
    ):

        return (
            db.query(cls.model)
            .filter(
                cls.model.media_roll_id
                == media_roll_id
            )
            .order_by(
                cls.model.created_at
            )
            .all()
        )

    @classmethod
    def latest(
        cls,
        db: Session,
        media_roll_id: int,
    ):

        return (
            db.query(cls.model)
            .filter(
                cls.model.media_roll_id
                == media_roll_id
            )
            .order_by(
                cls.model.id.desc()
            )
            .first()
        )
