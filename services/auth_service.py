from __future__ import annotations

from sqlalchemy.orm import Session

from models.user import User

from services.service_result import ServiceResult

from utils.security import verify_password


class AuthService:

    # =========================================================
    # AUTHENTICATE
    # =========================================================

    @staticmethod
    def authenticate(
        db: Session,
        username: str,
        password: str,
    ) -> ServiceResult:

        username = (username or "").strip()

        if not username:
            return ServiceResult.fail(
                "Username and password are required."
            )

        if not password:
            return ServiceResult.fail(
                "Username and password are required."
            )

        # -----------------------------------------------------
        # Find user
        # -----------------------------------------------------

        user = (
            db.query(User)
            .filter(
                User.username == username,
            )
            .first()
        )

        # Do not reveal whether the username exists.
        if user is None:
            return ServiceResult.fail(
                "Invalid username or password."
            )

        # -----------------------------------------------------
        # Active account check
        # -----------------------------------------------------

        if not user.is_active:
            return ServiceResult.fail(
                "This account is inactive."
            )

        # -----------------------------------------------------
        # Password verification
        # -----------------------------------------------------

        if not verify_password(
            password,
            user.password_hash,
        ):
            return ServiceResult.fail(
                "Invalid username or password."
            )

        # -----------------------------------------------------
        # Authentication successful
        # -----------------------------------------------------

        return ServiceResult.ok(
            data=user,
            message="Authentication successful.",
        )
