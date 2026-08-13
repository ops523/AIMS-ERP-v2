from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

from database import Base

from constants.status import MediaRollStatus

from models.media_roll import MediaRoll
from models.inventory_transaction import InventoryTransaction

from services.media_roll_service import MediaRollService


# =========================================================
# TEST DATABASE
# =========================================================

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


# =========================================================
# TEST MEDIA ROLL FACTORY
# =========================================================

def create_roll(
    db,
    status=MediaRollStatus.AVAILABLE,
    total_sqft=200.0,
    available_sqft=200.0,
):

    roll = MediaRoll(

        asset_id="MR-LIFECYCLE-TEST",

        roll_number="MR-LIFECYCLE-000001",

        manufacturer_roll_no="LIFECYCLE-001",

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
# INVENTORY RECEIPT FACTORY
# =========================================================

def create_inventory_receipt(
    db,
    roll,
    qty_sqft,
):

    receipt = InventoryTransaction(

        media_roll_id=roll.id,

        transaction_type="RECEIPT",

        reference_module="MEDIA_ROLL",

        reference_id=roll.id,

        warehouse_id=roll.warehouse_id,

        unit_cost=0,

        total_cost=0,

        wastage_sqft=0,

        qty_in=qty_sqft,

        qty_out=0,

        balance_qty=qty_sqft,

        remarks="Lifecycle test inventory receipt",

        performed_by="TEST_USER",
    )

    db.add(receipt)

    db.commit()

    db.refresh(receipt)

    return receipt


# =========================================================
# RESERVATION LIFECYCLE
# =========================================================

def test_available_to_reserved():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.AVAILABLE,
    )

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

    roll = create_roll(
        db,
        status=MediaRollStatus.AVAILABLE,
    )

    reserve_result = MediaRollService.reserve(
        db=db,
        media_roll_id=roll.id,
        user="TEST",
    )

    assert reserve_result.success is True

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

    db.close()


def test_reserved_to_allocated():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.RESERVED,
    )

    result = MediaRollService.change_status(
        db=db,
        media_roll_id=roll.id,
        new_status=MediaRollStatus.ALLOCATED,
        user="TEST",
        reason="Lifecycle test allocation",
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.ALLOCATED
    )

    db.close()


# =========================================================
# PRINTING LIFECYCLE
# =========================================================

def test_allocated_to_printing():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.ALLOCATED,
    )

    result = MediaRollService.change_status(
        db=db,
        media_roll_id=roll.id,
        new_status=MediaRollStatus.PRINTING,
        user="TEST",
        reason="Lifecycle test printing",
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
# INVALID STATUS TRANSITIONS
# =========================================================

def test_available_to_printed_is_rejected():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.AVAILABLE,
    )

    result = MediaRollService.change_status(
        db=db,
        media_roll_id=roll.id,
        new_status=MediaRollStatus.PRINTED,
        user="TEST",
        reason="Invalid lifecycle transition",
    )

    assert result.success is False

    assert (
        roll.status
        == MediaRollStatus.AVAILABLE
    )

    db.close()


def test_available_to_consumed_is_rejected():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.AVAILABLE,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty_sqft=1.0,
        user="TEST",
    )

    assert result.success is False

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

    result = MediaRollService.change_status(
        db=db,
        media_roll_id=roll.id,
        new_status=MediaRollStatus.PRINTED,
        user="TEST",
        reason="Invalid lifecycle transition",
    )

    assert result.success is False

    assert (
        roll.status
        == MediaRollStatus.RESERVED
    )

    db.close()


# =========================================================
# HISTORY + ACTIVITY
# =========================================================

def test_status_change_creates_history_and_activity():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.AVAILABLE,
    )

    result = MediaRollService.change_status(
        db=db,
        media_roll_id=roll.id,
        new_status=MediaRollStatus.RESERVED,
        user="TEST_USER",
        reason="Lifecycle test",
    )

    assert result.success is True

    assert (
        result.data.status
        == MediaRollStatus.RESERVED
    )

    db.refresh(roll)

    assert (
        roll.status
        == MediaRollStatus.RESERVED
    )

    db.close()


# =========================================================
# DAMAGE
# =========================================================

def test_available_to_damaged():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.AVAILABLE,
    )

    result = MediaRollService.change_status(
        db=db,
        media_roll_id=roll.id,
        new_status=MediaRollStatus.DAMAGED,
        user="TEST_USER",
        reason="Physical damage",
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

    result = MediaRollService.change_status(
        db=db,
        media_roll_id=roll.id,
        new_status=MediaRollStatus.AVAILABLE,
        user="TEST_USER",
        reason="Invalid damaged rollback",
    )

    assert result.success is False

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

    # The roll must have inventory ledger balance
    # before consumption can occur.
    create_inventory_receipt(
        db=db,
        roll=roll,
        qty_sqft=200.0,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty_sqft=50.0,
        user="TEST_USER",
    )

    assert result.success is True

    db.refresh(roll)

    assert (
        roll.available_sqft
        == 150.0
    )

    assert (
        roll.status
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

    create_inventory_receipt(
        db=db,
        roll=roll,
        qty_sqft=200.0,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty_sqft=200.0,
        user="TEST_USER",
    )

    assert result.success is True

    db.refresh(roll)

    assert (
        roll.available_sqft
        == 0.0
    )

    assert (
        roll.status
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

    create_inventory_receipt(
        db=db,
        roll=roll,
        qty_sqft=200.0,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty_sqft=250.0,
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
