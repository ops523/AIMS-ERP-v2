import pandas as pd
import streamlit as st

from database import SessionLocal

from services.roll_inventory_service import (
    RollInventoryService,
)

from components.page_header import PageHeader


PageHeader.render(

    "Roll Inventory",

    "Current Media Roll Stock",

    "📦",

)

db = SessionLocal()

search = st.text_input(
    "Search Roll Code"
)

rolls = RollInventoryService.search(
    db,
    search,
)

rows = []

for roll in rolls:

    rows.append(

        {

            "Roll Code": roll.roll_code,

            "Width": roll.width_ft,

            "Length": roll.length_ft,

            "Total Sq Ft": roll.total_sqft,

            "Balance Sq Ft": roll.balance_sqft,

        }

    )

st.dataframe(

    pd.DataFrame(rows),

    use_container_width=True,

)
