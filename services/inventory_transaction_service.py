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

        transaction = InventoryTransaction(

            media_roll_id=media_roll_id,

            transaction_type=transaction_type,

            reference_module=reference_module,

            reference_id=reference_id,

            qty_in=qty_in,

            qty_out=qty_out,

            balance_qty=new_balance,

            remarks=remarks,

            performed_by=user,
            
            campaign_id=campaign_id,

            printer_id=printer_id,

            warehouse_id=warehouse_id,

            unit_cost=unit_cost,

            total_cost=total_cost,

            wastage_sqft=wastage_sqft,

        )

        return InventoryTransactionRepository.create(
            db=db,
            transaction=transaction,
        )
