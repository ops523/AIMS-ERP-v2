from __future__ import annotations

from sqlalchemy.orm import Session

from constants.document_types import DocumentType
from constants.modules import Module
from constants.status import MediaRollStatus

from repositories.media_roll_repository import MediaRollRepository

from services.document_number_service import DocumentNumberService
from services.qr_service import QRService
from services.storage_manager import StorageManager
from services.activity_log_service import ActivityLogService
from services.transaction_service import TransactionService
from services.service_result import ServiceResult

from models.media_roll import MediaRoll


class MediaRollService:

    @staticmethod
    def create(
        db: Session,
        media_roll: MediaRoll,
        user=None,
    ) -> ServiceResult:

        try:

            with TransactionService.transaction(db):

                #
                # Step 1
                # Generate Roll Number
                #

                if not media_roll.roll_number:

                    media_roll.roll_number = (
                        DocumentNumberService.get_next_number(
                            DocumentType.MEDIA_ROLL
                        )
                    )

                #
                # Step 2
                # Default Status
                #

                if not media_roll.status:

                    media_roll.status = MediaRollStatus.RECEIVED

                #
                # Step 3
                # Save
                #

                MediaRollRepository.create(
                    db,
                    media_roll,
                )

                #
                # Step 4
                # QR generation
                #

                QRService.generate_for_media_roll(
                    db=db,
                    media_roll=media_roll,
                )

                #
                # Step 5
                # Activity Log
                #

                ActivityLogService.log(
                    db=db,
                    module=Module.MEDIA_ROLL,
                    action="CREATE",
                    reference_id=media_roll.id,
                    description=f"Media Roll {media_roll.roll_number} created",
                    user=user,
                )

                return ServiceResult.ok(
                    media_roll,
                    "Media Roll created successfully.",
                )

        except Exception as ex:

            return ServiceResult.fail(str(ex))
