from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants.roles import ADMIN, PRINTER

from models.base import Base
from models.printer import Printer
from models.user import User

from services.user_service import UserService
from utils.security import hash_password


def _get_session_factory():

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


def test_admin_user_has_no_printer_assignment():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        user = User(
            username="admin",
            password_hash=hash_password(
                "AdminPassword123!"
            ),
            full_name="Administrator",
            role=ADMIN,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.role == ADMIN
        assert user.printer_id is None

    finally:
        db.close()


def test_printer_user_has_printer_assignment():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        printer = Printer(
            printer_code="PR001",
            printer_name="Test Printer",
            print_capacity_day=7500,
            night_shift_capacity=15000,
            is_active=True,
        )

        db.add(printer)
        db.commit()
        db.refresh(printer)

        result = UserService.create_printer_account(
            db=db,
            username="printer_login",
            password="PrinterPassword123!",
            full_name="Printer Login",
            printer_id=printer.id,
        )

        assert result.success is True

        user = result.data

        assert user.role == PRINTER
        assert user.printer_id == printer.id

    finally:
        db.close()
