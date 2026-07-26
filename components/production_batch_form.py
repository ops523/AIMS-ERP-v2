import streamlit as st

from database import SessionLocal

from repositories.printer_repository import (
    PrinterRepository,
)

from services.production_batch_service import (
    ProductionBatchService,
)


class ProductionBatchForm:

    @staticmethod
    def render():

        db = SessionLocal()

        printers = PrinterRepository.get_all(db)

        printer = st.selectbox(
            "Printer",
            printers,
            format_func=lambda x: x.printer_name,
        )

        remarks = st.text_area("Remarks")

        if st.button("Create Production Batch"):

            batch = ProductionBatchService.create(

                db=db,

                printer_id=printer.id,

                remarks=remarks,

            )

            db.commit()

            st.success(
                f"Batch {batch.batch_number} created successfully."
            )

            st.rerun()
