from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants.roles import ADMIN, PRINTER

from models.base import Base
from models.printer import Printer
from models.user import User

from services.auth_service import AuthService
from services.user_service import UserService


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


def _create_user(
    db,
    username="admin",
    password="AdminPassword123!",
    role=ADMIN,
    is_active=True,
):

    printer = None

    if role == PRINTER:

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
            username=username,
            password=password,
            full_name="Test User",
            printer_id=printer.id,
        )

        assert result.success is True

        user = result.data

        if not is_active:
            user.is_active = False
            db.commit()
            db.refresh(user)

        return user

    from utils.security import hash_password

    user = User(
        username=username,
        password_hash=hash_password(password),
        full_name="Test User",
        role=role,
        is_active=is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def test_authentication_succeeds_with_correct_credentials():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        user = _create_user(db)

        result = AuthService.authenticate(
            db=db,
            username=user.username,
            password="AdminPassword123!",
        )

        assert result.success is True
        assert result.data.id == user.id
        assert result.data.username == "admin"
        assert result.message == "Authentication successful."

    finally:
        db.close()


def test_authentication_fails_with_wrong_password():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        user = _create_user(db)

        result = AuthService.authenticate(
            db=db,
            username=user.username,
            password="WrongPassword123!",
        )

        assert result.success is False
        assert result.data is None
        assert "invalid username or password" in result.message.lower()

    finally:
        db.close()


def test_authentication_fails_for_unknown_username():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        result = AuthService.authenticate(
            db=db,
            username="does_not_exist",
            password="SomePassword123!",
        )

        assert result.success is False
        assert result.data is None
        assert "invalid username or password" in result.message.lower()

    finally:
        db.close()


def test_inactive_user_cannot_authenticate():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        user = _create_user(
            db,
            is_active=False,
        )

        result = AuthService.authenticate(
            db=db,
            username=user.username,
            password="AdminPassword123!",
        )

        assert result.success is False
        assert result.data is None
        assert "inactive" in result.message.lower()

    finally:
        db.close()


def test_empty_username_is_rejected():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        result = AuthService.authenticate(
            db=db,
            username="",
            password="SomePassword123!",
        )

        assert result.success is False
        assert result.data is None

    finally:
        db.close()


def test_empty_password_is_rejected():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        result = AuthService.authenticate(
            db=db,
            username="admin",
            password="",
        )

        assert result.success is False
        assert result.data is None

    finally:
        db.close()


def test_printer_user_can_authenticate():

    SessionLocal = _get_session_factory()
    db = SessionLocal()

    try:

        user = _create_user(
            db,
            username="printer_login",
            password="PrinterPassword123!",
            role=PRINTER,
        )

        result = AuthService.authenticate(
            db=db,
            username="printer_login",
            password="PrinterPassword123!",
        )

        assert result.success is True
        assert result.data.id == user.id
        assert result.data.role == PRINTER
        assert result.data.printer_id is not None

    finally:
        db.close()
