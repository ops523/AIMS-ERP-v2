from models.production_batch import ProductionBatch


class ProductionDashboardService:

    @staticmethod
    def statistics(db):

        batches = db.query(ProductionBatch).count()

        open_batches = (

            db.query(ProductionBatch)

            .filter(
                ProductionBatch.status != "COMPLETED"
            )

            .count()

        )

        completed = batches - open_batches

        return {

            "total_batches": batches,

            "open_batches": open_batches,

            "completed_batches": completed,

        }
