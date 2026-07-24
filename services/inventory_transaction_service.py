from models.inventory_transaction import InventoryTransaction

from repositories.inventory_transaction_repository import (
    InventoryTransactionRepository,
)


class InventoryTransactionService:

    @staticmethod
    def post_transaction(
        db,
        media_roll_id,
        transaction_type,
        reference_module,
        qty_in=0,
        qty_out=0,
        reference_id=None,
        campaign_id=None,
        printer_id=None,
        warehouse_id=None,
        unit_cost=0,
        total_cost=0,
        wastage_sqft=0,
        remarks=None,
        user=None,
    ):

        # ----------------------------------------
        # Get Current Balance
        # ----------------------------------------

        current_balance = (
            InventoryTransactionRepository.latest_balance(
                db=db,
                media_roll_id=media_roll_id,
            )
        )

        # ----------------------------------------
        # Calculate New Balance
        # ----------------------------------------

        new_balance = (
            current_balance
            + qty_in
            - qty_out
        )

        # ----------------------------------------
        # Create Inventory Transaction
        # ----------------------------------------

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

        # ----------------------------------------
        # Save Transaction
        # ----------------------------------------

        return InventoryTransactionRepository.create(
            db=db,
            transaction=transaction,
        )

    @staticmethod
    def receive_roll(
        db,
        media_roll_id,
        warehouse_id,
        qty,
        user,
        remarks="Media Roll Received",
    ):

        return InventoryTransactionService.post_transaction(

            db=db,

            media_roll_id=media_roll_id,

            transaction_type="RECEIPT",

            reference_module="Receive Roll",

            warehouse_id=warehouse_id,

            qty_in=qty,

            qty_out=0,

            remarks=remarks,

            user=user,

        )

    @staticmethod
    def consume_roll(
        db,
        media_roll_id,
        campaign_id,
        printer_id,
        warehouse_id,
        qty,
        wastage=0,
        remarks="Roll Consumed",
        user=None,
    ):

        return InventoryTransactionService.post_transaction(

            db=db,

            media_roll_id=media_roll_id,

            transaction_type="CONSUMPTION",

            reference_module="Printing",

            campaign_id=campaign_id,

            printer_id=printer_id,

            warehouse_id=warehouse_id,

            qty_in=0,

            qty_out=qty,

            wastage_sqft=wastage,

            remarks=remarks,

            user=user,

        )

    @staticmethod
    def adjust_stock(
        db,
        media_roll_id,
        warehouse_id,
        qty,
        remarks,
        user=None,
    ):

        if qty >= 0:

            return InventoryTransactionService.post_transaction(

                db=db,

                media_roll_id=media_roll_id,

                transaction_type="ADJUSTMENT",

                reference_module="Stock Adjustment",

                warehouse_id=warehouse_id,

                qty_in=qty,

                qty_out=0,

                remarks=remarks,

                user=user,

            )

        return InventoryTransactionService.post_transaction(

            db=db,

            media_roll_id=media_roll_id,

            transaction_type="ADJUSTMENT",

            reference_module="Stock Adjustment",

            warehouse_id=warehouse_id,

            qty_in=0,

            qty_out=abs(qty),

            remarks=remarks,

            user=user,

        )
