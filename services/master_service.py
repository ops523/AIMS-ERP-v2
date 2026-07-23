from repositories.master_repository import MasterRepository


class MasterService:

    @staticmethod
    def validate_name(
        db,
        model,
        name,
        current_id=None
    ):

        existing = MasterRepository.get_by_name(
            db,
            model,
            name.strip()
        )

        if existing is None:
            return True, ""

        if current_id:

            if existing.id == current_id:
                return True, ""

        return False, "Name already exists."

    @staticmethod
    def activate(
        db,
        obj
    ):

        obj.active = True

        MasterRepository.update(db)

    @staticmethod
    def deactivate(
        db,
        obj
    ):

        obj.active = False

        MasterRepository.update(db)
