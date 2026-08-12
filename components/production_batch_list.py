import streamlit as st

from database import get_session

from repositories.production_batch_repository import (
    ProductionBatchRepository,
)


class ProductionBatchList:

    @staticmethod
    def render():

        db = get_session()

        try:

            batches = ProductionBatchRepository.list(db)

            st.subheader("Production Batches")

            if not batches:

                st.info("No Production Batches Found")

                return

            rows = []

            for batch in batches:

                rows.append(
                    {
                        "Batch": batch.batch_number,
                        "Printer": batch.printer.printer_name
                        if batch.printer else "",
                        "Status": batch.status,
                        "Planned Sq Ft": batch.total_planned_sqft,
                        "Printed Sq Ft": batch.total_printed_sqft,
                        "Completion %": batch.completion_percentage,
                    }
                )

            st.dataframe(
                rows,
                width="stretch",
                hide_index=True,
            )

        finally:
            db.close()
