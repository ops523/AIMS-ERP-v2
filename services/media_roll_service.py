from __future__ import annotations

from sqlalchemy.orm import Session

from constants.document_types import DocumentType
from constants.modules import Module
from constants.status import MediaRollStatus
from constants.inventory import (
    InventoryTransactionType,
)

from models.media_roll import MediaRoll

from repositories.media_roll_repository import (
    MediaRollRepository,
)

from repositories.media_roll_history_repository import (
    MediaRollHistoryRepository,
)

from services.document_number_service import (
    DocumentNumberService,
)

from services.qr_service import QRService

from services.activity_log_service import (
    ActivityLogService,
)

from services.inventory_transaction_service import (
    InventoryTransactionService,
)

from services.transaction_service import (
    TransactionService,
)

from services.service_result import (
    ServiceResult,
)

from validators.media_roll_validator import (
    MediaRollValidator,
)


class MediaRollService:

    # =========================================================
    # STATUS TRANSITIONS
    # =========================================================

    ALLOWED_TRANSITIONS = {

        MediaRollStatus.RECEIVED: {
            MediaRollStatus.AVAILABLE,
            MediaRollStatus.DAMAGED,
            MediaRollStatus.RETURNED,
        },

        MediaRollStatus.AVAILABLE: {
            MediaRollStatus.RESERVED,
            MediaRollStatus.ALLOCATED,
            MediaRollStatus.DAMAGED,
            MediaRollStatus.RETURNED,
            MediaRollStatus.LOST,
        },

        MediaRollStatus.RESERVED: {
            MediaRollStatus.AVAILABLE,
            MediaRollStatus.ALLOCATED,
        },

        MediaRollStatus.ALLOCATED: {
            MediaRollStatus.AVAILABLE,
            MediaRollStatus.PRINTING,
        },

        MediaRollStatus.PRINTING: {
            MediaRollStatus.PRINTED,
            MediaRollStatus.PARTIALLY_USED,
        },

        MediaRollStatus.PRINTED: {
            MediaRollStatus.PARTIALLY_USED,
            MediaRollStatus.CONSUMED,
        },

        MediaRollStatus.PARTIALLY_USED: {
            MediaRollStatus.PRINTED,
            MediaRollStatus.CONSUMED,
            MediaRollStatus.DAMAGED,
        },

        MediaRollStatus.CONSUMED: set(),

        MediaRollStatus.RETURNED: {
            MediaRollStatus.AVAILABLE,
        },

        MediaRollStatus.DAMAGED: set(),

        MediaRollStatus.LOST: set(),
    }

    # =========================================================
    # CREATE / RECEIVE
    # =========================================================

    @classmethod
    def receive(
        cls,
        db: Session,
        media_roll: MediaRoll,
        user: str | None = None,
    ) -> ServiceResult:

        validation = (
            MediaRollValidator.validate_create(
                media_roll
            )
        )

        if not validation.success:

            return validation

        try:

            with TransactionService.transaction(db):

                # -------------------------------------------------
                # Asset ID
                # -------------------------------------------------

                if not media_roll.asset_id:

                    media_roll.asset_id = (
                        cls._generate_asset_id(
                            media_roll
                        )
                    )

                # -------------------------------------------------
                # Roll Number
                # -------------------------------------------------

                if not media_roll.roll_number:

                    media_roll.roll_number = (
                        DocumentNumberService.generate(
                            db,
                            DocumentType.MEDIA_ROLL,
                        )
                    )

                # -------------------------------------------------
                # Initial Status
                # -------------------------------------------------

                media_roll.status = (
                    MediaRollStatus.RECEIVED
                )

                # -------------------------------------------------
                # Available Quantity
                # -------------------------------------------------

                media_roll.available_sqft = (
                    media_roll.total_sqft
                )

                media_roll.is_active = True

                # -------------------------------------------------
                # Persist Roll
                # -------------------------------------------------

                db.add(media_roll)

                db.flush()

                # -------------------------------------------------
                # QR
                # -------------------------------------------------

                QRService.generate_media_roll_qr(
                    db=db,
                    media_roll=media_roll,
                    user=user,
                )

                # -------------------------------------------------
                # Inventory Receipt
                # -------------------------------------------------

                InventoryTransactionService.receive_roll(
                    db=db,
                    media_roll_id=media_roll.id,
                    warehouse_id=media_roll.warehouse_id,
                    qty=media_roll.total_sqft,
                    user=user,
                    remarks="Media Roll Received",
                )

                # -------------------------------------------------
                # Status → AVAILABLE
                # -------------------------------------------------

                previous_status = (
                    media_roll.status
                )

                media_roll.status = (
                    MediaRollStatus.AVAILABLE
                )

                MediaRollHistoryRepository.add_event(
                    db=db,
                    media_roll_id=media_roll.id,
                    event="RECEIVED",
                    previous_status=previous_status,
                    current_status=media_roll.status,
                    reference_type="MEDIA_ROLL",
                    reference_number=media_roll.roll_number,
                    remarks="Media Roll received into inventory",
                    scanned_by=user,
                )

                # -------------------------------------------------
                # Activity Log
                # -------------------------------------------------

                ActivityLogService.log(
                    db=db,
                    module=Module.MEDIA_ROLL,
                    reference=media_roll.roll_number,
                    activity="Media Roll received",
                    performed_by=user,
                )

                return ServiceResult.ok(
                    data=media_roll,
                    message=(
                        "Media Roll received successfully."
                    ),
                )

        except Exception as exc:

            return ServiceResult.fail(
                "Unable to receive Media Roll.",
                [str(exc)],
            )

    # =========================================================
    # CREATE ALIAS
    # =========================================================

    @classmethod
    def create(
        cls,
        db: Session,
        media_roll: MediaRoll,
        user: str | None = None,
    ) -> ServiceResult:

        return cls.receive(
            db=db,
            media_roll=media_roll,
            user=user,
        )

    # =========================================================
    # UPDATE
    # =========================================================

    @classmethod
    def update(
        cls,
        db: Session,
        media_roll: MediaRoll,
        user: str | None = None,
    ) -> ServiceResult:

        validation = (
            MediaRollValidator.validate_create(
                media_roll
            )
        )

        if not validation.success:

            return validation

        try:

            with TransactionService.transaction(db):

                db.flush()

                ActivityLogService.log(
                    db=db,
                    module=Module.MEDIA_ROLL,
                    reference=media_roll.roll_number,
                    activity="Media Roll updated",
                    performed_by=user,
                )

                return ServiceResult.ok(
                    data=media_roll,
                    message=(
                        "Media Roll updated successfully."
                    ),
                )

        except Exception as exc:

            return ServiceResult.fail(
                "Unable to update Media Roll.",
                [str(exc)],
            )

    # =========================================================
    # CHANGE STATUS
    # =========================================================

    @classmethod
    def change_status(
        cls,
        db: Session,
        media_roll_id: int,
        new_status: str,
        reason: str | None = None,
        user: str | None = None,
    ) -> ServiceResult:

        try:

            with TransactionService.transaction(db):

                media_roll = (
                    MediaRollRepository.get(
                        db,
                        media_roll_id,
                    )
                )

                if media_roll is None:

                    return ServiceResult.fail(
                        "Media Roll not found."
                    )

                old_status = media_roll.status

                if old_status == new_status:

                    return ServiceResult.fail(
                        "Media Roll is already in "
                        f"{new_status} status."
                    )

                allowed = cls.ALLOWED_TRANSITIONS.get(
                    old_status,
                    set(),
                )

                if new_status not in allowed:

                    return ServiceResult.fail(
                        (
                            f"Invalid status transition: "
                            f"{old_status} → {new_status}"
                        )
                    )

                media_roll.status = new_status

                db.flush()

                MediaRollHistoryRepository.add_event(
                    db=db,
                    media_roll_id=media_roll.id,
                    event=new_status,
                    previous_status=old_status,
                    current_status=new_status,
                    reference_type="MEDIA_ROLL",
                    reference_number=media_roll.roll_number,
                    remarks=reason,
                    scanned_by=user,
                )

                ActivityLogService.log(
                    db=db,
                    module=Module.MEDIA_ROLL,
                    reference=media_roll.roll_number,
                    activity=(
                        f"Status changed from "
                        f"{old_status} to {new_status}"
                    ),
                    performed_by=user,
                )

                return ServiceResult.ok(
                    data=media_roll,
                    message=(
                        f"Media Roll status changed "
                        f"to {new_status}."
                    ),
                )

        except Exception as exc:

            return ServiceResult.fail(
                "Unable to change Media Roll status.",
                [str(exc)],
            )

    # =========================================================
    # RESERVE
    # =========================================================

    @classmethod
    def reserve(
        cls,
        db: Session,
        media_roll_id: int,
        reason: str | None = None,
        user: str | None = None,
    ):

        return cls.change_status(
            db=db,
            media_roll_id=media_roll_id,
            new_status=MediaRollStatus.RESERVED,
            reason=reason or "Roll reserved",
            user=user,
        )

    # =========================================================
    # ALLOCATE
    # =========================================================

    @classmethod
    def allocate(
        cls,
        db: Session,
        media_roll_id: int,
        reason: str | None = None,
        user: str | None = None,
    ):

        return cls.change_status(
            db=db,
            media_roll_id=media_roll_id,
            new_status=MediaRollStatus.ALLOCATED,
            reason=reason or "Roll allocated",
            user=user,
        )

    # =========================================================
    # START PRINTING
    # =========================================================

    @classmethod
    def start_printing(
        cls,
        db: Session,
        media_roll_id: int,
        reason: str | None = None,
        user: str | None = None,
    ):

        return cls.change_status(
            db=db,
            media_roll_id=media_roll_id,
            new_status=MediaRollStatus.PRINTING,
            reason=reason or "Printing started",
            user=user,
        )

    # =========================================================
    # MARK PRINTED
    # =========================================================

    @classmethod
    def mark_printed(
        cls,
        db: Session,
        media_roll_id: int,
        reason: str | None = None,
        user: str | None = None,
    ):

        return cls.change_status(
            db=db,
            media_roll_id=media_roll_id,
            new_status=MediaRollStatus.PRINTED,
            reason=reason or "Printing completed",
            user=user,
        )

    # =========================================================
    # CONSUME
    # =========================================================

    @classmethod
    def consume(
        cls,
        db: Session,
        media_roll_id: int,
        qty_sqft: float,
        user: str | None = None,
        reason: str | None = None,
    ) -> ServiceResult:

        if qty_sqft <= 0:

            return ServiceResult.fail(
                "Consumption quantity must be greater than zero."
            )

        try:

            with TransactionService.transaction(db):

                media_roll = (
                    MediaRollRepository.get(
                        db,
                        media_roll_id,
                    )
                )

                if media_roll is None:

                    return ServiceResult.fail(
                        "Media Roll not found."
                    )

                if qty_sqft > media_roll.available_sqft:

                    return ServiceResult.fail(
                        (
                            "Consumption quantity exceeds "
                            "available square feet."
                        )
                    )

                InventoryTransactionService.post_transaction(
                    db=db,
                    media_roll_id=media_roll.id,
                    transaction_type=(
                        InventoryTransactionType.CONSUMPTION
                    ),
                    reference_module=Module.MEDIA_ROLL,
                    warehouse_id=media_roll.warehouse_id,
                    qty_out=qty_sqft,
                    remarks=(
                        reason
                        or "Media Roll consumption"
                    ),
                    user=user,
                )

                media_roll.available_sqft -= qty_sqft

                if media_roll.available_sqft <= 0:

                    media_roll.available_sqft = 0

                    new_status = (
                        MediaRollStatus.CONSUMED
                    )

                else:

                    new_status = (
                        MediaRollStatus.PARTIALLY_USED
                    )

                old_status = media_roll.status

                media_roll.status = new_status

                db.flush()

                MediaRollHistoryRepository.add_event(
                    db=db,
                    media_roll_id=media_roll.id,
                    event="CONSUMED",
                    previous_status=old_status,
                    current_status=new_status,
                    reference_type="MEDIA_ROLL",
                    reference_number=media_roll.roll_number,
                    remarks=reason,
                    scanned_by=user,
                )

                ActivityLogService.log(
                    db=db,
                    module=Module.MEDIA_ROLL,
                    reference=media_roll.roll_number,
                    activity=(
                        f"{qty_sqft:.2f} sq ft consumed"
                    ),
                    performed_by=user,
                )

                return ServiceResult.ok(
                    data=media_roll,
                    message=(
                        "Media Roll consumption recorded."
                    ),
                )

        except Exception as exc:

            return ServiceResult.fail(
                "Unable to consume Media Roll.",
                [str(exc)],
            )

    # =========================================================
    # RETURN
    # =========================================================

    @classmethod
    def return_roll(
        cls,
        db: Session,
        media_roll_id: int,
        user: str | None = None,
        reason: str | None = None,
    ):

        return cls.change_status(
            db=db,
            media_roll_id=media_roll_id,
            new_status=MediaRollStatus.RETURNED,
            reason=reason or "Roll returned",
            user=user,
        )

    # =========================================================
    # DAMAGE
    # =========================================================

    @classmethod
    def damage(
        cls,
        db: Session,
        media_roll_id: int,
        user: str | None = None,
        reason: str | None = None,
    ):

        return cls.change_status(
            db=db,
            media_roll_id=media_roll_id,
            new_status=MediaRollStatus.DAMAGED,
            reason=reason or "Roll damaged",
            user=user,
        )

    # =========================================================
    # RELEASE RESERVATION
    # =========================================================

    @classmethod
    def release_reservation(
        cls,
        db: Session,
        media_roll_id: int,
        user: str | None = None,
        reason: str | None = None,
    ):

        return cls.change_status(
            db=db,
            media_roll_id=media_roll_id,
            new_status=MediaRollStatus.AVAILABLE,
            reason=reason or "Reservation released",
            user=user,
        )

    # =========================================================
    # SEARCH
    # =========================================================

    @staticmethod
    def search(
        db: Session,
        keyword: str | None = None,
    ):

        return (
            MediaRollRepository.search_keyword(
                db,
                keyword,
            )
        )

    # =========================================================
    # DASHBOARD
    # =========================================================

    @staticmethod
    def dashboard(
        db: Session,
    ):

        return (
            MediaRollRepository.dashboard_summary(
                db
            )
        )

    # =========================================================
    # HISTORY
    # =========================================================

    @staticmethod
    def history(
        db: Session,
        media_roll_id: int,
    ):

        return (
            MediaRollHistoryRepository.get_history(
                db,
                media_roll_id,
            )
        )

    # =========================================================
    # INTERNAL
    # =========================================================

    @staticmethod
    def _generate_asset_id(
        media_roll: MediaRoll,
    ) -> str:

        # Permanent human-readable asset identity.
        # UUID remains the technical identity.

        return (
            f"MR-"
            f"{media_roll.uuid[:8].upper()}"
        )
