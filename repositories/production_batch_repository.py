from sqlalchemy.orm import Session

from models.production_batch import ProductionBatch


class ProductionBatchRepository:

    @staticmethod
    def get_all(db: Session):

        return (
            db.query(ProductionBatch)
            .order_by(ProductionBatch.id.desc())
            .all()
        )

    @staticmethod
    def get_by_id(
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
    def get_by_batch_number(
        db: Session,
        batch_number: str,
    ):

        return (
            db.query(ProductionBatch)
            .filter(
                ProductionBatch.batch_number == batch_number
            )
            .first()
        )

    @staticmethod
    def add(
        db: Session,
        batch: ProductionBatch,
    ):

        db.add(batch)
        db.commit()
        db.refresh(batch)

        return batch

    @staticmethod
    def count(db: Session):

        return db.query(
            ProductionBatch
        ).count()
