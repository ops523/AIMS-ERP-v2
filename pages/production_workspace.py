import streamlit as st

from components.production_batch_list import ProductionBatchList

from database import SessionLocal

from components.page_header import PageHeader

from services.production_batch_service import (
    ProductionBatchService,
)

from services.production_item_service import (
    ProductionItemService,
)

PageHeader.render(

    "Production Workspace",

    "Production Planning & Printing",

    "🖨️",

)

db = SessionLocal()

st.info(
    "This workspace will manage the complete production lifecycle."
)

tab1, tab2, tab3, tab4 = st.tabs(

    [

        "Batch",

        "Items",

        "Roll Assignment",

        "Printing",

    ]

)

with tab1:

    from components.production_batch_form import (
    ProductionBatchForm,
    )

ProductionBatchForm.render()

st.divider()

ProductionBatchList.render()

with tab2:

    st.subheader("Production Items")

with tab3:

    st.subheader("Assign Media Rolls")

with tab4:

    st.subheader("Printing Progress")
