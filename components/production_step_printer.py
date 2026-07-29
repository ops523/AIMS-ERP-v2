import streamlit as st

from database import SessionLocal
from repositories.printer_repository import PrinterRepository


def render():

    db = SessionLocal()

    try:

        printers = PrinterRepository.get_all(db)

        options = {
            p.printer_name: p
            for p in printers
        }

        selected = st.selectbox(
            "Select Printer",
            list(options.keys()),
        )

        printer = options[selected]

        st.session_state.selected_printer = printer

        shift = st.radio(
            "Printing Shift",
            ["DAY", "NIGHT"],
            horizontal=True,
        )

        st.session_state.selected_shift = shift

        if shift == "DAY":
            capacity = printer.print_capacity_day
        else:
            capacity = printer.night_shift_capacity

        st.metric(
            "Available Capacity",
            f"{capacity:,.0f} Sq Ft",
        )

    finally:
        db.close()

    st.divider()

    left, right = st.columns(2)

    with left:
        if st.button("⬅ Back"):
            st.session_state.production_step = 1
            st.rerun()

    with right:
        if st.button("Next ➜"):
            st.session_state.production_step = 3
            st.rerun()
