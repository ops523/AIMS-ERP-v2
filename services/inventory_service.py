from sqlalchemy.orm import Session

from models.media_roll import MediaRoll

from models.inventory_transaction import InventoryTransaction


class InventoryService:

    @staticmethod
    def opening_transaction(

        db: Session,

        media_roll: MediaRoll

    ):

        trx = InventoryTransaction(

            media_roll_id=media_roll.id,

            transaction_type="OPENING",

            quantity_sqft=media_roll.total_sqft,

            balance_sqft=media_roll.total_sqft,

            remarks="Opening Balance"

        )

        db.add(trx)
