from models.production_item import ProductionItem

from repositories.production_item_repository import (
    ProductionItemRepository,
)


class ProductionItemService:

    @staticmethod
    def create(
        db,
        production_batch_id,
        artwork_id,
        planned_sqft,
    ):

        item = ProductionItem(

            production_batch_id=production_batch_id,

            artwork_id=artwork_id,

            planned_sqft=planned_sqft,

        )

        return ProductionItemRepository.create(
            db,
            item,
        )
