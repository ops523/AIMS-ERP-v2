import streamlit as st

from core.startup import startup

startup()

from components.production_dashboard import ProductionDashboard
from components.production_batch_wizard import ProductionBatchWizard
from components.production_batch_list import ProductionBatchList

st.title("🖨️ Production")

dashboard_tab, create_tab, active_tab = st.tabs(
    [
        "📊 Dashboard",
        "➕ Create Batch",
        "📋 Active Batches",
    ]
)

with dashboard_tab:

    ProductionDashboard.render()

with create_tab:

    ProductionBatchWizard.render()

with active_tab:

    ProductionBatchList.render()
