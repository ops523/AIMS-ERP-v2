import streamlit as st

# ---------------------------------------------------------
# Streamlit Configuration (Must be the first Streamlit call)
# ---------------------------------------------------------

st.set_page_config(
    page_title="AIMS ERP",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme_loader import load_theme

load_theme()

# ---------------------------------------------------------
# Initialize Database
# ---------------------------------------------------------

from init_db import initialize_database

initialize_database()

# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

st.title("🏢 AIMS ERP")
st.caption("Advertising Inventory Management System")

st.divider()

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Campaigns",
        value="0"
    )

with col2:
    st.metric(
        label="Media Rolls",
        value="0"
    )

with col3:
    st.metric(
        label="Printers",
        value="0"
    )

with col4:
    st.metric(
        label="Warehouses",
        value="0"
    )

st.divider()

left, right = st.columns([2, 1])

with left:

    st.subheader("Welcome")

    st.info(
        """
AIMS ERP has been initialized successfully.

Modules currently under development:

- Campaign Import Wizard
- Media Roll Inventory
- Printing Production
- Packaging
- Dispatch Planning
- QR Code Tracking
- Reports & Analytics
"""
    )

with right:

    st.subheader("System Status")

    st.success("✅ Database Connected")
    st.success("✅ Models Loaded")
    st.success("✅ Initialization Complete")

st.divider()

st.subheader("Current Version")

st.write("Sprint 3 - Campaign Import Wizard Development")
