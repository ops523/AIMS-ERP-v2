from sqlalchemy.orm import Session

from models.media_product import MediaProduct


class MediaProductRepository:

    @staticmethod
    def get_all(db):

        return (

            db.query(MediaProduct)

            .filter(

                MediaProduct.is_active == True

            )

            .order_by(

                MediaProduct.product_name

            )

            .all()

        )
