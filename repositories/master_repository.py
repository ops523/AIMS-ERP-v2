from sqlalchemy.orm import Session


class MasterRepository:

    @staticmethod
    def get_all(db: Session, model):

        return (
            db.query(model)
            .order_by(model.name)
            .all()
        )

    @staticmethod
    def get_active(db: Session, model):

        return (
            db.query(model)
            .filter(model.active == True)
            .order_by(model.name)
            .all()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        model,
        record_id: int
    ):

        return (
            db.query(model)
            .filter(model.id == record_id)
            .first()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        model,
        name: str
    ):

        return (
            db.query(model)
            .filter(model.name == name)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        obj
    ):

        db.add(obj)

        db.commit()

        db.refresh(obj)

        return obj

    @staticmethod
    def update(
        db: Session
    ):

        db.commit()

    @staticmethod
    def delete(
        db: Session,
        obj
    ):

        db.delete(obj)

        db.commit()
