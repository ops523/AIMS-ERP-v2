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

            st.error(
                "Authentication required."
            )

            return

        db = get_session()

        try:

            st.subheader(
                "Step 4 : Select Printer"
            )

            role = user.get("role")
            user_printer_id = user.get("printer_id")

            total_planned_sqft = float(
                st.session_state.get(
                    "total_planned_sqft",
                    0.0,
                )
            )

            if total_planned_sqft <= 0:

                st.error(
                    (
                        "Production quantity has not been defined. "
                        "Please go back to Step 3 and select artwork "
                        "quantities."
                    )
                )

                if st.button("⬅ Back"):

                    st.session_state.wizard_step = 3
                    st.rerun()

                return

            st.info(
                (
                    f"Planned production for this batch: "
                    f"**{total_planned_sqft:,.2f} Sq Ft**"
                )
            )

            selected_printer = None

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
                    (
                        "Your account is restricted to the "
                        "assigned printer."
                    )
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

                selected_printer = printer

                # Store only the ID.
                st.session_state.selected_printer = (
                    printer.id
                )

            # -------------------------------------------------
            # ADMIN / OPERATIONS
            # -------------------------------------------------

            elif role in (
                ADMIN,
                OPERATIONS,
            ):

                printers = (
                    PrinterRepository.get_all(db)
                )

                # Safety filter: only active printers.
                printers = [
                    printer
                    for printer in printers
                    if printer.is_active
                ]

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

                option_names = list(
                    options.keys()
                )

                current_selection = (
                    st.session_state.get(
                        "selected_printer"
                    )
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

                selected_printer_id = (
                    options[selected]
                )

                selected_printer = next(
                    (
                        printer
                        for printer in printers
                        if printer.id
                        == selected_printer_id
                    ),
                    None,
                )

                if selected_printer is not None:

                    st.session_state.selected_printer = (
                        selected_printer.id
                    )

            else:

                st.error(
                    "You are not authorized to create "
                    "production batches."
                )

                return

            if selected_printer is None:

                st.error(
                    "Please select a printer."
                )

                return

            # -------------------------------------------------
            # SHIFT
            # -------------------------------------------------

            st.divider()

            st.markdown(
                "#### Production Shift"
            )

            day_capacity = float(
                selected_printer.print_capacity_day
                or 0
            )

            night_capacity = float(
                selected_printer.night_shift_capacity
                or 0
            )

            current_shift = st.session_state.get(
                "selected_shift",
                "DAY",
            )

            shift_options = [
                "DAY",
                "NIGHT",
            ]

            default_shift_index = (
                shift_options.index(current_shift)
                if current_shift in shift_options
                else 0
            )

            selected_shift = st.radio(
                "Shift",
                shift_options,
                index=default_shift_index,
                horizontal=True,
                format_func=lambda value: (
                    "☀️ DAY"
                    if value == "DAY"
                    else "🌙 NIGHT"
                ),
            )

            if selected_shift == "DAY":

                capacity = day_capacity

            else:

                capacity = night_capacity

            st.session_state.selected_shift = (
                selected_shift
            )

            st.session_state.printer_capacity = (
                capacity
            )

            # -------------------------------------------------
            # Capacity Information
            # -------------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Batch Requirement",
                    f"{total_planned_sqft:,.0f} Sq Ft",
                )

            with col2:

                st.metric(
                    "Shift Capacity",
                    f"{capacity:,.0f} Sq Ft",
                )

            with col3:

                balance = (
                    capacity
                    - total_planned_sqft
                )

                st.metric(
                    "Capacity Balance",
                    f"{balance:,.0f} Sq Ft",
                )

            if capacity <= 0:

                st.error(
                    (
                        f"{selected_shift} shift capacity is not "
                        "configured for this printer."
                    )
                )

            elif total_planned_sqft > capacity:

                st.warning(
                    (
                        f"This batch requires "
                        f"{total_planned_sqft:,.2f} Sq Ft, "
                        f"but the {selected_shift} shift capacity "
                        f"is only {capacity:,.2f} Sq Ft."
                    )
                )

                st.caption(
                    (
                        "You can go back and reduce the batch "
                        "quantity or select another shift/printer."
                    )
                )

            else:

                st.success(
                    (
                        f"Capacity check passed: "
                        f"{total_planned_sqft:,.2f} Sq Ft planned "
                        f"within {capacity:,.2f} Sq Ft capacity."
                    )
                )

            # -------------------------------------------------
            # Navigation
            # -------------------------------------------------

            st.divider()

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "⬅ Back",
                    use_container_width=True,
                ):

                    st.session_state.wizard_step = 3
                    st.rerun()

            with c2:

                if st.button(
                    "Next ➜",
                    type="primary",
                    use_container_width=True,
                ):

                    selected_printer_id = (
                        st.session_state.get(
                            "selected_printer"
                        )
                    )

                    selected_shift = (
                        st.session_state.get(
                            "selected_shift"
                        )
                    )

                    capacity = float(
                        st.session_state.get(
                            "printer_capacity",
                            0,
                        )
                    )

                    if selected_printer_id is None:

                        st.error(
                            "Please select a printer."
                        )

                    elif selected_shift not in (
                        "DAY",
                        "NIGHT",
                    ):

                        st.error(
                            "Please select a valid production shift."
                        )

                    elif capacity <= 0:

                        st.error(
                            (
                                f"{selected_shift} shift capacity "
                                "must be configured before "
                                "continuing."
                            )
                        )

                    elif total_planned_sqft > capacity:

                        st.error(
                            (
                                "Batch quantity exceeds the selected "
                                "printer's shift capacity. "
                                "Please reduce the quantity or "
                                "select another shift/printer."
                            )
                        )

                    else:

                        # A ProductionBatch has exactly ONE printer.
                        # No multi-printer state is created here.
                        st.session_state.wizard_step = 5

                        st.rerun()

        finally:

            db.close()