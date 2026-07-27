from models.production_allocation import (
    ProductionAllocation,
)

from repositories.production_allocation_repository import (
    ProductionAllocationRepository,
)

from constants.production_allocation import (
    ALLOCATED,
)


class ProductionAllocationService:

    @staticmethod
    def allocate_roll(
        db,
        production_item,
        media_roll,
        sqft,
    ):

        allocation = ProductionAllocation(

            production_item_id=production_item.id,

            media_roll_id=media_roll.id,

            allocated_sqft=sqft,

            balance_sqft=sqft,

            status=ALLOCATED,

        )

        return ProductionAllocationRepository.create(
            db,
            allocation,
        )
