import streamlit as st

from database import SessionLocal

from components.page_header import PageHeader

from components.production_batch_form import (
    ProductionBatchForm,
)

from components.production_batch_list import (
    ProductionBatchList,
)

from services.production_batch_service import (
    ProductionBatchService,
)

from services.production_item_service import (
    ProductionItemService,
)


db = SessionLocal()


PageHeader.render(
    title="Production Workspace",
    subtitle="Production Planning & Printing",
    icon="🖨️",
)

st.info(
    "Manage the complete production lifecycle from a single workspace."
)

tab_batch, tab_items, tab_rolls, tab_printing = st.tabs(
    [
        "Production Batch",
        "Production Items",
        "Roll Assignment",
        "Printing Progress",
    ]
)


# --------------------------------------------------------
# Production Batch
# --------------------------------------------------------

with tab_batch:

    st.subheader("Create Production Batch")

    ProductionBatchForm.render()

    st.divider()

    st.subheader("Existing Production Batches")

    ProductionBatchList.render()


# --------------------------------------------------------
# Production Items
# --------------------------------------------------------

with tab_items:

    st.info(
        "Production Items module will be added in Sprint 7.4."
    )


# --------------------------------------------------------
# Roll Assignment
# --------------------------------------------------------

with tab_rolls:

    st.info(
        "Roll Assignment module will be added in Sprint 7.5."
    )


# --------------------------------------------------------
# Printing Progress
# --------------------------------------------------------

with tab_printing:

    st.info(
        "Printing Progress module will be added in Sprint 7.6."
    )
