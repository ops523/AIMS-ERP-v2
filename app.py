from __future__ import annotations

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
# Authentication Gate
# ---------------------------------------------------------

if not is_authenticated():

    render_login()

    st.stop()

# ---------------------------------------------------------
# Authenticated Shell
# ---------------------------------------------------------

render_authenticated_shell()

# ---------------------------------------------------------
# Role-Based Navigation
# ---------------------------------------------------------

from core.navigation import get_navigation_for_role

user = st.session_state.get("role")

navigation_items = get_navigation_for_role(user)

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

# ---------------------------------------------------------
# Run Navigation
# ---------------------------------------------------------

pg = st.navigation(
    pages,
    position="sidebar",
)

pg.run()
