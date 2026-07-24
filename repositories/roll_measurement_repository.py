from sqlalchemy.orm import Session

from models.roll_measurement import RollMeasurement


class RollMeasurementRepository:

    @staticmethod
    def create(
        db: Session,
        measurement: RollMeasurement,
    ):

        db.add(measurement)
        db.commit()
        db.refresh(measurement)

        return measurement

    @staticmethod
    def get_by_roll(
        db: Session,
        roll_id: int,
    ):

        return (
            db.query(RollMeasurement)
            .filter(
                RollMeasurement.media_roll_id == roll_id
            )
            .order_by(
                RollMeasurement.measured_at.desc()
            )
            .all()
        )

    @staticmethod
    def latest(
        db: Session,
        roll_id: int,
    ):

        return (
            db.query(RollMeasurement)
            .filter(
                RollMeasurement.media_roll_id == roll_id
            )
            .order_by(
                RollMeasurement.measured_at.desc()
            )
            .first()
        )
