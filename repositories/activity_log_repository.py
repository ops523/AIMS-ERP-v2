from sqlalchemy.orm import Session

from models.activity_log import ActivityLog


class ActivityLogRepository:

    @staticmethod
    def log(
        db: Session,
        module: str,
        reference: str,
        activity: str,
        performed_by: str,
    ):

        obj = ActivityLog(
            module=module,
            reference=reference,
            activity=activity,
            performed_by=performed_by,
        )

        db.add(obj)
        db.flush()

        return obj
