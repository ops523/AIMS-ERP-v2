from repositories.media_roll_history_repository import (
    MediaRollHistoryRepository,
)

from models.media_roll_history import (
    MediaRollHistory,
)

from constants.qr_status import CREATED

from constants.qr_events import QR_CREATED

from services.activity_logger import ActivityLogger


class QRService:

    COMPANY_PREFIX = "ADW"

    @staticmethod
    def generate_roll_payload(
        media_roll,
    ):

        return (
            f"{QRService.COMPANY_PREFIX}"
            f"|MR|"
            f"{media_roll.uuid}"
        )

    @staticmethod
    def record_creation(
        db,
        media_roll,
        user="System",
    ):

        history = MediaRollHistory(

            media_roll_id=media_roll.id,

            event=QR_CREATED,

            previous_status=None,

            current_status=CREATED,

            reference_type="Media Roll",

            reference_number=media_roll.roll_number,

            remarks="QR Generated",

            scanned_by=user,

        )

        return (
            MediaRollHistoryRepository.add(
                db,
                history,
            )
        )

    @staticmethod
    def record_event(
        db,
        media_roll,
        event,
        previous_status,
        current_status,
        reference_type="",
        reference_number="",
        remarks="",
        scanned_by="System",
        location="",
    ):

        history = MediaRollHistory(

            media_roll_id=media_roll.id,

            event=event,

            previous_status=previous_status,

            current_status=current_status,

            reference_type=reference_type,

            reference_number=reference_number,

            remarks=remarks,

            scanned_by=scanned_by,

            location=location,

        )

        return (
            MediaRollHistoryRepository.add(
                db,
                history,
            )
        )

    @staticmethod
    def get_history(
        db,
        media_roll_id,
    ):

        return (
            MediaRollHistoryRepository.get_history(
                db,
                media_roll_id,
            )
        )

    ActivityLogger.log(
        db=db,
        module="QR",
        reference=media_roll.roll_number,
        activity=event,
        performed_by=scanned_by,
    )
