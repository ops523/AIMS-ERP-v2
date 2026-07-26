from models.production_batch import ProductionBatch
from utils.number_generator import NumberGenerator

from repositories.production_batch_repository import (
    ProductionBatchRepository,
)


class ProductionBatchService:

    @staticmethod
    def create(
        db,
        batch_number,
        campaign_id,
        printer_id,
        remarks=None,
    ):

        batch = ProductionBatch(

            batch_number=NumberGenerator.production_batch_number(db),

            campaign_id=campaign_id,

            printer_id=printer_id,

            remarks=remarks,

        )

        return ProductionBatchRepository.create(
            db,
            batch,
        )
