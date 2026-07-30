from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.media_roll import MediaRoll


class MediaRollRepository:

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    @staticmethod
    def create(
        db: Session,
        media_roll: MediaRoll,
    ) -> MediaRoll:

        db.add(media_roll)

        db.commit()

        db.refresh(media_roll)

        return media_roll

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    @staticmethod
    def update(
        db: Session,
        media_roll: MediaRoll,
    ) -> MediaRoll:

        db.commit()

        db.refresh(media_roll)

        return media_roll

    # ---------------------------------------------------------
    # DELETE (Soft Delete)
    # ---------------------------------------------------------

    @staticmethod
    def deactivate(
        db: Session,
        media_roll: MediaRoll,
    ) -> MediaRoll:

        media_roll.is_active = False

        db.commit()

        db.refresh(media_roll)

        return media_roll

    # ---------------------------------------------------------
    # GET BY ID
    # ---------------------------------------------------------

    @staticmethod
    def get_by_id(
        db: Session,
        media_roll_id: int,
    ) -> Optional[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(MediaRoll.id == media_roll_id)
            .first()
        )

    # ---------------------------------------------------------
    # GET BY UUID
    # ---------------------------------------------------------

    @staticmethod
    def get_by_uuid(
        db: Session,
        uuid: str,
    ) -> Optional[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(MediaRoll.uuid == uuid)
            .first()
        )

    # ---------------------------------------------------------
    # GET BY ROLL NUMBER
    # ---------------------------------------------------------

    @staticmethod
    def get_by_roll_number(
        db: Session,
        roll_number: str,
    ) -> Optional[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(MediaRoll.roll_number == roll_number)
            .first()
        )

    # ---------------------------------------------------------
    # GET BY QR PAYLOAD
    # ---------------------------------------------------------

    @staticmethod
    def get_by_qr_payload(
        db: Session,
        payload: str,
    ) -> Optional[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(MediaRoll.qr_payload == payload)
            .first()
        )

    # ---------------------------------------------------------
    # LIST ALL
    # ---------------------------------------------------------

    @staticmethod
    def list_all(
        db: Session,
        active_only: bool = True,
    ) -> List[MediaRoll]:

        query = db.query(MediaRoll)

        if active_only:

            query = query.filter(
                MediaRoll.is_active.is_(True)
            )

        return (
            query
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    @staticmethod
    def search(
        db: Session,
        keyword: str,
    ) -> List[MediaRoll]:

        keyword = f"%{keyword}%"

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.roll_number.ilike(keyword)
                |
                MediaRoll.batch_number.ilike(keyword)
                |
                MediaRoll.qr_payload.ilike(keyword)
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # ---------------------------------------------------------
    # BY STATUS
    # ---------------------------------------------------------

    @staticmethod
    def by_status(
        db: Session,
        status: str,
    ) -> List[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.status == status
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # ---------------------------------------------------------
    # BY WAREHOUSE
    # ---------------------------------------------------------

    @staticmethod
    def by_warehouse(
        db: Session,
        warehouse_id: int,
    ) -> List[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.warehouse_id == warehouse_id
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # ---------------------------------------------------------
    # AVAILABLE
    # ---------------------------------------------------------

    @staticmethod
    def available(
        db: Session,
    ) -> List[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.status == "AVAILABLE",
                MediaRoll.is_active.is_(True),
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # ---------------------------------------------------------
    # COUNT
    # ---------------------------------------------------------

    @staticmethod
    def count(
        db: Session,
    ) -> int:

        return (
            db.query(
                func.count(MediaRoll.id)
            )
            .scalar()
            or 0
        )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    @staticmethod
    def summary(
        db: Session,
    ):

        total = (
            db.query(
                func.count(MediaRoll.id)
            )
            .scalar()
            or 0
        )

        available = (
            db.query(
                func.count(MediaRoll.id)
            )
            .filter(
                MediaRoll.status == "AVAILABLE"
            )
            .scalar()
            or 0
        )

        allocated = (
            db.query(
                func.count(MediaRoll.id)
            )
            .filter(
                MediaRoll.status == "ALLOCATED"
            )
            .scalar()
            or 0
        )

        consumed = (
            db.query(
                func.count(MediaRoll.id)
            )
            .filter(
                MediaRoll.status == "CONSUMED"
            )
            .scalar()
            or 0
        )

        return {

            "total": total,

            "available": available,

            "allocated": allocated,

            "consumed": consumed,

        }
