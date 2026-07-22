from sqlalchemy.orm import Session

from models.manufacturer import Manufacturer


class ManufacturerRepository:

    @staticmethod
    def get_all(db):

        return (

            db.query(Manufacturer)

            .filter(

                Manufacturer.is_active == True

            )

            .order_by(

                Manufacturer.manufacturer_name

            )

            .all()

        )
