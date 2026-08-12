from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from components.qr_label_generator import QRLabelGenerator
from core.storage_manager import StorageManager

from constants.qr_events import QR_CREATED

from repositories.media_roll_history_repository import (
    MediaRollHistoryRepository,
)


class QRService:

    COMPANY_PREFIX = "ADW"

    MEDIA_ROLL = "MR"

    PACKAGE = "PK"

    DISPATCH = "DS"

    # =========================================================
    # PAYLOAD
    # =========================================================

    @classmethod
    def generate_payload(
        cls,
        entity: str,
        uuid: str,
    ) -> str:

        return (
            f"{cls.COMPANY_PREFIX}|"
            f"{entity}|"
            f"{uuid}"
        )

    # =========================================================
    # MEDIA ROLL QR
    # =========================================================

    @classmethod
    def generate_media_roll_qr(
        cls,
        db: Session,
        media_roll,
        user: str | None = None,
    ):

        if not media_roll.uuid:

            raise ValueError(
                "Media Roll UUID is required "
                "before QR generation."
            )

        if not media_roll.roll_number:

            raise ValueError(
                "Roll Number is required "
                "before QR generation."
            )

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

        media_roll.qr_code = (
            media_roll.roll_number
        )

        media_roll.qr_payload = payload

        media_roll.qr_image_path = str(
            qr_path
        )

        media_roll.qr_generated_on = (
            datetime.utcnow()
        )

        db.flush()

        MediaRollHistoryRepository.add_event(
            db=db,
            media_roll_id=media_roll.id,
            event=QR_CREATED,
            previous_status=media_roll.status,
            current_status=media_roll.status,
            reference_type="MEDIA_ROLL",
            reference_number=media_roll.roll_number,
            remarks="QR generated",
            scanned_by=user,
        )

        return media_roll

    # =========================================================
    # QR ARTIFACT CLEANUP
    # =========================================================

    @classmethod
    def delete_qr_artifact(
        cls,
        media_roll,
    ) -> None:
        """
        Delete the physical QR image associated with a Media Roll.

        Database rollback is handled by TransactionService. This method
        only removes the filesystem artifact created by QR generation.
        Cleanup failures are deliberately swallowed so they never hide
        the original business transaction error.
        """

        if media_roll is None:
            return

        qr_image_path = getattr(
            media_roll,
            "qr_image_path",
            None,
        )

        if not qr_image_path:
            return

        try:
            path = Path(qr_image_path)

            if path.exists():
                path.unlink()

        except OSError:
            pass
