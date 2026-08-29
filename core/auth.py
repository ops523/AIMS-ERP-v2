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

COOKIE_CONTROLLER_KEY = "aims_erp_cookie_controller"
COOKIE_READY = "aims_erp_cookie_ready"


# =========================================================
# COOKIE CONTROLLER
# =========================================================

def _cookie_controller():
    from streamlit_cookies_controller import CookieController

    return CookieController(
        key=COOKIE_CONTROLLER_KEY,
    )


def _get_session_cookie() -> str | None:
    """
    Safely retrieve the persistent authentication cookie.

    streamlit-cookies-controller loads browser cookies through
    a Streamlit component. The cookie cache may not be populated
    during the first script execution, so refresh the controller
    before reading the cookie.
    """

    try:

        controller = _cookie_controller()

        # Refresh the browser cookie cache.
        controller.refresh()

        token = controller.get(COOKIE_NAME)

        st.session_state[COOKIE_READY] = True

        if token:
            return str(token)

        return None

    except (TypeError, AttributeError, RuntimeError):

        # The component may not yet be initialized on the first
        # Streamlit execution. Do not crash the application.
        st.session_state[COOKIE_READY] = False

        return None


# =========================================================
# SESSION HELPERS
# =========================================================

def _initialize_session_state() -> None:

    defaults = {
        AUTHENTICATED: False,
        USER_ID: None,
        USERNAME: None,
        FULL_NAME: None,
        ROLE: None,
        PRINTER_ID: None,
        AUTH_TOKEN: None,
        COOKIE_READY: False,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


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

    _initialize_session_state()

    # -----------------------------------------------------
    # Already authenticated in this Streamlit session.
    # -----------------------------------------------------

    if is_authenticated():
        return

    # -----------------------------------------------------
    # Try to restore persistent browser session.
    # -----------------------------------------------------

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

            # Invalid/expired server-side session.
            # Remove the browser cookie as well.
            try:
                controller = _cookie_controller()
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

        # Explicitly make the authentication cookie persistent.
        controller.set(
            COOKIE_NAME,
            token,
            path="/",
            max_age=7 * 24 * 60 * 60,
            same_site="lax",
            secure=True,
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

        controller.remove(
            COOKIE_NAME,
            path="/",
            same_site="lax",
            secure=True,
        )

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