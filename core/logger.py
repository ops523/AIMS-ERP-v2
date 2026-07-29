from sqlalchemy.orm import Session

from models.activity_log import ActivityLog


class ActivityLogger:

    @staticmethod
    def log(
        db: Session,
        module,
        reference,
        activity,
        performed_by="SYSTEM",
    ):

        db.add(

            ActivityLog(

                module=module,

                reference=reference,

                activity=activity,

                performed_by=performed_by,

            )

        )

        db.commit()
