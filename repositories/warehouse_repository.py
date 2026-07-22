from sqlalchemy.orm import Session

from models.warehouse import Warehouse


class WarehouseRepository:

    @staticmethod
    def get_all(db: Session):

        return (

            db.query(Warehouse)

            .filter(

                Warehouse.is_active == True

            )

            .order_by(

                Warehouse.warehouse_name

            )

            .all()

        )
