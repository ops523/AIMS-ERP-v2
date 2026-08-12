from sqlalchemy.orm import Session

from models.activity_log import ActivityLog


class ActivityLogService:

    @staticmethod
    def log(
        db: Session,
        module: str,
        reference: str,
        activity: str,
        performed_by: str | None = None,
    ):

        log = ActivityLog(

            module=module,

            reference=reference,

            activity=activity,

            performed_by=(
                performed_by
                if performed_by
                else "SYSTEM"
            ),
        )

        db.add(log)

        db.flush()

        return log
