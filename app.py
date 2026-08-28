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

from core.startup import startup

startup()

from database import SessionLocal
from models.user import User
from utils.security import verify_password

db = SessionLocal()

try:
    user = (
        db.query(User)
        .filter(User.username == "admin")
        .first()
    )

    st.write("ADMIN EXISTS:", user is not None)

    if user:
        st.write("ROLE:", user.role)
        st.write("ACTIVE:", user.is_active)
        st.write(
            "PASSWORD MATCH:",
            verify_password(
                "admin123",
                user.password_hash,
            ),
        )
finally:
    db.close()

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
