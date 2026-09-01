from __future__ import annotations

from sqlalchemy.orm import Session

from models.production_batch import ProductionBatch
from models.production_item import ProductionItem

from services.production_allocation_service import (
    ProductionAllocationService,
)

from services.printing_session_service import (
    PrintingSessionService,
)

from services.inventory_transaction_service import (
    InventoryTransactionService,
)

from services.activity_log_service import (
    ActivityLogService,
)

from services.document_number_service import (
    DocumentNumberService,
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
        """
        Create a complete production batch atomically.

        Flow:

            Batch
              ↓
            Items
              ↓
            Allocations
              ↓
            Inventory Reservation
              ↓
            Printing Session
              ↓
            Activity Log
              ↓
            COMMIT

        If any operation fails, the transaction is rolled back.
        """

        try:

            # --------------------------------------------------
            # 1. Validate inputs
            # --------------------------------------------------

            if printer is None:
                raise ValueError(
                    "Printer is required."
                )

            if campaign_version is None:
                raise ValueError(
                    "Campaign version is required."
                )

            if not artworks:
                raise ValueError(
                    "At least one artwork is required."
                )

            if not roll_allocations:
                raise ValueError(
                    "At least one media roll allocation is required."
                )

            # --------------------------------------------------
            # 2. Create production batch
            # --------------------------------------------------

            batch = ProductionBatch(
                batch_number=DocumentNumberService.generate(
                    db,
                    "PRODUCTION_BATCH",
                ),
                printer_id=printer.id,
                status="PLANNED",
                remarks=remarks,
            )

            db.add(batch)
            db.flush()

            # --------------------------------------------------
            # 3. Create production items
            # --------------------------------------------------

            artwork_items = {}

            for artwork in artworks:

                if artwork is None:
                    raise ValueError(
                        "Invalid artwork supplied."
                    )

                planned_sqft = float(
                    artwork.artwork_sqft or 0
                )

                if planned_sqft <= 0:
                    raise ValueError(
                        (
                            "Artwork must have a "
                            "positive square-foot quantity."
                        )
                    )

                item = ProductionItem(
                    production_batch_id=batch.id,
                    campaign_artwork_id=artwork.id,
                    planned_sqft=planned_sqft,
                    printed_sqft=0,
                    wastage_sqft=0,
                    status="PENDING",
                )

                db.add(item)
                db.flush()

                artwork_items[artwork.id] = item

            # --------------------------------------------------
            # 4. Validate and create roll allocations
            # --------------------------------------------------

            created_allocations = []

            for allocation_data in roll_allocations:

                artwork_id = allocation_data.get(
                    "campaign_artwork_id"
                )

                if artwork_id is None:
                    raise ValueError(
                        (
                            "campaign_artwork_id is required "
                            "for every roll allocation."
                        )
                    )

                item = artwork_items.get(
                    artwork_id
                )

                if item is None:
                    raise ValueError(
                        (
                            "Roll allocation references "
                            "an artwork that is not part "
                            "of this production batch."
                        )
                    )

                media_roll = allocation_data.get(
                    "media_roll"
                )

                if media_roll is None:
                    raise ValueError(
                        (
                            "media_roll is required "
                            "for every allocation."
                        )
                    )

                allocated_sqft = float(
                    allocation_data.get(
                        "allocated_sqft",
                        0,
                    )
                )

                if allocated_sqft <= 0:
                    raise ValueError(
                        (
                            "Allocated square feet "
                            "must be greater than zero."
                        )
                    )

                allocation = (
                    ProductionAllocationService.allocate(
                        db=db,
                        batch=batch,
                        item=item,
                        artwork=item.campaign_artwork,
                        media_roll=media_roll,
                        allocated_sqft=allocated_sqft,
                        status="ALLOCATED",
                    )
                )

                created_allocations.append(
                    allocation
                )

            db.flush()

            # --------------------------------------------------
            # 5. Reserve media-roll inventory
            # --------------------------------------------------

            InventoryTransactionService.reserve_batch(
                db=db,
                batch=batch,
            )

            # --------------------------------------------------
            # 6. Create printing session
            # --------------------------------------------------

            PrintingSessionService.start_session(
                db=db,
                batch=batch,
                printer=printer,
            )

            # --------------------------------------------------
            # 7. Activity log
            # --------------------------------------------------

            ActivityLogService.batch_created(
                db=db,
                batch=batch,
            )

            # --------------------------------------------------
            # 8. Commit ONLY after everything succeeds
            # --------------------------------------------------

            db.commit()

            db.refresh(batch)

            return batch

        except Exception:

            db.rollback()

            raise
