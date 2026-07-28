from sqlalchemy.orm import Session

from models.printing_session import PrintingSession


class PrintingSessionRepository:

    @staticmethod
    def create(
        db: Session,
        session: PrintingSession,
    ):
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_by_batch(
        db: Session,
        batch_id: int,
    ):
        return (
            db.query(PrintingSession)
            .filter(
                PrintingSession.production_batch_id == batch_id
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
                PrintingSession.status == "IN_PROGRESS"
            )
            .all()
        )
