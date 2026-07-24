from repositories.roll_inventory_repository import (
    RollInventoryRepository,
)


class RollInventoryService:

    @staticmethod
    def all(db):

        return RollInventoryRepository.get_all(db)

    @staticmethod
    def available(db):

        return RollInventoryRepository.available(db)

    @staticmethod
    def search(
        db,
        keyword,
    ):

        if not keyword:

            return RollInventoryRepository.get_all(db)

        return RollInventoryRepository.search(
            db,
            keyword,
        )
