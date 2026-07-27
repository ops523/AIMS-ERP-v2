from sqlalchemy.orm import Session

from models.production_allocation import (
    ProductionAllocation,
)


class ProductionAllocationRepository:

    @staticmethod
    def create(
        db: Session,
        allocation: ProductionAllocation,
    ):

        db.add(allocation)

        db.commit()

        db.refresh(allocation)

        return allocation

    @staticmethod
    def get_roll_allocations(
        db: Session,
        media_roll_id: int,
    ):

        return (
            db.query(
                ProductionAllocation
            )
            .filter(
                ProductionAllocation.media_roll_id
                == media_roll_id
            )
            .all()
        )

    @staticmethod
    def get_item_allocations(
        db: Session,
        production_item_id: int,
    ):

        return (
            db.query(
                ProductionAllocation
            )
            .filter(
                ProductionAllocation.production_item_id
                == production_item_id
            )
            .all()
        )
