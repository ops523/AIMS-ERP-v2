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

        )

        return InventoryTransactionRepository.create(
            db=db,
            transaction=transaction,
        )
