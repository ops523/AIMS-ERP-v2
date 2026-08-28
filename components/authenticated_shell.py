from __future__ import annotations

import streamlit as st

from core.auth import current_user, logout


def render_authenticated_shell() -> None:
    """
    Render the common authenticated application shell.

    Navigation itself is managed by app.py through st.navigation().
    This component is responsible only for the authenticated
    user's identity and logout control.
    """

    user = current_user()

    if user is None:
        return

    # -----------------------------------------------------
    # Sidebar - authenticated user
    # -----------------------------------------------------

    with st.sidebar:

        st.markdown("### AIMS ERP")

        st.caption(
            user["full_name"] or user["username"]
        )

        st.caption(
            f"Role: {user['role']}"
        )

        if user["printer_id"] is not None:

            st.caption(
                f"Printer ID: {user['printer_id']}"
            )

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True,
        ):

            logout()

            st.rerun()


def render_dashboard() -> None:
    """
    Render the default AIMS ERP dashboard.
    """

    user = current_user()

    if user is None:
        return

    st.title("🏢 AIMS ERP")

    st.caption(
        "Advertising Inventory Management System"
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Campaigns",
            "0",
        )

    with col2:
        st.metric(
            "Media Rolls",
            "0",
        )

    with col3:
        st.metric(
            "Printers",
            "0",
        )

    with col4:
        st.metric(
            "Warehouses",
            "0",
        )

    st.divider()

    st.success(
        f"Welcome, {user['full_name']}."
    )

    st.info(
        "Authentication is active."
    )
