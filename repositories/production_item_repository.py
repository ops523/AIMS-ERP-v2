from sqlalchemy.orm import Session

from models.production_item import ProductionItem


class ProductionItemRepository:

    @staticmethod
    def create(
        db: Session,
        item: ProductionItem,
    ):

        db.add(item)

        db.flush()

        return item

    @staticmethod
    def get_batch_items(
        db: Session,
        batch_id: int,
    ):

        return (

            db.query(ProductionItem)

            .filter(
                ProductionItem.production_batch_id == batch_id
            )

            .all()

        )
