import pandas as pd
import streamlit as st

from database import SessionLocal

from repositories.production_batch_repository import (
    ProductionBatchRepository,
)


class ProductionBatchList:

    @staticmethod
    def render():

        db = SessionLocal()

        batches = ProductionBatchRepository.get_all(db)

        rows = []

        for batch in batches:

            rows.append(

                {

                    "Batch": batch.batch_number,

                    "Campaign": batch.campaign.campaign_name,

                    "Printer": batch.printer.printer_name,

                    "Status": batch.status,

                }

            )

        st.data_editor(

            pd.DataFrame(rows),

            disabled=True,

            use_container_width=True,

        )
