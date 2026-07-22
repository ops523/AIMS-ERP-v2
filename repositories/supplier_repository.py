from sqlalchemy.orm import Session

from models.supplier import Supplier


class SupplierRepository:

    @staticmethod
    def get_all(db: Session):

        return (

            db.query(Supplier)

            .filter(Supplier.is_active == True)

            .order_by(Supplier.supplier_name)

            .all()

        )
