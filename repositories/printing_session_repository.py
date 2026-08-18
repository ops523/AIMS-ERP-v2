from __future__ import annotations

from sqlalchemy.orm import Session

from models.printing_session import PrintingSession


class PrintingSessionRepository:

    @staticmethod
    def create(
        db: Session,
        session: PrintingSession,
    ) -> PrintingSession:
        """
        Create a printing session without committing.

        Transaction ownership remains with the calling service.
        """

        db.add(session)
        db.flush()

        return session

    @staticmethod
    def get_by_batch(
        db: Session,
        batch_id: int,
    ):
        return (
            db.query(PrintingSession)
            .filter(
                PrintingSession.production_batch_id
                == batch_id
            )
            .order_by(
                PrintingSession.id
            )
            .all()
        )

    @staticmethod
    def get_active(
        db: Session,
    ):
        return (
            db.query(PrintingSession)
            .filter(
                PrintingSession.status
                == "IN_PROGRESS"
            )
            .order_by(
                PrintingSession.id
            )
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        session_id: int,
    ):
        return (
            db.query(PrintingSession)
            .filter(
                PrintingSession.id
                == session_id
            )
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        session: PrintingSession,
    ) -> PrintingSession:

        db.add(session)
        db.flush()

        return session
