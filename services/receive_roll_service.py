from models.media_roll import MediaRoll

from repositories.media_roll_repository import MediaRollRepository

from services.code_generator import CodeGenerator
from services.roll_measurement_service import RollMeasurementService
from services.activity_service import ActivityService

from models.inventory_transaction import InventoryTransaction

from repositories.inventory_transaction_repository import (
    InventoryTransactionRepository,
)


class ReceiveRollService:

    @staticmethod
    def receive_roll(
        db,

        supplier_id,
        manufacturer_id,
        media_product_id,
        warehouse_id,

        roll_width,

        nominal_length,

        measured_length,

        measured_width,

        received_by,

        remarks=None,
    ):

        roll_code = CodeGenerator.generate(
            db=db,
            model=MediaRoll,
            code_field="roll_code",
            prefix="ROLL",
        )

        nominal_sqft = round(
            roll_width * nominal_length,
            2
        )

        media_roll = MediaRoll(

            roll_code=roll_code,

            supplier_id=supplier_id,

            manufacturer_id=manufacturer_id,

            media_product_id=media_product_id,

            warehouse_id=warehouse_id,

            width_ft=roll_width,

            length_ft=nominal_length,

            total_sqft=nominal_sqft,

            balance_sqft=nominal_sqft,
        )

        media_roll = MediaRollRepository.create(
            db,
            media_roll,
        )

        RollMeasurementService.create_measurement(

            db=db,

            media_roll_id=media_roll.id,

            measured_length_ft=measured_length,

            measured_width_ft=measured_width,

            measured_by=received_by,

            remarks=remarks,
        )

        InventoryTransactionRepository.create(

            db,

            InventoryTransaction(

            media_roll_id=media_roll.id,

            transaction_type="RECEIPT",

            quantity_sqft=media_roll.total_sqft,

            remarks="Roll Received",

            )

        )

        ActivityService.log(

            db=db,

            module="Inventory",

            reference=roll_code,

            activity="Media Roll Received",

            user=received_by,
        )

        return media_roll
