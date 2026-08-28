from __future__ import annotations

import streamlit as st

from database import SessionLocal
from services.auth_service import AuthService
from services.user_session_service import UserSessionService


# =========================================================
# SESSION KEYS
# =========================================================

AUTHENTICATED = "authenticated"
USER_ID = "user_id"
USERNAME = "username"
FULL_NAME = "full_name"
ROLE = "role"
PRINTER_ID = "printer_id"
AUTH_TOKEN = "auth_token"

COOKIE_NAME = "aims_erp_session"


# =========================================================
# COOKIE CONTROLLER
# =========================================================

def _cookie_controller():
    from streamlit_cookies_controller import CookieController

    return CookieController()


def _get_session_cookie() -> str | None:
    """
    Safely read the persistent authentication cookie.

    The cookie controller is client-side and may not have
    received browser cookies during the first script execution.
    """

    try:

        controller = _cookie_controller()

        token = controller.get(COOKIE_NAME)

        if token:
            st.session_state["_cookie_ready"] = True
            return token

        # The controller may legitimately have no cookie.
        # Mark it ready after a successful read.
        st.session_state["_cookie_ready"] = True

        return None

    except (TypeError, AttributeError):

        return None


# =========================================================
# SESSION HELPERS
# =========================================================

def _clear_session_state() -> None:

    st.session_state[AUTHENTICATED] = False
    st.session_state[USER_ID] = None
    st.session_state[USERNAME] = None
    st.session_state[FULL_NAME] = None
    st.session_state[ROLE] = None
    st.session_state[PRINTER_ID] = None
    st.session_state[AUTH_TOKEN] = None


def _set_authenticated_user(user, token: str) -> None:

    st.session_state[AUTHENTICATED] = True
    st.session_state[USER_ID] = user.id
    st.session_state[USERNAME] = user.username
    st.session_state[FULL_NAME] = user.full_name
    st.session_state[ROLE] = user.role
    st.session_state[PRINTER_ID] = user.printer_id
    st.session_state[AUTH_TOKEN] = token


# =========================================================
# SESSION INITIALIZATION
# =========================================================

def initialize_auth_session() -> None:
    """
    Initialize authentication state and restore a persistent
    login session from the browser cookie when necessary.
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

    if AUTH_TOKEN not in st.session_state:
        st.session_state[AUTH_TOKEN] = None

    # Already authenticated in this Streamlit session.
    if is_authenticated():
        return

    token = _get_session_cookie()

    if not token:
        return

    db = SessionLocal()

    try:

        user = UserSessionService.get_user(
            db=db,
            token=token,
        )

        if user is None:

            try:
                controller.remove(COOKIE_NAME)
            except Exception:
                pass

            _clear_session_state()
            return

        _set_authenticated_user(
            user=user,
            token=token,
        )

    finally:
        db.close()


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

        token = UserSessionService.create(
            db=db,
            user=user,
        )

        controller = _cookie_controller()

        controller.set(
            COOKIE_NAME,
            token,
        )

        _set_authenticated_user(
            user=user,
            token=token,
        )

        return True, result.message

    finally:
        db.close()


# =========================================================
# LOGOUT
# =========================================================

def logout() -> None:
    """
    Invalidate the persistent server-side session,
    remove the browser cookie and clear Streamlit state.
    """

    token = st.session_state.get(AUTH_TOKEN)

    db = SessionLocal()

    try:

        UserSessionService.invalidate(
            db=db,
            token=token,
        )

    finally:
        db.close()

    try:
        controller = _cookie_controller()
        controller.remove(COOKIE_NAME)
    except Exception:
        pass

    _clear_session_state()


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
