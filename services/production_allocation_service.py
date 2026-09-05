from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from constants.status import MediaRollStatus

from models.media_roll import MediaRoll
from models.production_allocation import ProductionAllocation

from repositories.production_allocation_repository import (
    ProductionAllocationRepository,
)


class ProductionAllocationService:

    # =========================================================
    # ALLOCATION VALIDATION
    # =========================================================

    @staticmethod
    def validate_roll_allocation(
        db: Session,
        media_roll: MediaRoll,
        allocated_sqft: float,
        exclude_allocation_id: int | None = None,
    ) -> float:
        """
        Validate that a requested quantity can safely be
        allocated from a media roll.

        Returns the remaining allocatable balance after the
        requested quantity.

        Existing active production allocations are included
        in the calculation.
        """

        if media_roll is None:
            raise ValueError(
                "Media roll is required."
            )

        if allocated_sqft <= 0:
            raise ValueError(
                "Allocated quantity must be greater than zero."
            )

        if not media_roll.is_active:
            raise ValueError(
                f"Media roll {media_roll.roll_number} is inactive."
            )

        if media_roll.status not in (
            MediaRollStatus.AVAILABLE,
            MediaRollStatus.PARTIALLY_USED,
        ):
            raise ValueError(
                (
                    f"Media roll {media_roll.roll_number} "
                    f"is not available for allocation."
                )
            )

        physical_balance = float(
            media_roll.available_sqft or 0.0
        )

        active_statuses = {
            "ALLOCATED",
            "RESERVED",
            "PARTIALLY_PRINTED",
            "PRINTING",
        }

        allocations = (
            db.query(ProductionAllocation)
            .filter(
                ProductionAllocation.media_roll_id
                == media_roll.id,
                ProductionAllocation.status.in_(
                    active_statuses
                ),
            )
            .all()
        )

        already_reserved = 0.0

        for allocation in allocations:

            if (
                exclude_allocation_id is not None
                and allocation.id
                == exclude_allocation_id
            ):
                continue

            already_reserved += float(
                allocation.allocated_sqft or 0.0
            )

        remaining = (
            physical_balance
            - already_reserved
            - allocated_sqft
        )

        if remaining < -0.0001:

            usable = max(
                physical_balance
                - already_reserved,
                0.0,
            )

            raise ValueError(
                (
                    f"Insufficient available quantity on "
                    f"roll {media_roll.roll_number}. "
                    f"Available for allocation: "
                    f"{usable:,.2f} Sq Ft; "
                    f"requested: {allocated_sqft:,.2f} Sq Ft."
                )
            )

        return max(
            remaining,
            0.0,
        )

    # =========================================================
    # CREATE ALLOCATION
    # =========================================================

    @staticmethod
    def allocate(
        db: Session,
        batch,
        item,
        artwork,
        media_roll,
        allocated_sqft: float,
        status: str = "ALLOCATED",
    ) -> ProductionAllocation:

        if allocated_sqft <= 0:
            raise ValueError(
                "Allocated quantity must be greater than zero."
            )

        if batch is None:
            raise ValueError(
                "Production batch is required."
            )

        if item is None:
            raise ValueError(
                "Production item is required."
            )

        if artwork is None:
            raise ValueError(
                "Campaign artwork is required."
            )

        if media_roll is None:
            raise ValueError(
                "Media roll is required."
            )

        ProductionAllocationService.validate_roll_allocation(
            db=db,
            media_roll=media_roll,
            allocated_sqft=allocated_sqft,
        )

        allocation = ProductionAllocation(
            production_batch_id=batch.id,
            production_item_id=item.id,
            campaign_artwork_id=artwork.id,
            media_roll_id=media_roll.id,
            allocated_sqft=allocated_sqft,
            printed_sqft=0,
            wastage_sqft=0,
            balance_sqft=allocated_sqft,
            status=status,
        )

        return ProductionAllocationRepository.create(
            db,
            allocation,
        )

    # =========================================================
    # ID-BASED ALLOCATION
    # =========================================================

    @staticmethod
    def allocate_from_ids(
        db: Session,
        batch_id: int,
        production_item_id: int,
        campaign_artwork_id: int,
        media_roll_id: int,
        allocated_sqft: float,
        status: str = "ALLOCATED",
    ) -> ProductionAllocation:

        if allocated_sqft <= 0:
            raise ValueError(
                "Allocated quantity must be greater than zero."
            )

        media_roll = (
            db.query(MediaRoll)
            .filter(
                MediaRoll.id == media_roll_id
            )
            .first()
        )

        if media_roll is None:
            raise ValueError(
                "Media roll not found."
            )

        ProductionAllocationService.validate_roll_allocation(
            db=db,
            media_roll=media_roll,
            allocated_sqft=allocated_sqft,
        )

        allocation = ProductionAllocation(
            production_batch_id=batch_id,
            production_item_id=production_item_id,
            campaign_artwork_id=campaign_artwork_id,
            media_roll_id=media_roll_id,
            allocated_sqft=allocated_sqft,
            printed_sqft=0,
            wastage_sqft=0,
            balance_sqft=allocated_sqft,
            status=status,
        )

        return ProductionAllocationRepository.create(
            db,
            allocation,
        )

    # =========================================================
    # UPDATE PRINTED QUANTITY
    # =========================================================

    @staticmethod
    def update_printed_quantity(
        db: Session,
        allocation: ProductionAllocation,
        printed_sqft: float,
        wastage_sqft: float = 0,
    ) -> ProductionAllocation:

        if printed_sqft < 0:
            raise ValueError(
                "Printed quantity cannot be negative."
            )

        if wastage_sqft < 0:
            raise ValueError(
                "Wastage quantity cannot be negative."
            )

        total_processed = (
            printed_sqft
            + wastage_sqft
        )

        if total_processed > allocation.allocated_sqft:
            raise ValueError(
                (
                    "Printed quantity plus wastage "
                    "cannot exceed allocated quantity."
                )
            )

        allocation.printed_sqft = printed_sqft
        allocation.wastage_sqft = wastage_sqft

        allocation.balance_sqft = max(
            allocation.allocated_sqft
            - printed_sqft
            - wastage_sqft,
            0,
        )

        if allocation.balance_sqft <= 0:

            allocation.status = "COMPLETED"

        elif printed_sqft > 0:

            allocation.status = "PARTIALLY_PRINTED"

        else:

            allocation.status = "ALLOCATED"

        db.flush()

        return allocation

    # =========================================================
    # BATCH ALLOCATIONS
    # =========================================================

    @staticmethod
    def get_batch_allocations(
        db: Session,
        batch_id: int,
    ):

        return ProductionAllocationRepository.get_by_batch(
            db,
            batch_id,
        )

    # =========================================================
    # BATCH ROLL SUMMARY
    # =========================================================

    @staticmethod
    def get_batch_roll_summary(
        db: Session,
        batch_id: int,
    ) -> dict[int, float]:

        allocations = (
            ProductionAllocationService.get_batch_allocations(
                db,
                batch_id,
            )
        )

        summary = defaultdict(float)

        for allocation in allocations:

            summary[
                allocation.media_roll_id
            ] += float(
                allocation.allocated_sqft or 0.0
            )

        return dict(summary)