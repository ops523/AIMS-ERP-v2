from repositories.activity_log_repository import (
    ActivityLogRepository,
)


class ActivityService:

    @staticmethod
    def log(
        db,
        module,
        reference,
        activity,
        user,
    ):

        return ActivityLogRepository.log(

            db=db,

            module=module,

            reference=reference,

            activity=activity,

            performed_by=user,

        )
