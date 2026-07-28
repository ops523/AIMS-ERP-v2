from models.activity_log import ActivityLog


class ActivityLogService:

    @staticmethod
    def batch_created(
        db,
        batch,
    ):

        log = ActivityLog(

            module="Production",

            action="Batch Created",

            reference_number=batch.batch_number,

            remarks=f"Production Batch {batch.batch_number} created.",
        )

        db.add(log)
