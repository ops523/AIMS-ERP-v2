from models.inventory_transaction import InventoryTransaction

from repositories.inventory_transaction_repository import (
    InventoryTransactionRepository,
)


class InventoryTransactionService:

    @staticmethod
    def receive_roll(
        db,
        media_roll_id,
        quantity_sqft,
        remarks="Roll Received",
    ):

        transaction = InventoryTransaction(

            media_roll_id=media_roll_id,

            transaction_type="RECEIPT",

            quantity_sqft=quantity_sqft,

            remarks=remarks,

        )

        return InventoryTransactionRepository.create(
            db,
            transaction,
        )
