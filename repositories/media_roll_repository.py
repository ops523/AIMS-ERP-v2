from repositories.base_repository import BaseRepository
from models.media_roll import MediaRoll


class MediaRollRepository(BaseRepository[MediaRoll]):

    model = MediaRoll

    @classmethod
    def get_by_roll_number(
        cls,
        db,
        roll_number: str,
    ):

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
        db,
        asset_id: str,
    ):

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
        db,
        payload: str,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.qr_payload == payload
            )
            .first()
        )

    @classmethod
    def available(
        cls,
        db,
    ):

        from constants.status import MediaRollStatus

        return cls.search(
            db,
            MediaRoll.status == MediaRollStatus.AVAILABLE,
            MediaRoll.is_active.is_(True),
        )

    @classmethod
    def by_warehouse(
        cls,
        db,
        warehouse_id: int,
    ):

        return cls.search(
            db,
            MediaRoll.warehouse_id == warehouse_id,
            MediaRoll.is_active.is_(True),
        )

    @classmethod
    def by_supplier(
        cls,
        db,
        supplier_id: int,
    ):

        return cls.search(
            db,
            MediaRoll.supplier_id == supplier_id,
            MediaRoll.is_active.is_(True),
        )

    @classmethod
    def by_manufacturer(
        cls,
        db,
        manufacturer_id: int,
    ):

        return cls.search(
            db,
            MediaRoll.manufacturer_id == manufacturer_id,
            MediaRoll.is_active.is_(True),
        )

    @classmethod
    def dashboard_summary(
        cls,
        db,
    ):

        from constants.status import MediaRollStatus

        rolls = cls.list(db)

        return {

            "total": len(rolls),

            "available": len(
                [
                    r
                    for r in rolls
                    if r.status == MediaRollStatus.AVAILABLE
                ]
            ),

            "allocated": len(
                [
                    r
                    for r in rolls
                    if r.status == MediaRollStatus.ALLOCATED
                ]
            ),

            "printing": len(
                [
                    r
                    for r in rolls
                    if r.status == MediaRollStatus.PRINTING
                ]
            ),

            "printed": len(
                [
                    r
                    for r in rolls
                    if r.status == MediaRollStatus.PRINTED
                ]
            ),

            "consumed": len(
                [
                    r
                    for r in rolls
                    if r.status == MediaRollStatus.CONSUMED
                ]
            ),

        }
