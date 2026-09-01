from __future__ import annotations

import streamlit as st

from database import get_session

from models.printer import Printer

from constants.roles import (
    ADMIN,
    OPERATIONS,
    PRINTER,
)

from core.auth import current_user

from repositories.printer_repository import (
    PrinterRepository,
)


class StepPrinter:

    @staticmethod
    def render():

        user = current_user()

        if user is None:
            st.error("Authentication required.")
            return

        db = get_session()

        try:

            st.subheader("Step 4 : Select Printer")

            role = user.get("role")
            user_printer_id = user.get("printer_id")

            # -------------------------------------------------
            # PRINTER USER
            # -------------------------------------------------

            if role == PRINTER:

                if user_printer_id is None:

                    st.error(
                        "Your account is not assigned to a printer."
                    )

                    return

                printer = (
                    db.query(Printer)
                    .filter(
                        Printer.id == user_printer_id
                    )
                    .first()
                )

                if printer is None:

                    st.error(
                        "Your assigned printer could not be found."
                    )

                    return

                if not printer.is_active:

                    st.error(
                        "Your assigned printer is inactive."
                    )

                    return

                st.info(
                    "Your account is restricted to the assigned printer."
                )

                st.markdown(
                    f"### 🖨️ {printer.printer_name}"
                )

                st.caption(
                    f"Printer Code: {printer.printer_code}"
                )

                if printer.city or printer.state:

                    location = ", ".join(
                        part
                        for part in [
                            printer.city,
                            printer.state,
                        ]
                        if part
                    )

                    st.caption(
                        f"Location: {location}"
                    )

                st.caption(
                    f"Daily Capacity: "
                    f"{printer.print_capacity_day:,.0f} Sq Ft"
                )

                st.session_state.selected_printer = (
                    printer.id
                )

            # -------------------------------------------------
            # ADMIN / OPERATIONS
            # -------------------------------------------------

            else:

                printers = (
                    PrinterRepository.get_all(db)
                )

                if not printers:

                    st.warning(
                        "No active printers available."
                    )

                    return

                options = {
                    (
                        f"{printer.printer_name} "
                        f"({printer.printer_code})"
                    ): printer.id
                    for printer in printers
                }

                current_selection = (
                    st.session_state.get(
                        "selected_printer"
                    )
                )

                option_names = list(
                    options.keys()
                )

                default_index = 0

                if current_selection is not None:

                    for index, printer_id in enumerate(
                        options.values()
                    ):

                        if printer_id == current_selection:

                            default_index = index
                            break

                selected = st.selectbox(
                    "Printer",
                    option_names,
                    index=default_index,
                )

                st.session_state.selected_printer = (
                    options[selected]
                )

            # -------------------------------------------------
            # NAVIGATION
            # -------------------------------------------------

            st.divider()

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "⬅ Back",
                    width="stretch",
                ):

                    st.session_state.wizard_step = 3

                    st.rerun()

            with c2:

                if st.button(
                    "Next ➜",
                    type="primary",
                    width="stretch",
                ):

                    selected_printer = (
                        st.session_state.get(
                            "selected_printer"
                        )
                    )

                    if selected_printer is None:

                        st.error(
                            "Please select a printer."
                        )

                    else:

                        st.session_state.wizard_step = 5

                        st.rerun()

        finally:

            db.close()