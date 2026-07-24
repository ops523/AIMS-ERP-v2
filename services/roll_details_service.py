from repositories.roll_details_repository import (
    RollDetailsRepository,
)


class RollDetailsService:

    @staticmethod
    def get(
        db,
        roll_id,
    ):

        return RollDetailsRepository.get(
            db,
            roll_id,
        )
