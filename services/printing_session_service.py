from __future__ import annotations

from sqlalchemy.orm import Session

from models.printing_session import PrintingSession

from repositories.printing_session_repository import (
    PrintingSessionRepository,
)


class PrintingSessionService:

    @staticmethod
    def start_session(
        db: Session,
        batch,
        printer,
        operator_name: str | None = None,
        shift: str = "DAY",
        remarks: str | None = None,
    ) -> PrintingSession:
        """
        Start a printing session for a production batch.

        This method intentionally does NOT commit.

        The caller owns the surrounding transaction.
        """

        if batch is None:
            raise ValueError(
                "Production batch is required."
            )

        if printer is None:
            raise ValueError(
                "Printer is required."
            )

        # Determine the next session number.
        existing_sessions = (
            PrintingSessionRepository.get_by_batch(
                db,
                batch.id,
            )
        )

        next_session_number = (
            len(existing_sessions) + 1
        )

        session = PrintingSession(
            production_batch_id=batch.id,
            printer_id=printer.id,
            session_number=next_session_number,
            operator_name=operator_name,
            shift=shift,
            planned_sqft=batch.total_planned_sqft,
            printed_sqft=0,
            wastage_sqft=0,
            status="IN_PROGRESS",
            remarks=remarks,
        )

        return PrintingSessionRepository.create(
            db,
            session,
        )

    @staticmethod
    def complete_session(
        db: Session,
        session: PrintingSession,
        printed_sqft: float,
        wastage_sqft: float = 0,
        remarks: str | None = None,
    ) -> PrintingSession:
        """
        Complete an active printing session.
        """

        if printed_sqft < 0:
            raise ValueError(
                "Printed quantity cannot be negative."
            )

        if wastage_sqft < 0:
            raise ValueError(
                "Wastage quantity cannot be negative."
            )

        session.printed_sqft = printed_sqft
        session.wastage_sqft = wastage_sqft

        if remarks is not None:
            session.remarks = remarks

        session.status = "COMPLETED"

        db.flush()

        return session

    @staticmethod
    def get_batch_sessions(
        db: Session,
        batch_id: int,
    ):
        return PrintingSessionRepository.get_by_batch(
            db,
            batch_id,
        )

    @staticmethod
    def get_active_sessions(
        db: Session,
    ):
        return PrintingSessionRepository.get_active(
            db,
        )
