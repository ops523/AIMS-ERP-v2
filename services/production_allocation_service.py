from sqlalchemy.orm import Session

from models.production_allocation import ProductionAllocation

from repositories.production_allocation_repository import (
    ProductionAllocationRepository,
)


class ProductionAllocationService:

    @staticmethod
    def allocate(
        db: Session,
        batch,
        artwork,
        required_sqft,
    ):

        allocation = ProductionAllocation(

            production_batch_id=batch.id,

            campaign_artwork_id=artwork.id,

            allocated_sqft=required_sqft,

            printed_sqft=0,

            status="ALLOCATED",
        )

        ProductionAllocationRepository.create(
            db,
            allocation,
        )

        return allocation
