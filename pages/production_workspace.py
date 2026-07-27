import streamlit as st

from components.production_dashboard import ProductionDashboard
from components.production_batch_wizard import ProductionBatchWizard
from components.production_batch_list import ProductionBatchList

ProductionDashboard.render()

st.divider()

ProductionBatchWizard.render()

st.divider()

ProductionBatchList.render()
