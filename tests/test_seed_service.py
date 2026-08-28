from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

from models.base import Base
from models.user import User

from services.seed_service import seed_database

from utils.security import verify_password


def test_seed_creates_argon2_admin_password():

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    db = SessionLocal()

    try:

        seed_database(db)

        user = (
            db.query(User)
            .filter(User.username == "admin")
            .first()
        )

        assert user is not None
        assert user.role == "Admin"
        assert user.is_active is True

        assert verify_password(
            "admin@123",
            user.password_hash,
        )

    finally:

        db.close()
