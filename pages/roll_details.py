import streamlit as st

from database import SessionLocal

from services.roll_details_service import (
    RollDetailsService,
)

from components.page_header import PageHeader


PageHeader.render(
    "Roll Details",
    "Media Roll Information",
    "📦",
)

db = SessionLocal()

roll_id = st.number_input(
    "Roll ID",
    min_value=1,
    step=1,
)

if st.button("Load Roll"):

    roll = RollDetailsService.get(
        db,
        roll_id,
    )

    if roll is None:

        st.error("Roll not found.")

    else:

        c1, c2 = st.columns(2)

        with c1:

            st.write("### General")

            st.write(f"**Roll Code:** {roll.roll_code}")
            st.write(f"**Width:** {roll.width_ft}")
            st.write(f"**Length:** {roll.length_ft}")

        with c2:

            st.write("### Inventory")

            st.write(f"**Total Sq Ft:** {roll.total_sqft}")
            st.write(f"**Balance Sq Ft:** {roll.balance_sqft}")
            st.write(f"**Warehouse ID:** {roll.warehouse_id}")
