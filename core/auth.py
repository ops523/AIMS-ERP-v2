from __future__ import annotations

import streamlit as st

from database import SessionLocal
from services.auth_service import AuthService


# =========================================================
# SESSION KEYS
# =========================================================

AUTHENTICATED = "authenticated"
USER_ID = "user_id"
USERNAME = "username"
FULL_NAME = "full_name"
ROLE = "role"
PRINTER_ID = "printer_id"


# =========================================================
# SESSION INITIALIZATION
# =========================================================

def initialize_auth_session() -> None:
    """
    Initialize authentication-related Streamlit session state.
    """

    if AUTHENTICATED not in st.session_state:
        st.session_state[AUTHENTICATED] = False

    if USER_ID not in st.session_state:
        st.session_state[USER_ID] = None

    if USERNAME not in st.session_state:
        st.session_state[USERNAME] = None

    if FULL_NAME not in st.session_state:
        st.session_state[FULL_NAME] = None

    if ROLE not in st.session_state:
        st.session_state[ROLE] = None

    if PRINTER_ID not in st.session_state:
        st.session_state[PRINTER_ID] = None


# =========================================================
# LOGIN
# =========================================================

def login(
    username: str,
    password: str,
) -> tuple[bool, str]:

    db = SessionLocal()

    try:

        result = AuthService.authenticate(
            db=db,
            username=username,
            password=password,
        )

        if not result.success:
            return False, result.message

        user = result.data

        # -------------------------------------------------
        # Store identity only
        # -------------------------------------------------

        st.session_state[AUTHENTICATED] = True
        st.session_state[USER_ID] = user.id
        st.session_state[USERNAME] = user.username
        st.session_state[FULL_NAME] = user.full_name
        st.session_state[ROLE] = user.role
        st.session_state[PRINTER_ID] = user.printer_id

        return True, result.message

    finally:

        db.close()


# =========================================================
# LOGOUT
# =========================================================

def logout() -> None:
    """
    Clear authentication state.
    """

    st.session_state[AUTHENTICATED] = False
    st.session_state[USER_ID] = None
    st.session_state[USERNAME] = None
    st.session_state[FULL_NAME] = None
    st.session_state[ROLE] = None
    st.session_state[PRINTER_ID] = None


# =========================================================
# AUTHENTICATION CHECK
# =========================================================

def is_authenticated() -> bool:

    return bool(
        st.session_state.get(
            AUTHENTICATED,
            False,
        )
    )


# =========================================================
# CURRENT USER
# =========================================================

def current_user() -> dict | None:

    if not is_authenticated():
        return None

    return {
        "id": st.session_state.get(USER_ID),
        "username": st.session_state.get(USERNAME),
        "full_name": st.session_state.get(FULL_NAME),
        "role": st.session_state.get(ROLE),
        "printer_id": st.session_state.get(PRINTER_ID),
    }
