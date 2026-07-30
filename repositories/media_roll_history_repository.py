from sqlalchemy.orm import Session

from models.media_roll_history import (
    MediaRollHistory,
)


class MediaRollHistoryRepository:

    @staticmethod
    def add(
        db: Session,
        history: MediaRollHistory,
    ):

        db.add(history)

        db.commit()

        db.refresh(history)

        return history

    @staticmethod
    def get_history(
        db: Session,
        media_roll_id: int,
    ):

        return (
            db.query(MediaRollHistory)
            .filter(
                MediaRollHistory.media_roll_id
                == media_roll_id
            )
            .order_by(
                MediaRollHistory.created_at
            )
            .all()
        )

    @staticmethod
    def latest(
        db: Session,
        media_roll_id: int,
    ):

        return (
            db.query(MediaRollHistory)
            .filter(
                MediaRollHistory.media_roll_id
                == media_roll_id
            )
            .order_by(
                MediaRollHistory.id.desc()
            )
            .first()
        )
