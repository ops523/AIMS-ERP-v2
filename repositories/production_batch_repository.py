from sqlalchemy.orm import Session

from repositories.base_repository import BaseRepository

from models.production_batch import ProductionBatch


class ProductionBatchRepository(
    BaseRepository[ProductionBatch]
):

    model = ProductionBatch

    @classmethod
    def get_open_batches(
        cls,
        db: Session,
    ):

        return (
            db.query(cls.model)
            .filter(
                cls.model.status != "CLOSED"
            )
            .order_by(
                cls.model.created_at.desc()
            )
            .all()
        )

    @classmethod
    def get_by_batch_number(
        cls,
        db: Session,
        batch_number: str,
    ):

        return (
            db.query(cls.model)
            .filter(
                cls.model.batch_number
                == batch_number
            )
            .first()
        )
