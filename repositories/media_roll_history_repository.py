from __future__ import annotations

from sqlalchemy.orm import Session

from models.media_roll_history import MediaRollHistory
from repositories.base_repository import BaseRepository


class MediaRollHistoryRepository(
    BaseRepository[MediaRollHistory]
):

    model = MediaRollHistory

    # =========================================================
    # ADD EVENT
    # =========================================================

    @classmethod
    def add_event(
        cls,
        db: Session,
        media_roll_id: int,
        event: str,
        previous_status: str | None = None,
        current_status: str | None = None,
        location: str | None = None,
        reference_type: str | None = None,
        reference_number: str | None = None,
        remarks: str | None = None,
        scanned_by: str | None = None,
    ) -> MediaRollHistory:

        history = MediaRollHistory(

            media_roll_id=media_roll_id,

            event=event,

            previous_status=previous_status,

            current_status=current_status,

            location=location,

            reference_type=reference_type,

            reference_number=reference_number,

            remarks=remarks,

            scanned_by=scanned_by,
        )

        db.add(history)

        db.flush()

        return history

    # =========================================================
    # HISTORY
    # =========================================================

    @classmethod
    def get_history(
        cls,
        db: Session,
        media_roll_id: int,
    ):

        return (
            db.query(cls.model)
            .filter(
                cls.model.media_roll_id == media_roll_id
            )
            .order_by(
                cls.model.created_at.asc()
            )
            .all()
        )

    # =========================================================
    # LATEST
    # =========================================================

    @classmethod
    def latest(
        cls,
        db: Session,
        media_roll_id: int,
    ):

        return (
            db.query(cls.model)
            .filter(
                cls.model.media_roll_id == media_roll_id
            )
            .order_by(
                cls.model.id.desc()
            )
            .first()
        )
