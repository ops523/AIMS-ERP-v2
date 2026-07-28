from sqlalchemy.orm import Session

from models.production_batch import ProductionBatch
from models.production_item import ProductionItem
from models.production_allocation import ProductionAllocation

from services.printing_session_service import (
    PrintingSessionService,
)

from services.inventory_transaction_service import (
    InventoryTransactionService,
)

from services.activity_log_service import (
    ActivityLogService,
)


class ProductionBatchCreator:

    @staticmethod
    def create_batch(
        db: Session,
        printer,
        campaign_version,
        artworks,
        roll_allocations,
        remarks=None,
    ):

        batch = ProductionBatch(
            batch_number=None,          # generated later
            printer_id=printer.id,
            status="PLANNED",
            remarks=remarks,
        )

        db.add(batch)
        db.flush()

        production_items = []

        for artwork in artworks:

            item = ProductionItem(
                production_batch_id=batch.id,
                campaign_artwork_id=artwork.id,
                planned_sqft=artwork.artwork_sqft,
                printed_sqft=0,
                wastage_sqft=0,
                status="PENDING",
            )

            db.add(item)
            db.flush()

            production_items.append(item)

        db.flush()

        #
        # Roll Allocations
        #

        for allocation in roll_allocations:

            pa = ProductionAllocation(

                production_item_id=allocation["production_item_id"],

                media_roll_id=allocation["media_roll_id"],

                allocated_sqft=allocation["allocated_sqft"],

                consumed_sqft=0,

                wastage_sqft=0,

                status="RESERVED",
            )

            db.add(pa)

        db.flush()

        #
        # Create Printing Session
        #

        PrintingSessionService.start_session(
            db,
            batch=batch,
            printer=printer,
        )

        #
        # Inventory Reservation
        #

        InventoryTransactionService.reserve_batch(
            db=db,
            batch=batch,
        )

        #
        # Activity Log
        #

        ActivityLogService.batch_created(
            db=db,
            batch=batch,
        )

        db.commit()

        db.refresh(batch)

        return batch
