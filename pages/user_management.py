from __future__ import annotations

import streamlit as st

from constants.roles import (
    ADMIN,
    OPERATIONS,
    WAREHOUSE,
    PRINTER,
    DISPATCH,
    VIEWER,
)

from core.authorization import require_permission
from database import SessionLocal
from models.printer import Printer
from models.user import User
from services.user_service import UserService


# =========================================================
# AUTHORIZATION
# =========================================================

role = st.session_state.get("role")

require_permission(
    role,
    "users.view",
)


# =========================================================
# PAGE HEADER
# =========================================================

st.title("User Management")
st.caption(
    "Manage AIMS ERP users and printer login accounts."
)


# =========================================================
# DATABASE
# =========================================================

db = SessionLocal()


try:

    # =====================================================
    # USERS
    # =====================================================

    st.subheader("Users")

    users = (
        db.query(User)
        .order_by(User.username)
        .all()
    )

    if users:

        user_rows = []

        for user in users:

            printer_name = ""

            if user.printer_id:

                printer = (
                    db.query(Printer)
                    .filter(
                        Printer.id == user.printer_id
                    )
                    .first()
                )

                if printer:
                    printer_name = printer.printer_name

            user_rows.append(
                {
                    "Username": user.username,
                    "Name": user.full_name,
                    "Role": user.role,
                    "Printer": printer_name,
                    "Active": user.is_active,
                }
            )

        st.dataframe(
            user_rows,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No users found.")


    # =====================================================
    # ADMIN ACTIONS
    # =====================================================

    if role != ADMIN:

        st.stop()

    st.divider()

    st.subheader("Printer Login Account")

    tab_create, tab_reset = st.tabs(
        [
            "Create Printer Account",
            "Reset Password",
        ]
    )


    # =====================================================
    # CREATE PRINTER ACCOUNT
    # =====================================================

    with tab_create:

        printers = (
            db.query(Printer)
            .filter(
                Printer.is_active.is_(True)
            )
            .order_by(Printer.printer_name)
            .all()
        )

        if not printers:

            st.warning(
                "No active printers are available."
            )

        else:

            printer_options = {
                f"{p.printer_code} - {p.printer_name}": p.id
                for p in printers
            }

            with st.form(
                "create_printer_account"
            ):

                username = st.text_input(
                    "Username"
                )

                full_name = st.text_input(
                    "Full Name"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                )

                selected_printer = st.selectbox(
                    "Printer",
                    list(
                        printer_options.keys()
                    ),
                )

                submitted = st.form_submit_button(
                    "Create Printer Account",
                    type="primary",
                )

            if submitted:

                result = (
                    UserService.create_printer_account(
                        db=db,
                        username=username,
                        password=password,
                        full_name=full_name,
                        printer_id=printer_options[
                            selected_printer
                        ],
                    )
                )

                if result.success:

                    st.success(
                        result.message
                    )

                    st.rerun()

                else:

                    st.error(
                        result.message
                    )


    # =====================================================
    # RESET PASSWORD
    # =====================================================

    with tab_reset:

        resettable_users = (
            db.query(User)
            .filter(
                User.is_active.is_(True)
            )
            .order_by(User.username)
            .all()
        )

        if not resettable_users:

            st.info("No active users found.")

        else:

            user_options = {
                f"{u.username} - {u.full_name}": u.id
                for u in resettable_users
            }

            with st.form(
                "reset_user_password"
            ):

                selected_user = st.selectbox(
                    "User",
                    list(
                        user_options.keys()
                    ),
                )

                new_password = st.text_input(
                    "New Password",
                    type="password",
                )

                submitted = st.form_submit_button(
                    "Reset Password",
                )

            if submitted:

                result = (
                    UserService.reset_password(
                        db=db,
                        user_id=user_options[
                            selected_user
                        ],
                        new_password=new_password,
                    )
                )

                if result.success:

                    st.success(
                        result.message
                    )

                else:

                    st.error(
                        result.message
                    )

finally:

    db.close()
