import streamlit as st

from repositories.production_batch_repository import (
    ProductionBatchRepository,
)


def show(db):

    batches = ProductionBatchRepository.get_all(db)

    st.subheader("Production Batches")

    if not batches:

        st.info("No Production Batches Found")

        return

    rows = []

    for batch in batches:

        rows.append(
            {
                "Batch": batch.batch_number,
                "Campaign": batch.campaign_name,
                "Printer": batch.printer.printer_name,
                "Status": batch.status,
                "Target Sqft": batch.total_sqft,
                "Printed": batch.printed_sqft,
            }
        )

    st.dataframe(
        rows,
        width="stretch",
    )
