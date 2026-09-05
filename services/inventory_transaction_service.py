from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from constants.inventory import InventoryTransactionType
from constants.modules import Module
from constants.status import MediaRollStatus

from models.inventory_transaction import InventoryTransaction
from models.media_roll import MediaRoll
from models.production_allocation import ProductionAllocation

from repositories.inventory_transaction_repository import (
    InventoryTransactionRepository,
)


class InventoryTransactionService:

    # =========================================================
    # GENERIC POST
    # =========================================================

    @staticmethod
    def post_transaction(
        db: Session,
        media_roll_id: int,
        transaction_type: str,
        reference_module: str,
        qty_in: float = 0,
        qty_out: float = 0,
        reference_id: int | None = None,
        campaign_id: int | None = None,
        printer_id: int | None = None,
        warehouse_id: int | None = None,
        unit_cost: float = 0,
        total_cost: float = 0,
        wastage_sqft: float = 0,
        remarks: str | None = None,
        user: str | None = None,
    ):

        if qty_in < 0:
            raise ValueError(
                "qty_in cannot be negative."
            )

        if qty_out < 0:
            raise ValueError(
                "qty_out cannot be negative."
            )

        if qty_in > 0 and qty_out > 0:
            raise ValueError(
                (
                    "A transaction cannot have both "
                    "qty_in and qty_out."
                )
            )

        current_balance = (
            InventoryTransactionRepository.latest_balance(
                db=db,
                media_roll_id=media_roll_id,
            )
        )

        new_balance = (
            current_balance
            + qty_in
            - qty_out
        )

        if new_balance < 0:
            raise ValueError(
                (
                    "Insufficient inventory. "
                    f"Current balance: {current_balance:.2f}, "
                    f"Requested out: {qty_out:.2f}"
                )
            )

        transaction = InventoryTransaction(
            media_roll_id=media_roll_id,
            transaction_type=transaction_type,
            reference_module=reference_module,
            reference_id=reference_id,
            campaign_id=campaign_id,
            printer_id=printer_id,
            warehouse_id=warehouse_id,
            qty_in=qty_in,
            qty_out=qty_out,
            balance_qty=new_balance,
            unit_cost=unit_cost,
            total_cost=total_cost,
            wastage_sqft=wastage_sqft,
            remarks=remarks,
            performed_by=user,
        )

        return (
            InventoryTransactionRepository.create(
                db=db,
                transaction=transaction,
            )
        )

    # =========================================================
    # RECEIVE MEDIA ROLL
    # =========================================================

    @staticmethod
    def receive_roll(
        db: Session,
        media_roll_id: int,
        warehouse_id: int,
        qty: float,
        user: str | None = None,
        remarks: str = "Media Roll Received",
    ):

        if qty <= 0:
            raise ValueError(
                "Receipt quantity must be greater than zero."
            )

        return (
            InventoryTransactionService.post_transaction(
                db=db,
                media_roll_id=media_roll_id,
                transaction_type=(
                    InventoryTransactionType.RECEIPT
                ),
                reference_module=Module.MEDIA_ROLL,
                warehouse_id=warehouse_id,
                qty_in=qty,
                remarks=remarks,
                user=user,
            )
        )

    # =========================================================
    # CONSUME MEDIA ROLL
    # =========================================================

    @staticmethod
    def consume_roll(
        db: Session,
        media_roll_id: int,
        warehouse_id: int,
        qty: float,
        campaign_id: int | None = None,
        printer_id: int | None = None,
        wastage: float = 0,
        unit_cost: float = 0,
        total_cost: float = 0,
        remarks: str = "Roll Consumed",
        user: str | None = None,
    ):

        if qty <= 0:
            raise ValueError(
                "Consumption quantity must be greater than zero."
            )

        return (
            InventoryTransactionService.post_transaction(
                db=db,
                media_roll_id=media_roll_id,
                transaction_type=(
                    InventoryTransactionType.CONSUMPTION
                ),
                reference_module=Module.PRODUCTION,
                campaign_id=campaign_id,
                printer_id=printer_id,
                warehouse_id=warehouse_id,
                qty_out=qty,
                wastage_sqft=wastage,
                unit_cost=unit_cost,
                total_cost=total_cost,
                remarks=remarks,
                user=user,
            )
        )

    # =========================================================
    # ADJUST STOCK
    # =========================================================

    @staticmethod
    def adjust_stock(
        db: Session,
        media_roll_id: int,
        warehouse_id: int,
        qty: float,
        remarks: str,
        user: str | None = None,
    ):

        if qty == 0:
            raise ValueError(
                "Adjustment quantity cannot be zero."
            )

        if qty > 0:

            return (
                InventoryTransactionService.post_transaction(
                    db=db,
                    media_roll_id=media_roll_id,
                    transaction_type=(
                        InventoryTransactionType.ADJUSTMENT
                    ),
                    reference_module=Module.INVENTORY,
                    warehouse_id=warehouse_id,
                    qty_in=qty,
                    remarks=remarks,
                    user=user,
                )
            )

        return (
            InventoryTransactionService.post_transaction(
                db=db,
                media_roll_id=media_roll_id,
                transaction_type=(
                    InventoryTransactionType.ADJUSTMENT
                ),
                reference_module=Module.INVENTORY,
                warehouse_id=warehouse_id,
                qty_out=abs(qty),
                remarks=remarks,
                user=user,
            )
        )

    # =========================================================
    # WAREHOUSE TRANSFER
    # =========================================================

    @staticmethod
    def transfer(
        db: Session,
        media_roll_id: int,
        from_warehouse_id: int,
        to_warehouse_id: int,
        qty: float,
        remarks: str = "Warehouse Transfer",
        user: str | None = None,
    ):

        if qty <= 0:
            raise ValueError(
                "Transfer quantity must be greater than zero."
            )

        if from_warehouse_id == to_warehouse_id:
            raise ValueError(
                (
                    "Source and destination warehouse "
                    "cannot be the same."
                )
            )

        InventoryTransactionService.post_transaction(
            db=db,
            media_roll_id=media_roll_id,
            transaction_type=(
                InventoryTransactionType.TRANSFER
            ),
            reference_module=(
                Module.WAREHOUSE_TRANSFER
            ),
            warehouse_id=from_warehouse_id,
            qty_out=qty,
            remarks=remarks,
            user=user,
        )

        return (
            InventoryTransactionService.post_transaction(
                db=db,
                media_roll_id=media_roll_id,
                transaction_type=(
                    InventoryTransactionType.TRANSFER
                ),
                reference_module=(
                    Module.WAREHOUSE_TRANSFER
                ),
                warehouse_id=to_warehouse_id,
                qty_in=qty,
                remarks=remarks,
                user=user,
            )
        )

    # =========================================================
    # RESERVE PRODUCTION BATCH
    # =========================================================

    @staticmethod
    def reserve_batch(
        db: Session,
        batch,
    ):
        """
        Reserve all media-roll allocations for a production batch.

        Reservation is NOT a physical inventory movement.

        Therefore:
            - qty_in = 0
            - qty_out = 0
            - no inventory transaction is created

        The important integrity rule is that allocations against
        the same media roll are aggregated before validation.

        Example:

            Roll balance = 1,000 Sq Ft

            Allocation A = 700
            Allocation B = 400

        The old implementation checked them independently.

        This implementation checks:

            700 + 400 = 1,100

        and correctly rejects the batch.
        """

        allocations = (
            db.query(ProductionAllocation)
            .filter(
                ProductionAllocation.production_batch_id
                == batch.id
            )
            .all()
        )

        if not allocations:
            return []

        # -----------------------------------------------------
        # Aggregate requested quantities by roll
        # -----------------------------------------------------

        requested_by_roll = defaultdict(float)

        allocation_by_roll = defaultdict(list)

        for allocation in allocations:

            if allocation.media_roll_id is None:
                raise ValueError(
                    (
                        f"Allocation {allocation.id} "
                        "has no media roll."
                    )
                )

            if allocation.allocated_sqft <= 0:
                raise ValueError(
                    (
                        f"Invalid allocation quantity "
                        f"for allocation {allocation.id}."
                    )
                )

            # Already completed allocations do not need a new
            # reservation.
            if allocation.status == "COMPLETED":
                continue

            requested_by_roll[
                allocation.media_roll_id
            ] += float(
                allocation.allocated_sqft
            )

            allocation_by_roll[
                allocation.media_roll_id
            ].append(allocation)

        # -----------------------------------------------------
        # Validate every roll as an aggregate
        # -----------------------------------------------------

        for roll_id, requested_quantity in (
            requested_by_roll.items()
        ):

            roll = (
                db.query(MediaRoll)
                .filter(
                    MediaRoll.id == roll_id
                )
                .with_for_update()
                .first()
            )

            if roll is None:
                raise ValueError(
                    (
                        "Media Roll not found for "
                        f"roll ID {roll_id}."
                    )
                )

            if not roll.is_active:
                raise ValueError(
                    (
                        f"Media Roll {roll.roll_number} "
                        "is inactive."
                    )
                )

            physical_balance = float(
                roll.available_sqft or 0.0
            )

            # -------------------------------------------------
            # Existing reservations from OTHER batches
            # -------------------------------------------------

            reserved_allocations = (
                db.query(
                    ProductionAllocation
                )
                .filter(
                    ProductionAllocation.media_roll_id
                    == roll.id,
                    ProductionAllocation.status.in_(
                        [
                            "ALLOCATED",
                            "RESERVED",
                            "PARTIALLY_PRINTED",
                            "PRINTING",
                        ]
                    ),
                    ProductionAllocation.production_batch_id
                    != batch.id,
                )
                .all()
            )

            existing_reserved = sum(
                float(
                    allocation.allocated_sqft
                    or 0.0
                )
                for allocation
                in reserved_allocations
            )

            usable_balance = (
                physical_balance
                - existing_reserved
            )

            if requested_quantity > (
                usable_balance + 0.0001
            ):

                raise ValueError(
                    (
                        f"Insufficient available media on "
                        f"roll {roll.roll_number}. "
                        f"Physical balance: "
                        f"{physical_balance:,.2f} Sq Ft; "
                        f"already reserved by other batches: "
                        f"{existing_reserved:,.2f} Sq Ft; "
                        f"available for this batch: "
                        f"{max(usable_balance, 0):,.2f} Sq Ft; "
                        f"requested by this batch: "
                        f"{requested_quantity:,.2f} Sq Ft."
                    )
                )

        # -----------------------------------------------------
        # All rolls passed validation.
        # Now mark allocations reserved.
        # -----------------------------------------------------

        reserved = []

        for allocation in allocations:

            if allocation.status == "COMPLETED":
                continue

            allocation.status = "RESERVED"

            reserved.append(
                allocation
            )

        db.flush()

        return reserved