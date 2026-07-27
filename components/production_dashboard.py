import streamlit as st

from database import get_session

from repositories.production_batch_repository import (
    ProductionBatchRepository,
)

from repositories.printer_repository import (
    PrinterRepository,
)


class ProductionDashboard:

    @staticmethod
    def render():

        db = get_session()

        batches = ProductionBatchRepository.get_all(db)

        printers = PrinterRepository.get_all(db)

        st.subheader("Production Dashboard")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Production Batches",
            len(batches),
        )

        c2.metric(
            "Printers",
            len(printers),
        )

        c3.metric(
            "Active Printing",
            sum(
                1
                for b in batches
                if b.status == "PRINTING"
            ),
        )

        c4.metric(
            "Completed",
            sum(
                1
                for b in batches
                if b.status == "COMPLETED"
            ),
        )

        st.divider()

        st.dataframe(
            [
                {
                    "Batch": b.batch_number,
                    "Printer": b.printer.printer_name,
                    "Status": b.status,
                }
                for b in batches
            ],
            width="stretch",
        )

        db.close()
