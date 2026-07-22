"""
Measurement calculations used throughout AIMS.
"""

from __future__ import annotations


METER_TO_FEET = 3.28084


class MeasurementService:

    @staticmethod
    def sqft_from_roll(
        length_m: float,
        width_ft: float
    ) -> float:

        return round(
            length_m * METER_TO_FEET * width_ft,
            2
        )

    @staticmethod
    def printable_sqft(
        total_sqft: float,
        reserve_percent: float = 0
    ) -> float:

        return round(

            total_sqft *

            ((100 - reserve_percent) / 100),

            2

        )

    @staticmethod
    def utilization(
        printed: float,
        received: float
    ) -> float:

        if received == 0:

            return 0

        return round(

            printed / received * 100,

            2

        )

    @staticmethod
    def wastage_percent(
        waste: float,
        received: float
    ) -> float:

        if received == 0:

            return 0

        return round(

            waste / received * 100,

            2

        )
