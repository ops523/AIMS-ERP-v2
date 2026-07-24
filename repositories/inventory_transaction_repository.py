from sqlalchemy.orm import Session

from models.inventory_transaction import InventoryTransaction


class InventoryTransactionRepository:

    @staticmethod
    def create(
        db: Session,
        transaction: InventoryTransaction,
    ):

        db.add(transaction)
        db.flush()
        db.refresh(transaction)

        return transaction

    @staticmethod
    def latest_balance(
        db: Session,
        media_roll_id: int,
    ):

        tx = (
            db.query(InventoryTransaction)
            .filter(
                InventoryTransaction.media_roll_id == media_roll_id
            )
            .order_by(
                InventoryTransaction.id.desc()
            )
            .first()
        )

        if tx is None:
            return 0

        return tx.balance_qty

    @staticmethod
    def history(
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
