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


# =========================================================
# COOKIE CONTROLLER
# =========================================================

def _cookie_controller():
    """
    Return the single CookieController instance used by the
    authentication system.

    The controller is tied to a stable Streamlit session-state
    key. This is important because creating multiple controller
    instances with different keys can create multiple Streamlit
    component instances and interfere with cookie lifecycle.
    """

    from streamlit_cookies_controller import CookieController

    return CookieController(
        key=COOKIE_CONTROLLER_KEY,
    )


# =========================================================
# SESSION HELPERS
# =========================================================

def _initialize_session_state() -> None:
    """
    Initialize all authentication-related Streamlit session
    state values.
    """

    defaults = {
        AUTHENTICATED: False,
        USER_ID: None,
        USERNAME: None,
        FULL_NAME: None,
        ROLE: None,
        PRINTER_ID: None,
        AUTH_TOKEN: None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


def _clear_session_state() -> None:
    """
    Clear the current Streamlit authentication state.
    """

    st.session_state[AUTHENTICATED] = False
    st.session_state[USER_ID] = None
    st.session_state[USERNAME] = None
    st.session_state[FULL_NAME] = None
    st.session_state[ROLE] = None
    st.session_state[PRINTER_ID] = None
    st.session_state[AUTH_TOKEN] = None


def _set_authenticated_user(
    user,
    token: str,
) -> None:
    """
    Store the authenticated user in Streamlit session state.
    """

    st.session_state[AUTHENTICATED] = True
    st.session_state[USER_ID] = user.id
    st.session_state[USERNAME] = user.username
    st.session_state[FULL_NAME] = user.full_name
    st.session_state[ROLE] = user.role
    st.session_state[PRINTER_ID] = user.printer_id
    st.session_state[AUTH_TOKEN] = token


# =========================================================
# BROWSER COOKIE
# =========================================================

def _get_session_cookie() -> str | None:
    """
    Read the persistent authentication cookie using the same
    CookieController instance/key used for writing the cookie.

    We intentionally do not call controller.refresh() here.

    CookieController maintains its browser-cookie cache in
    Streamlit session state. Calling refresh() during every
    authentication initialization can create another component
    instance and cause StreamlitDuplicateElementKey errors.
    """

    try:

        controller = _cookie_controller()

        token = controller.get(
            COOKIE_NAME,
        )

        if not token:
            return None

        return str(token)

    except (
        TypeError,
        AttributeError,
        RuntimeError,
        KeyError,
    ):
        return None


def _set_session_cookie(
    token: str,
) -> None:
    """
    Persist the server-side authentication token in the browser.

    The cookie is:

    - available to the entire application path
    - HTTPS-only
    - SameSite=Lax
    - valid for 7 days
    """

    if not token:
        return

    try:

        controller = _cookie_controller()

        controller.set(
            COOKIE_NAME,
            token,
            path="/",
            max_age=7 * 24 * 60 * 60,
            secure=True,
            same_site="lax",
        )

    except (
        TypeError,
        AttributeError,
        RuntimeError,
    ):
        pass


def _remove_session_cookie() -> None:
    """
    Remove the persistent authentication cookie.
    """

    try:

        controller = _cookie_controller()

        controller.remove(
            COOKIE_NAME,
            path="/",
            secure=True,
            same_site="lax",
        )

    except (
        TypeError,
        AttributeError,
        RuntimeError,
        KeyError,
    ):
        pass


# =========================================================
# SESSION INITIALIZATION
# =========================================================

def initialize_auth_session() -> None:
    """
    Initialize authentication state and restore a persistent
    login session from the browser cookie.
    """

    _initialize_session_state()

    # -----------------------------------------------------
    # Already authenticated in this Streamlit session.
    # -----------------------------------------------------

    if is_authenticated():
        return

    # -----------------------------------------------------
    # Restore persistent browser session.
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

            _remove_session_cookie()
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
    """
    Authenticate a user and create a persistent server-side
    session.
    """

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

        # -------------------------------------------------
        # Persist token in browser.
        # -------------------------------------------------

        _set_session_cookie(token)

        # -------------------------------------------------
        # Authenticate current Streamlit session immediately.
        # -------------------------------------------------

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
    Invalidate the persistent server-side session, remove the
    browser cookie and clear Streamlit session state.
    """

    token = st.session_state.get(
        AUTH_TOKEN,
    )

    db = SessionLocal()

    try:

        if token:

            UserSessionService.invalidate(
                db=db,
                token=token,
            )

    finally:
        db.close()

    # -----------------------------------------------------
    # Remove browser persistence.
    # -----------------------------------------------------

    _remove_session_cookie()

    # -----------------------------------------------------
    # Clear current Streamlit session.
    # -----------------------------------------------------

    _clear_session_state()


# =========================================================
# AUTHENTICATION CHECK
# =========================================================

def is_authenticated() -> bool:
    """
    Return whether the current Streamlit session is authenticated.
    """

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
    """
    Return the currently authenticated user information.
    """

    if not is_authenticated():
        return None

    return {
        "id": st.session_state.get(USER_ID),
        "username": st.session_state.get(USERNAME),
        "full_name": st.session_state.get(FULL_NAME),
        "role": st.session_state.get(ROLE),
        "printer_id": st.session_state.get(PRINTER_ID),
    }