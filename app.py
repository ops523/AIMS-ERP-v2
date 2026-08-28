import streamlit as st

# ---------------------------------------------------------
# Streamlit Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AIMS ERP",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme_loader import load_theme

load_theme()

# ---------------------------------------------------------
# Application Startup
# ---------------------------------------------------------

from core.startup import startup

startup()

# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

from core.auth import (
    initialize_auth_session,
    is_authenticated,
)

from components.login import render_login
from components.authenticated_shell import (
    render_authenticated_shell,
    render_dashboard,
)

initialize_auth_session()

# ---------------------------------------------------------
# Navigation
#
# IMPORTANT:
# st.navigation() must be called on every run.
#
# This prevents Streamlit from automatically exposing the
# files inside pages/ before authentication has completed.
# ---------------------------------------------------------

from core.navigation import get_navigation_for_role


def build_navigation():
    """
    Build the application navigation based on authentication
    and the authenticated user's role.
    """

    # -----------------------------------------------------
    # Logged-out navigation
    # -----------------------------------------------------

    if not is_authenticated():

        return {
            "AIMS ERP": [
                st.Page(
                    render_login,
                    title="Login",
                    icon="🔐",
                    default=True,
                )
            ]
        }

    # -----------------------------------------------------
    # Logged-in navigation
    # -----------------------------------------------------

    role = st.session_state.get("role")

    navigation_items = get_navigation_for_role(role)

    pages = {
        "AIMS ERP": [
            st.Page(
                render_dashboard,
                title="App",
                icon="🏢",
                default=True,
            )
        ]
    }

    for item in navigation_items:

        pages["AIMS ERP"].append(
            st.Page(
                item.page,
                title=item.label,
                icon=item.icon,
            )
        )

    return pages


# ---------------------------------------------------------
# Build Navigation
# ---------------------------------------------------------

pages = build_navigation()

pg = st.navigation(
    pages,
    position="sidebar",
)

# ---------------------------------------------------------
# Authenticated Shell
#
# Render the identity/logout section only when authenticated.
# ---------------------------------------------------------

if is_authenticated():

    render_authenticated_shell()

# ---------------------------------------------------------
# Run Selected Page
# ---------------------------------------------------------

pg.run()