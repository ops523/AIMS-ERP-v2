from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

from database import Base

from constants.status import MediaRollStatus

from models.media_roll import MediaRoll
from models.media_roll_history import MediaRollHistory
from models.activity_log import ActivityLog

from services.media_roll_service import MediaRollService


def create_test_db():

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
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


def create_roll(
    db,
    status=MediaRollStatus.AVAILABLE,
    total_sqft=200.0,
    available_sqft=200.0,
):

    roll = MediaRoll(

        asset_id="MR-STATUS-TEST001",

        roll_number="MR-STATUS-000001",

        supplier_id=1,

        manufacturer_id=1,

        product_id=1,

        warehouse_id=1,

        ordered_length_m=50.0,

        actual_length_m=50.0,

        width_ft=4.0,

        total_sqft=total_sqft,

        available_sqft=available_sqft,

        status=status,

        is_active=True,
    )

    db.add(roll)

    db.commit()

    db.refresh(roll)

    return roll


# =========================================================
# BASIC VALID TRANSITIONS
# =========================================================


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

    db.close()


def test_reserved_to_available():

    db = create_test_db()

    roll = create_roll(db)

    reserve_result = MediaRollService.reserve(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert reserve_result.success is True

    result = MediaRollService.release_reservation(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.AVAILABLE
    )

    db.close()


def test_reserved_to_allocated():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.RESERVED,
    )

    result = MediaRollService.allocate(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.ALLOCATED
    )

    db.close()


def test_allocated_to_printing():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.ALLOCATED,
    )

    result = MediaRollService.mark_printing(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.PRINTING
    )

    db.close()


def test_printing_to_printed():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.PRINTING,
    )

    result = MediaRollService.mark_printed(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.PRINTED
    )

    db.close()


# =========================================================
# INVALID TRANSITIONS
# =========================================================


def test_available_to_printed_is_rejected():

    db = create_test_db()

    roll = create_roll(db)

    result = MediaRollService.mark_printed(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is False

    db.refresh(roll)

    assert (
        roll.status
        == MediaRollStatus.AVAILABLE
    )

    db.close()


def test_available_to_consumed_is_rejected():

    db = create_test_db()

    roll = create_roll(db)

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is False

    db.refresh(roll)

    assert (
        roll.status
        == MediaRollStatus.AVAILABLE
    )

    db.close()


def test_reserved_to_printed_is_rejected():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.RESERVED,
    )

    result = MediaRollService.mark_printed(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert result.success is False

    db.refresh(roll)

    assert (
        roll.status
        == MediaRollStatus.RESERVED
    )

    db.close()


# =========================================================
# AUDIT
# =========================================================


def test_status_change_creates_history_and_activity():

    db = create_test_db()

    roll = create_roll(db)

    result = MediaRollService.reserve(
        db=db,
        media_roll_id=roll.id,
        user="TEST_USER",
    )

    assert result.success is True

    history = (
        db.query(MediaRollHistory)
        .filter(
            MediaRollHistory.media_roll_id
            == roll.id
        )
        .all()
    )

    assert len(history) >= 1

    latest_history = history[-1]

    assert (
        latest_history.previous_status
        == MediaRollStatus.AVAILABLE
    )

    assert (
        latest_history.current_status
        == MediaRollStatus.RESERVED
    )

    activities = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.reference
            == roll.roll_number
        )
        .all()
    )

    assert len(activities) >= 1

    db.close()


# =========================================================
# DAMAGE
# =========================================================


def test_available_to_damaged():

    db = create_test_db()

    roll = create_roll(db)

    result = MediaRollService.damage(
        db=db,
        media_roll_id=roll.id,
        user="TEST_USER",
        reason="Damaged during handling",
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.DAMAGED
    )

    db.close()


def test_damaged_roll_cannot_return_to_available():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.DAMAGED,
    )

    result = MediaRollService.release_reservation(
        db=db,
        media_roll_id=roll.id,
        user="TEST_USER",
    )

    assert result.success is False

    db.refresh(roll)

    assert (
        roll.status
        == MediaRollStatus.DAMAGED
    )

    db.close()


# =========================================================
# CONSUMPTION
# =========================================================


def test_printed_roll_can_be_partially_consumed():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.PRINTED,
        total_sqft=200.0,
        available_sqft=200.0,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty=50.0,
        user="TEST_USER",
    )

    assert result.success is True

    assert (
        result.data.available_sqft
        == 150.0
    )

    assert (
        result.data.status
        == MediaRollStatus.PARTIALLY_USED
    )

    db.close()


def test_printed_roll_can_be_fully_consumed():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.PRINTED,
        total_sqft=200.0,
        available_sqft=200.0,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty=200.0,
        user="TEST_USER",
    )

    assert result.success is True

    assert (
        result.data.available_sqft
        == 0.0
    )

    assert (
        result.data.status
        == MediaRollStatus.CONSUMED
    )

    db.close()


def test_consuming_more_than_available_is_rejected():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.PRINTED,
        total_sqft=200.0,
        available_sqft=200.0,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty=250.0,
        user="TEST_USER",
    )

    assert result.success is False

    db.refresh(roll)

    assert (
        roll.available_sqft
        == 200.0
    )

    assert (
        roll.status
        == MediaRollStatus.PRINTED
    )

    db.close()
