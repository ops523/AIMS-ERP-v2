from __future__ import annotations

from sqlalchemy.orm import Session

from models.production_allocation import ProductionAllocation

from repositories.production_allocation_repository import (
    ProductionAllocationRepository,
)


class ProductionAllocationService:

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
        """
        Create a production allocation linking:

            ProductionBatch
                ↓
            ProductionItem
                ↓
            CampaignArtwork
                ↓
            MediaRoll

        The allocation quantity is initially treated as
        completely unprinted.
        """

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
        """
        ID-based allocation helper.

        Useful for service/API/UI layers where the related
        objects have already been validated and only IDs
        are available.
        """

        if allocated_sqft <= 0:
            raise ValueError(
                "Allocated quantity must be greater than zero."
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

    @staticmethod
    def update_printed_quantity(
        db: Session,
        allocation: ProductionAllocation,
        printed_sqft: float,
        wastage_sqft: float = 0,
    ) -> ProductionAllocation:
        """
        Update production against an allocation.

        printed_sqft + wastage_sqft cannot exceed
        allocated_sqft.
        """

        if printed_sqft < 0:
            raise ValueError(
                "Printed quantity cannot be negative."
            )

        if wastage_sqft < 0:
            raise ValueError(
                "Wastage quantity cannot be negative."
            )

        total_processed = (
            printed_sqft + wastage_sqft
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

    @staticmethod
    def get_batch_allocations(
        db: Session,
        batch_id: int,
    ):
        return ProductionAllocationRepository.get_by_batch(
            db,
            batch_id,
        )
