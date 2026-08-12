from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base

import models

from constants.status import MediaRollStatus
from models.media_roll import MediaRoll

from services.media_roll_service import (
    MediaRollService,
)


def create_test_db():

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False
        },
    )

    Base.metadata.create_all(
        bind=engine
    )

    Session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return Session()


def create_roll(db):

    roll = MediaRoll(

        asset_id="MR-TEST001",

        roll_number="MR-TEST-000001",

        supplier_id=1,

        manufacturer_id=1,

        product_id=1,

        warehouse_id=1,

        ordered_length_m=50,

        actual_length_m=50,

        width_ft=4,

        total_sqft=200,

        available_sqft=200,

        status=MediaRollStatus.AVAILABLE,

        is_active=True,
    )

    db.add(roll)

    db.commit()

    db.refresh(roll)

    return roll


def test_available_to_reserved():

    db = create_test_db()

    roll = create_roll(db)

    result = MediaRollService.reserve(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.RESERVED
    )


def test_reserved_to_available():

    db = create_test_db()

    roll = create_roll(db)

    MediaRollService.reserve(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    result = (
        MediaRollService.release_reservation(
            db=db,
            media_roll_id=roll.id,
            user="TEST",
        )
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.AVAILABLE
    )


def test_invalid_status_transition():

    db = create_test_db()

    roll = create_roll(db)

    result = MediaRollService.mark_printed(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is False
