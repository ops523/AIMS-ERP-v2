from models.activity_log import ActivityLog


class ActivityLogService:

    @staticmethod
    def log(
        db,
        module,
        action,
        reference_number,
        remarks="",
        user=None,
    ):

        log = ActivityLog(

            module=module,

            action=action,

            reference_number=reference_number,

            remarks=remarks,

            user=user,
        )

        db.add(log)
