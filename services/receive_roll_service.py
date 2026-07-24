from models.media_roll import MediaRoll

from repositories.media_roll_repository import MediaRollRepository

from services.code_generator import CodeGenerator
from services.roll_measurement_service import RollMeasurementService
from services.inventory_transaction_service import (
    InventoryTransactionService,
)
from services.activity_service import ActivityService


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

        # --------------------------------------------------
        # Generate Roll Code
        # --------------------------------------------------

        roll_code = CodeGenerator.generate(
            db=db,
            model=MediaRoll,
            code_field="roll_code",
            prefix="ROLL",
        )

        # --------------------------------------------------
        # Calculate Nominal Sq Ft
        # --------------------------------------------------

        nominal_sqft = round(
            roll_width * nominal_length,
            2,
        )

        # --------------------------------------------------
        # Create Media Roll
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Save Roll Measurement
        # --------------------------------------------------

        RollMeasurementService.create_measurement(

            db=db,

            media_roll_id=media_roll.id,

            measured_length_ft=measured_length,

            measured_width_ft=measured_width,

            measured_by=received_by,

            remarks=remarks,

        )

        # --------------------------------------------------
        # Create Inventory Ledger Entry
        # --------------------------------------------------

        InventoryTransactionService.post_transaction(

            db=db,

            media_roll_id=media_roll.id,

            transaction_type="RECEIPT",

            reference_module="Receive Roll",

            qty_in=media_roll.total_sqft,

            qty_out=0,

            reference_id=media_roll.id,

            remarks="Media Roll Received",

            user=received_by,

        )

        # --------------------------------------------------
        # Activity Log
        # --------------------------------------------------

        ActivityService.log(

            db=db,

            module="Inventory",

            reference=roll_code,

            activity="Media Roll Received",

            user=received_by,

        )

        # --------------------------------------------------
        # TODO (Sprint 4.2)
        # --------------------------------------------------
        # Generate QR Code
        # Save QR Image
        # Print QR Sticker
        # --------------------------------------------------

        return media_roll

        try:

        media_roll = MediaRollRepository.create(...)

        RollMeasurementService.create_measurement(...)

        InventoryTransactionService.post_transaction(...)

        ActivityService.log(...)

        db.commit()

        return media_roll

        except Exception:

        db.rollback()

        raise
