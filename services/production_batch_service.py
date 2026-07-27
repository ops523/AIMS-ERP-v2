from database import SessionLocal

from models.production_batch import ProductionBatch

from repositories.production_batch_repository import (
    ProductionBatchRepository,
)

from constants.production_batch import DRAFT


class ProductionBatchService:

    @staticmethod
    def generate_batch_number():

        db = SessionLocal()

        try:

            count = (
                ProductionBatchRepository.count(db)
                + 1
            )

            return f"PB{count:06d}"

        finally:

            db.close()

    @staticmethod
    def create_batch(
        db,
        printer_id,
        remarks="",
    ):

        batch = ProductionBatch(

            batch_number=ProductionBatchService.generate_batch_number(),

            printer_id=printer_id,

            status=DRAFT,

            remarks=remarks,

        )

        return ProductionBatchRepository.add(
            db,
            batch,
        )
