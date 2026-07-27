import streamlit as st

from database import SessionLocal

from components.page_header import PageHeader

from components.production_dashboard import ProductionDashboard

from components.production_batch_form import (
    ProductionBatchForm,
)

from components.production_batch_list import (
    ProductionBatchList,
)

ProductionDashboard.render()

st.divider()

ProductionBatchForm.render()

st.divider()

ProductionBatchList.render()
