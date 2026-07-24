from sqlalchemy.orm import Session

from models.inventory_transaction import InventoryTransaction


class InventoryLedgerRepository:

    @staticmethod
    def get_roll_history(
        db: Session,
        media_roll_id: int,
    ):

        return (

            db.query(InventoryTransaction)

            .filter(
                InventoryTransaction.media_roll_id == media_roll_id
            )

            .order_by(
                InventoryTransaction.transaction_date.asc()
            )

            .all()

        )
