from sqlalchemy.orm import Session

from models.media_roll import MediaRoll


class RollInventoryRepository:

    @staticmethod
    def get_all(
        db: Session,
    ):

        return (
            db.query(MediaRoll)
            .order_by(MediaRoll.id.desc())
            .all()
        )

    @staticmethod
    def available(
        db: Session,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.balance_sqft > 0
            )
            .order_by(MediaRoll.id.desc())
            .all()
        )

    @staticmethod
    def search(
        db: Session,
        keyword: str,
    ):

        return (
            db.query(MediaRoll)
            .filter(
                MediaRoll.roll_code.ilike(f"%{keyword}%")
            )
            .all()
        )
