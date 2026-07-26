from datetime import datetime

from sqlalchemy.orm import Session

from models.production_batch import ProductionBatch


class NumberGenerator:

    @staticmethod
    def production_batch_number(
        db: Session,
    ):

        today = datetime.now().strftime("%Y%m%d")

        prefix = f"PB-{today}-"

        last = (
            db.query(ProductionBatch)
            .filter(
                ProductionBatch.batch_number.like(
                    f"{prefix}%"
                )
            )
            .order_by(
                ProductionBatch.batch_number.desc()
            )
            .first()
        )

        if last:

            number = int(
                last.batch_number.split("-")[-1]
            ) + 1

        else:

            number = 1

        return f"{prefix}{number:03d}"
