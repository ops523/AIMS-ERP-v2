from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from constants.status import MediaRollStatus

from models.media_roll import MediaRoll

from repositories.base_repository import BaseRepository


class MediaRollRepository(BaseRepository[MediaRoll]):

    model = MediaRoll

    # =========================================================
    # BASIC LOOKUPS
    # =========================================================

    @classmethod
    def get_by_roll_number(
        cls,
        db: Session,
        roll_number: str,
    ) -> Optional[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.roll_number == roll_number
            )
            .first()
        )

    @classmethod
    def get_by_asset_id(
        cls,
        db: Session,
        asset_id: str,
    ) -> Optional[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.asset_id == asset_id
            )
            .first()
        )

    @classmethod
    def get_by_qr_payload(
        cls,
        db: Session,
        payload: str,
    ) -> Optional[MediaRoll]:

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.qr_payload == payload
            )
            .first()
        )

    @classmethod
    def get_by_manufacturer_roll_no(
        cls,
        db: Session,
        manufacturer_roll_no: str,
    ) -> Optional[MediaRoll]:

        if not manufacturer_roll_no:
            return None

        manufacturer_roll_no = (
            manufacturer_roll_no.strip()
        )

        if not manufacturer_roll_no:
            return None

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.manufacturer_roll_no
                == manufacturer_roll_no,
                MediaRoll.is_active.is_(True),
            )
            .first()
        )

    # =========================================================
    # STATUS
    # =========================================================

    @classmethod
    def by_status(
        cls,
        db: Session,
        status: str,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.status == status,
                MediaRoll.is_active.is_(True),
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    @classmethod
    def available(
        cls,
        db: Session,
    ):

        return cls.by_status(
            db,
            MediaRollStatus.AVAILABLE,
        )

    @classmethod
    def available_for_allocation(
        cls,
        db: Session,
    ):
        """
        Return rolls that are physically usable for a new
        production allocation.

        AVAILABLE rolls are eligible.

        PARTIALLY_USED rolls are also eligible when they still
        contain physical balance.

        RESERVED / ALLOCATED / PRINTING rolls are excluded because
        they are already committed to production.
        """

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.is_active.is_(True),
                MediaRoll.available_sqft > 0,
                MediaRoll.status.in_(
                    [
                        MediaRollStatus.AVAILABLE,
                        MediaRollStatus.PARTIALLY_USED,
                    ]
                ),
            )
            .order_by(
                MediaRoll.created_at.asc()
            )
            .all()
        )

    # =========================================================
    # WAREHOUSE
    # =========================================================

    @classmethod
    def by_warehouse(
        cls,
        db: Session,
        warehouse_id: int,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.warehouse_id == warehouse_id,
                MediaRoll.is_active.is_(True),
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # =========================================================
    # SUPPLIER
    # =========================================================

    @classmethod
    def by_supplier(
        cls,
        db: Session,
        supplier_id: int,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.supplier_id == supplier_id,
                MediaRoll.is_active.is_(True),
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # =========================================================
    # MANUFACTURER
    # =========================================================

    @classmethod
    def by_manufacturer(
        cls,
        db: Session,
        manufacturer_id: int,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.manufacturer_id == manufacturer_id,
                MediaRoll.is_active.is_(True),
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # =========================================================
    # PRODUCT
    # =========================================================

    @classmethod
    def by_product(
        cls,
        db: Session,
        product_id: int,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.product_id == product_id,
                MediaRoll.is_active.is_(True),
            )
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # =========================================================
    # SEARCH
    # =========================================================

    @classmethod
    def search_keyword(
        cls,
        db: Session,
        keyword: str | None = None,
    ):

        query = db.query(MediaRoll).filter(
            MediaRoll.is_active.is_(True)
        )

        if keyword:

            keyword = keyword.strip()

            if keyword:

                pattern = f"%{keyword}%"

                query = query.filter(
                    or_(
                        MediaRoll.roll_number.ilike(
                            pattern
                        ),
                        MediaRoll.asset_id.ilike(
                            pattern
                        ),
                        MediaRoll.qr_payload.ilike(
                            pattern
                        ),
                        MediaRoll.manufacturer_roll_no.ilike(
                            pattern
                        ),
                        MediaRoll.purchase_order.ilike(
                            pattern
                        ),
                        MediaRoll.invoice_number.ilike(
                            pattern
                        ),
                    )
                )

        return (
            query
            .order_by(
                MediaRoll.created_at.desc()
            )
            .all()
        )

    # =========================================================
    # DASHBOARD
    # =========================================================

    @classmethod
    def dashboard_summary(
        cls,
        db: Session,
    ):

        rolls = (
            db.query(MediaRoll)
            .filter(
                MediaRoll.is_active.is_(True)
            )
            .all()
        )

        return {

            "total": len(rolls),

            "received": sum(
                r.status == MediaRollStatus.RECEIVED
                for r in rolls
            ),

            "available": sum(
                r.status == MediaRollStatus.AVAILABLE
                for r in rolls
            ),

            "reserved": sum(
                r.status == MediaRollStatus.RESERVED
                for r in rolls
            ),

            "allocated": sum(
                r.status == MediaRollStatus.ALLOCATED
                for r in rolls
            ),

            "printing": sum(
                r.status == MediaRollStatus.PRINTING
                for r in rolls
            ),

            "printed": sum(
                r.status == MediaRollStatus.PRINTED
                for r in rolls
            ),

            "partially_used": sum(
                r.status == MediaRollStatus.PARTIALLY_USED
                for r in rolls
            ),

            "consumed": sum(
                r.status == MediaRollStatus.CONSUMED
                for r in rolls
            ),

            "returned": sum(
                r.status == MediaRollStatus.RETURNED
                for r in rolls
            ),

            "damaged": sum(
                r.status == MediaRollStatus.DAMAGED
                for r in rolls
            ),

            "lost": sum(
                r.status == MediaRollStatus.LOST
                for r in rolls
            ),
        }