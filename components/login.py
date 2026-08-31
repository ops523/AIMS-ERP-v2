from __future__ import annotations

import streamlit as st

from core.auth import login


def render_login() -> None:

    st.title("🏢 AIMS ERP")

    st.caption(
        "Advertising Inventory Management System"
    )

    st.divider()

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.subheader("Sign In")

        with st.form("login_form"):

            username = st.text_input(
                "Username",
                autocomplete="username",
            )

            password = st.text_input(
                "Password",
                type="password",
                autocomplete="current-password",
            )

            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )

        if submitted:

            success, message = login(
                username=username,
                password=password,
            )

            if success:

                st.success(message)
                st.rerun()
                
            else:

                st.error(message)
