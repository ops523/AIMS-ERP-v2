from models.production_batch import ProductionBatch

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

            batch_number=batch_number,

            campaign_id=campaign_id,

            printer_id=printer_id,

            remarks=remarks,

        )

        return ProductionBatchRepository.create(
            db,
            batch,
        )
