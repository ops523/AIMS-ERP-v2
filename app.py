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
# Initialize Database
# ---------------------------------------------------------

from config import DATABASE_URL

st.write("DATABASE:", DATABASE_URL)

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
)

initialize_auth_session()

# ---------------------------------------------------------
# Application Routing
# ---------------------------------------------------------

if not is_authenticated():

    render_login()

else:

    render_authenticated_shell()
