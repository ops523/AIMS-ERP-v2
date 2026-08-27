from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.user import User
from models.printer import Printer


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


def test_user_can_be_created_without_printer():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        user = User(
            username="admin",
            password_hash="test-hash",
            full_name="Administrator",
            role="Admin",
            printer_id=None,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.printer_id is None
        assert user.printer is None

    finally:
        db.close()


def test_printer_user_can_be_linked_to_printer():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        printer = Printer(
            printer_code="P001",
            printer_name="Test Printer",
            print_capacity_day=7500,
            night_shift_capacity=15000,
        )

        db.add(printer)
        db.flush()

        user = User(
            username="test_printer",
            password_hash="test-hash",
            full_name="Test Printer Account",
            role="Printer",
            printer_id=printer.id,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.printer_id == printer.id
        assert user.printer is not None
        assert user.printer.printer_code == "P001"

    finally:
        db.close()


def test_printer_can_access_its_login_user():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        printer = Printer(
            printer_code="P002",
            printer_name="Second Printer",
            print_capacity_day=5000,
            night_shift_capacity=10000,
        )

        db.add(printer)
        db.flush()

        user = User(
            username="printer_002",
            password_hash="test-hash",
            full_name="Second Printer Account",
            role="Printer",
            printer_id=printer.id,
            is_active=True,
        )

        db.add(user)
        db.commit()

        db.refresh(printer)

        assert printer.user is not None
        assert printer.user.username == "printer_002"

    finally:
        db.close()
