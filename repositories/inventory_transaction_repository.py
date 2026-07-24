from sqlalchemy.orm import Session

from models.inventory_transaction import InventoryTransaction


class InventoryTransactionRepository:

    @staticmethod
    def create(
        db: Session,
        transaction: InventoryTransaction,
    ):

        db.add(transaction)

        db.commit()

        db.refresh(transaction)

        return transaction

    @staticmethod
    def get_all(
        db: Session,
    ):

        return (
            db.query(InventoryTransaction)
            .order_by(
                InventoryTransaction.id.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_roll(
        db: Session,
        media_roll_id: int,
    ):

        return (
            db.query(InventoryTransaction)
            .filter(
                InventoryTransaction.media_roll_id == media_roll_id
            )
            .order_by(
                InventoryTransaction.id.desc()
            )
            .all()
        )
