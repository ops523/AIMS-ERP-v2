from models.printing_session import PrintingSession

from repositories.printing_session_repository import (
    PrintingSessionRepository,
)


class PrintingSessionService:

    @staticmethod
    def start_session(
        db,
        batch,
        printer,
    ):

        session = PrintingSession(
            production_batch_id=batch.id,
            printer_id=printer.id,
            planned_sqft=batch.total_planned_sqft,
            status="IN_PROGRESS",
        )

        return PrintingSessionRepository.create(
            db,
            session,
        )
