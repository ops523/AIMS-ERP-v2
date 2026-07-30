from sqlalchemy.orm import Session

from models.production_batch import ProductionBatch

from repositories.production_batch_repository import (
    ProductionBatchRepository,
)

from services.document_number_service import (
    DocumentNumberService,
)

from constants.production_batch import DRAFT


class ProductionBatchService:

    @staticmethod
    def create_batch(
        db: Session,
        printer_id: int,
        remarks: str = "",
    ):

        batch = ProductionBatch(

            batch_number=DocumentNumberService.generate(
                db,
                "PRODUCTION_BATCH",
            ),

            printer_id=printer_id,

            status=DRAFT,

            remarks=remarks,

        )

        return ProductionBatchRepository.add(
            db,
            batch,
        )
