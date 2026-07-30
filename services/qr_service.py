from datetime import datetime

from sqlalchemy.orm import Session

from components.qr_label_generator import QRLabelGenerator

from core.storage_manager import StorageManager

from repositories.media_roll_history_repository import (
    MediaRollHistoryRepository,
)

from services.activity_logger import ActivityLogger


class QRService:

    COMPANY_PREFIX = "ADW"

    MEDIA_ROLL = "MR"

    PACKAGE = "PK"

    DISPATCH = "DS"

    @classmethod
    def generate_payload(
        cls,
        entity: str,
        uuid: str,
    ):

        return f"{cls.COMPANY_PREFIX}|{entity}|{uuid}"

    @classmethod
    def generate_media_roll_qr(
        cls,
        db: Session,
        media_roll,
        user: str,
    ):

        payload = cls.generate_payload(

            cls.MEDIA_ROLL,

            str(media_roll.uuid),

        )

        qr_path = StorageManager.qr_path(

            "media_rolls",

            media_roll.roll_number,

        )

        QRLabelGenerator.generate(

            payload,

            qr_path,

        )

        media_roll.qr_payload = payload

        media_roll.qr_image_path = str(qr_path)

        media_roll.qr_generated_on = datetime.now()

        db.commit()

        db.refresh(media_roll)

        MediaRollHistoryRepository.add_event(

            db=db,

            media_roll_id=media_roll.id,

            event="QR_GENERATED",

            remarks="QR Generated",

            performed_by=user,

        )

        ActivityLogger.log(

            db=db,

            module="QR",

            reference=media_roll.roll_number,

            activity="QR Generated",

            performed_by=user,

        )

        return media_roll
