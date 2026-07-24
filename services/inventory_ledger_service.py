from repositories.inventory_ledger_repository import (
    InventoryLedgerRepository,
)


class InventoryLedgerService:

    @staticmethod
    def history(
        db,
        media_roll_id,
    ):

        return InventoryLedgerRepository.get_roll_history(
            db,
            media_roll_id,
        )
