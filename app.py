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

from core.navigation import (
    NAVIGATION_ITEMS,
    get_navigation_for_role,
)

# ---------------------------------------------------------
# Build ALL pages on EVERY run
#
# IMPORTANT:
# Do not make page registration dependent on authentication.
# Streamlit needs every route registered during the initial
# execution of the entrypoint to support direct URLs/refresh.
# ---------------------------------------------------------

dashboard_page = st.Page(
    render_dashboard,
    title="App",
    icon="🏢",
    default=True,
)

page_objects = {
    "app": dashboard_page,
}

for item in NAVIGATION_ITEMS:

    page_objects[item.page] = st.Page(
        item.page,
        title=item.label,
        icon=item.icon,
    )

all_pages = [
    dashboard_page,
]

all_pages.extend(
    page_objects[item.page]
    for item in NAVIGATION_ITEMS
)

# ---------------------------------------------------------
# Register the complete router.
#
# Navigation UI is intentionally hidden. We render our own
# role-aware sidebar navigation below.
# ---------------------------------------------------------

pg = st.navigation(
    all_pages,
    position="hidden",
)

# ---------------------------------------------------------
# Initialize / restore authentication
# ---------------------------------------------------------

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

user = st.session_state.get("role")

navigation_items = get_navigation_for_role(
    user
)

render_authenticated_shell(
    navigation_items=navigation_items,
    page_objects=page_objects,
)

# ---------------------------------------------------------
# Run the selected page
# ---------------------------------------------------------

pg.run()