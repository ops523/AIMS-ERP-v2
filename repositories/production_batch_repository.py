from sqlalchemy.orm import Session

from models.production_batch import ProductionBatch


class ProductionBatchRepository:

    @staticmethod
    def create(
        db: Session,
        batch: ProductionBatch,
    ):
        db.add(batch)
        db.flush()
        return batch

    @staticmethod
    def get_all(
        db: Session,
    ):
        return (
            db.query(ProductionBatch)
            .order_by(
                ProductionBatch.id.desc()
            )
            .all()
        )

    @staticmethod
    def get(
        db: Session,
        batch_id: int,
    ):
        return (
            db.query(ProductionBatch)
            .filter(
                ProductionBatch.id == batch_id
            )
            .first()
        )
    
    @staticmethod
    def open_batches(db):

        return (

            db.query(ProductionBatch)

            .filter(
            ProductionBatch.status != "COMPLETED"
            )

        .all()

        )
