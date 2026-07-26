import streamlit as st

from database import SessionLocal

from repositories.campaign_repository import (
    CampaignRepository,
)

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

        campaigns = CampaignRepository.get_all(db)

        printers = PrinterRepository.get_all(db)

        campaign = st.selectbox(

            "Campaign",

            campaigns,

            format_func=lambda x: x.campaign_name,

        )

        printer = st.selectbox(

            "Printer",

            printers,

            format_func=lambda x: x.printer_name,

        )

        remarks = st.text_area("Remarks")

        if st.button("Create Batch"):

            batch = ProductionBatchService.create(

                db=db,

                campaign_id=campaign.id,

                printer_id=printer.id,

                remarks=remarks,

            )

            db.commit()

            st.success(

                f"Production Batch {batch.batch_number} created."

            )

            st.rerun()
