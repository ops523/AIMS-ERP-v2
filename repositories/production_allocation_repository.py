from sqlalchemy.orm import Session

from models.production_allocation import ProductionAllocation


class ProductionAllocationRepository:

    @staticmethod
    def create(db: Session, allocation: ProductionAllocation):

        db.add(allocation)
        db.flush()

        return allocation

    @staticmethod
    def get_by_batch(db: Session, batch_id: int):

        return (
            db.query(ProductionAllocation)
            .filter(
                ProductionAllocation.production_batch_id == batch_id
            )
            .all()
        )

    @staticmethod
    def delete(db: Session, allocation):

        db.delete(allocation)
