from models.roll_measurement import RollMeasurement
from repositories.roll_measurement_repository import (
    RollMeasurementRepository,
)


class RollMeasurementService:

    @staticmethod
    def calculate_sqft(
        length_ft: float,
        width_ft: float,
    ) -> float:

        return round(length_ft * width_ft, 2)

    @staticmethod
    def create_measurement(
        db,
        media_roll_id: int,
        measured_length_ft: float,
        measured_width_ft: float,
        measured_by: str,
        remarks: str | None = None,
    ):

        sqft = RollMeasurementService.calculate_sqft(
            measured_length_ft,
            measured_width_ft,
        )

        measurement = RollMeasurement(
            media_roll_id=media_roll_id,
            measured_length_ft=measured_length_ft,
            measured_width_ft=measured_width_ft,
            actual_sqft=sqft,
            measured_by=measured_by,
            remarks=remarks,
        )

        return RollMeasurementRepository.create(
            db,
            measurement,
        )
