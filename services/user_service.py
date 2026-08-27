from __future__ import annotations

from sqlalchemy.orm import Session

from constants.roles import PRINTER
from models.printer import Printer
from models.user import User

from services.service_result import ServiceResult
from services.transaction_service import TransactionService

from utils.security import hash_password


class UserService:

    # =========================================================
    # CREATE PRINTER ACCOUNT
    # =========================================================

    @staticmethod
    def create_printer_account(
        db: Session,
        username: str,
        password: str,
        full_name: str,
        printer_id: int,
    ) -> ServiceResult:

        # -----------------------------------------------------
        # Basic validation
        # -----------------------------------------------------

        username = (username or "").strip()
        full_name = (full_name or "").strip()

        if not username:
            return ServiceResult.fail(
                "Username is required."
            )

        if not full_name:
            return ServiceResult.fail(
                "Full name is required."
            )

        if not password:
            return ServiceResult.fail(
                "Password is required."
            )

        if printer_id is None:
            return ServiceResult.fail(
                "Printer is required for a Printer account."
            )

        # -----------------------------------------------------
        # Printer validation
        # -----------------------------------------------------

        printer = (
            db.query(Printer)
            .filter(
                Printer.id == printer_id
            )
            .first()
        )

        if printer is None:
            return ServiceResult.fail(
                "Selected printer was not found."
            )

        if not printer.is_active:
            return ServiceResult.fail(
                "Selected printer is inactive."
            )

        # -----------------------------------------------------
        # Username validation
        # -----------------------------------------------------

        existing_username = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if existing_username:
            return ServiceResult.fail(
                "Username is already in use."
            )

        # -----------------------------------------------------
        # Printer account validation
        # -----------------------------------------------------

        existing_printer_account = (
            db.query(User)
            .filter(
                User.printer_id == printer_id,
                User.role == PRINTER,
                User.is_active.is_(True),
            )
            .first()
        )

        if existing_printer_account:
            return ServiceResult.fail(
                "This printer already has a login account."
            )

        # -----------------------------------------------------
        # Create account
        # -----------------------------------------------------

        try:

            with TransactionService.transaction(db):

                user = User(
                    username=username,
                    password_hash=hash_password(password),
                    full_name=full_name,
                    role=PRINTER,
                    printer_id=printer_id,
                    is_active=True,
                )

                db.add(user)

                db.flush()

                return ServiceResult.ok(
                    data=user,
                    message=(
                        "Printer login account created successfully."
                    ),
                )

        except Exception as exc:

            return ServiceResult.fail(
                "Unable to create printer login account.",
                [str(exc)],
            )
