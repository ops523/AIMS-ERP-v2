from sqlalchemy.orm import Session

from models.activity_log import ActivityLog


class ActivityLogger:

    @staticmethod
    def log(
        db: Session,
        module: str,
        reference: str,
        activity: str,
        performed_by: str,
    ):

        log = ActivityLog(

            module=module,

            reference=reference,

            activity=activity,

            performed_by=performed_by,

        )

        db.add(log)

        db.commit()

        db.refresh(log)

        return log
