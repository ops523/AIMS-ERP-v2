from models.production_batch import ProductionBatch
from repositories.production_batch_repository import (
    ProductionBatchRepository,
)
from utils.number_generator import NumberGenerator


class ProductionBatchService:

    @staticmethod
    def create(
        db,
        printer_id,
        remarks=None,
    ):

        batch = ProductionBatch(

            batch_number=NumberGenerator.production_batch_number(db),

            printer_id=printer_id,

            remarks=remarks,

        )

        return ProductionBatchRepository.create(
            db=db,
            batch=batch,
        )
