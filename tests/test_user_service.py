from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants.roles import ADMIN, PRINTER

from models.base import Base
from models.printer import Printer
from models.user import User

from services.user_service import UserService

from utils.security import verify_password


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


def _create_printer(db):

    printer = Printer(
        printer_code="PR001",
        printer_name="Test Printer",
        city="Mumbai",
        state="Maharashtra",
        print_capacity_day=7500,
        night_shift_capacity=15000,
        is_active=True,
    )

    db.add(printer)
    db.commit()
    db.refresh(printer)

    return printer


def test_printer_account_can_be_created():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        printer = _create_printer(db)

        result = UserService.create_printer_account(
            db=db,
            username="test_printer",
            password="SecurePassword123!",
            full_name="Test Printer Account",
            printer_id=printer.id,
        )

        assert result.success is True
        assert result.data is not None

        user = result.data

        assert user.username == "test_printer"
        assert user.role == PRINTER
        assert user.printer_id == printer.id
        assert user.is_active is True

        assert user.password_hash != "SecurePassword123!"

        assert verify_password(
            "SecurePassword123!",
            user.password_hash,
        )

    finally:
        db.close()


def test_printer_account_requires_printer():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        result = UserService.create_printer_account(
            db=db,
            username="printer_without_assignment",
            password="SecurePassword123!",
            full_name="Printer Account",
            printer_id=None,
        )

        assert result.success is False

    finally:
        db.close()


def test_inactive_printer_cannot_get_account():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        printer = Printer(
            printer_code="PR002",
            printer_name="Inactive Printer",
            print_capacity_day=5000,
            night_shift_capacity=10000,
            is_active=False,
        )

        db.add(printer)
        db.commit()
        db.refresh(printer)

        result = UserService.create_printer_account(
            db=db,
            username="inactive_printer",
            password="SecurePassword123!",
            full_name="Inactive Printer",
            printer_id=printer.id,
        )

        assert result.success is False
        assert "inactive" in result.message.lower()

    finally:
        db.close()


def test_duplicate_username_is_rejected():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        printer_1 = _create_printer(db)

        result_1 = UserService.create_printer_account(
            db=db,
            username="same_username",
            password="SecurePassword123!",
            full_name="First Account",
            printer_id=printer_1.id,
        )

        assert result_1.success is True

        printer_2 = Printer(
            printer_code="PR003",
            printer_name="Second Printer",
            print_capacity_day=5000,
            night_shift_capacity=10000,
            is_active=True,
        )

        db.add(printer_2)
        db.commit()
        db.refresh(printer_2)

        result_2 = UserService.create_printer_account(
            db=db,
            username="same_username",
            password="AnotherPassword123!",
            full_name="Second Account",
            printer_id=printer_2.id,
        )

        assert result_2.success is False
        assert "username" in result_2.message.lower()

    finally:
        db.close()


def test_second_account_for_same_printer_is_rejected():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        printer = _create_printer(db)

        result_1 = UserService.create_printer_account(
            db=db,
            username="printer_one",
            password="SecurePassword123!",
            full_name="First Account",
            printer_id=printer.id,
        )

        assert result_1.success is True

        result_2 = UserService.create_printer_account(
            db=db,
            username="printer_two",
            password="AnotherPassword123!",
            full_name="Second Account",
            printer_id=printer.id,
        )

        assert result_2.success is False
        assert "already has" in result_2.message.lower()

    finally:
        db.close()


def test_printer_account_password_is_not_stored_plaintext():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        printer = _create_printer(db)

        password = "VerySecretPassword123!"

        result = UserService.create_printer_account(
            db=db,
            username="secure_printer",
            password=password,
            full_name="Secure Printer",
            printer_id=printer.id,
        )

        assert result.success is True

        user = result.data

        assert user.password_hash != password
        assert verify_password(
            password,
            user.password_hash,
        )

    finally:
        db.close()
