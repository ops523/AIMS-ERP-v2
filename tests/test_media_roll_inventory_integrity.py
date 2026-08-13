from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

from database import Base

from constants.status import MediaRollStatus

from models.media_roll import MediaRoll
from models.inventory_transaction import (
    InventoryTransaction,
)

from services.inventory_transaction_service import (
    InventoryTransactionService,
)

from services.media_roll_service import (
    MediaRollService,
)


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
# MEDIA ROLL FACTORY
# =========================================================

def create_roll(
    db,
    total_sqft=200.0,
    available_sqft=200.0,
    status=MediaRollStatus.AVAILABLE,
):

    roll = MediaRoll(

        asset_id="MR-INTEGRITY-TEST",

        roll_number="MR-INTEGRITY-000001",

        manufacturer_roll_no="INTEGRITY-001",

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
# RECEIPT HELPER
# =========================================================

def create_receipt(
    db,
    roll,
    qty,
):

    return (
        InventoryTransactionService.receive_roll(
            db=db,
            media_roll_id=roll.id,
            warehouse_id=roll.warehouse_id,
            qty=qty,
            user="TEST_USER",
            remarks="Inventory integrity test receipt",
        )
    )


# =========================================================
# TEST 1
# RECEIPT CREATES INITIAL BALANCE
# =========================================================

def test_receipt_creates_initial_balance():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=200.0,
        available_sqft=200.0,
    )

    transaction = create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    assert transaction is not None

    assert transaction.qty_in == 200.0

    assert transaction.qty_out == 0

    assert transaction.balance_qty == 200.0

    db.close()


# =========================================================
# TEST 2
# SECOND RECEIPT INCREASES BALANCE
# =========================================================

def test_second_receipt_increases_balance():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=400.0,
        available_sqft=400.0,
    )

    first = create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    second = create_receipt(
        db=db,
        roll=roll,
        qty=100.0,
    )

    assert first.balance_qty == 200.0

    assert second.balance_qty == 300.0

    db.close()


# =========================================================
# TEST 3
# PARTIAL CONSUMPTION REDUCES BALANCE
# =========================================================

def test_partial_consumption_reduces_balance():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=200.0,
        available_sqft=200.0,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    transaction = (
        InventoryTransactionService.consume_roll(
            db=db,
            media_roll_id=roll.id,
            campaign_id=None,
            printer_id=None,
            warehouse_id=roll.warehouse_id,
            qty=50.0,
            wastage=0,
            remarks="Partial consumption test",
            user="TEST_USER",
        )
    )

    assert transaction.qty_in == 0

    assert transaction.qty_out == 50.0

    assert transaction.balance_qty == 150.0

    db.close()


# =========================================================
# TEST 4
# FULL CONSUMPTION REACHES ZERO
# =========================================================

def test_full_consumption_reaches_zero():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=200.0,
        available_sqft=200.0,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    transaction = (
        InventoryTransactionService.consume_roll(
            db=db,
            media_roll_id=roll.id,
            campaign_id=None,
            printer_id=None,
            warehouse_id=roll.warehouse_id,
            qty=200.0,
            wastage=0,
            remarks="Full consumption test",
            user="TEST_USER",
        )
    )

    assert transaction.balance_qty == 0.0

    db.close()


# =========================================================
# TEST 5
# OVER-CONSUMPTION IS REJECTED
# =========================================================

def test_over_consumption_is_rejected():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=200.0,
        available_sqft=200.0,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    try:

        InventoryTransactionService.consume_roll(
            db=db,
            media_roll_id=roll.id,
            campaign_id=None,
            printer_id=None,
            warehouse_id=roll.warehouse_id,
            qty=250.0,
            wastage=0,
            remarks="Invalid over-consumption",
            user="TEST_USER",
        )

        assert False, (
            "Expected over-consumption "
            "to be rejected."
        )

    except ValueError as exc:

        assert (
            "Insufficient inventory"
            in str(exc)
        )

    db.close()


# =========================================================
# TEST 6
# NEGATIVE RECEIPT IS REJECTED
# =========================================================

def test_negative_receipt_is_rejected():

    db = create_test_db()

    roll = create_roll(db)

    try:

        create_receipt(
            db=db,
            roll=roll,
            qty=-10.0,
        )

        assert False, (
            "Expected negative receipt "
            "to be rejected."
        )

    except ValueError as exc:

        assert (
            "greater than zero"
            in str(exc)
        )

    db.close()


# =========================================================
# TEST 7
# NEGATIVE CONSUMPTION IS REJECTED
# =========================================================

def test_negative_consumption_is_rejected():

    db = create_test_db()

    roll = create_roll(
        db,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    try:

        InventoryTransactionService.consume_roll(
            db=db,
            media_roll_id=roll.id,
            campaign_id=None,
            printer_id=None,
            warehouse_id=roll.warehouse_id,
            qty=-10.0,
            wastage=0,
            remarks="Invalid negative consumption",
            user="TEST_USER",
        )

        assert False, (
            "Expected negative consumption "
            "to be rejected."
        )

    except ValueError as exc:

        assert (
            "cannot be negative"
            in str(exc)
            or "greater than zero"
            in str(exc)
        )

    db.close()


# =========================================================
# TEST 8
# ZERO RECEIPT IS REJECTED
# =========================================================

def test_zero_receipt_is_rejected():

    db = create_test_db()

    roll = create_roll(db)

    try:

        create_receipt(
            db=db,
            roll=roll,
            qty=0,
        )

        assert False, (
            "Expected zero receipt "
            "to be rejected."
        )

    except ValueError as exc:

        assert (
            "greater than zero"
            in str(exc)
        )

    db.close()


# =========================================================
# TEST 9
# SEQUENTIAL TRANSACTIONS
# =========================================================

def test_sequential_inventory_transactions():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=500.0,
        available_sqft=500.0,
        status=MediaRollStatus.PRINTED,
    )

    first_receipt = create_receipt(
        db=db,
        roll=roll,
        qty=500.0,
    )

    assert first_receipt.balance_qty == 500.0

    first_consumption = (
        InventoryTransactionService.consume_roll(
            db=db,
            media_roll_id=roll.id,
            campaign_id=None,
            printer_id=None,
            warehouse_id=roll.warehouse_id,
            qty=100.0,
            wastage=0,
            remarks="First consumption",
            user="TEST_USER",
        )
    )

    assert (
        first_consumption.balance_qty
        == 400.0
    )

    second_consumption = (
        InventoryTransactionService.consume_roll(
            db=db,
            media_roll_id=roll.id,
            campaign_id=None,
            printer_id=None,
            warehouse_id=roll.warehouse_id,
            qty=150.0,
            wastage=0,
            remarks="Second consumption",
            user="TEST_USER",
        )
    )

    assert (
        second_consumption.balance_qty
        == 250.0
    )

    db.close()


# =========================================================
# TEST 10
# LEDGER BALANCE MATCHES EXPECTED BALANCE
# =========================================================

def test_ledger_balance_matches_expected_balance():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=300.0,
        available_sqft=300.0,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=300.0,
    )

    InventoryTransactionService.consume_roll(
        db=db,
        media_roll_id=roll.id,
        campaign_id=None,
        printer_id=None,
        warehouse_id=roll.warehouse_id,
        qty=75.0,
        wastage=0,
        remarks="Balance test",
        user="TEST_USER",
    )

    latest = (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.media_roll_id
            == roll.id
        )
        .order_by(
            InventoryTransaction.id.desc()
        )
        .first()
    )

    assert latest is not None

    assert latest.balance_qty == 225.0

    db.close()


# =========================================================
# TEST 11
# MEDIA ROLL CONSUMPTION KEEPS BOTH BALANCES IN SYNC
# =========================================================

def test_media_roll_and_ledger_remain_in_sync():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=200.0,
        available_sqft=200.0,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty_sqft=50.0,
        user="TEST_USER",
    )

    assert result.success is True

    db.refresh(roll)

    latest = (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.media_roll_id
            == roll.id
        )
        .order_by(
            InventoryTransaction.id.desc()
        )
        .first()
    )

    assert latest is not None

    assert (
        roll.available_sqft
        == latest.balance_qty
    )

    assert roll.available_sqft == 150.0

    db.close()


# =========================================================
# TEST 12
# FULL MEDIA ROLL CONSUMPTION SYNCHRONIZES TO ZERO
# =========================================================

def test_full_media_roll_consumption_synchronizes_to_zero():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=200.0,
        available_sqft=200.0,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    result = MediaRollService.consume(
        db=db,
        media_roll_id=roll.id,
        qty_sqft=200.0,
        user="TEST_USER",
    )

    assert result.success is True

    db.refresh(roll)

    latest = (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.media_roll_id
            == roll.id
        )
        .order_by(
            InventoryTransaction.id.desc()
        )
        .first()
    )

    assert latest is not None

    assert latest.balance_qty == 0.0

    assert roll.available_sqft == 0.0

    assert (
        roll.available_sqft
        == latest.balance_qty
    )

    assert (
        roll.status
        == MediaRollStatus.CONSUMED
    )

    db.close()


# =========================================================
# TEST 13
# FAILED TRANSACTION DOES NOT CREATE LEDGER ENTRY
# =========================================================

def test_failed_consumption_does_not_create_transaction():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=200.0,
        available_sqft=200.0,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=200.0,
    )

    before_count = (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.media_roll_id
            == roll.id
        )
        .count()
    )

    try:

        InventoryTransactionService.consume_roll(
            db=db,
            media_roll_id=roll.id,
            campaign_id=None,
            printer_id=None,
            warehouse_id=roll.warehouse_id,
            qty=300.0,
            wastage=0,
            remarks="Should fail",
            user="TEST_USER",
        )

        assert False, (
            "Expected transaction "
            "to fail."
        )

    except ValueError:

        pass

    after_count = (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.media_roll_id
            == roll.id
        )
        .count()
    )

    assert (
        before_count
        == after_count
    )

    db.close()


# =========================================================
# TEST 14
# LEDGER HISTORY IS PRESERVED
# =========================================================

def test_inventory_transaction_history_is_preserved():

    db = create_test_db()

    roll = create_roll(
        db,
        total_sqft=300.0,
        available_sqft=300.0,
        status=MediaRollStatus.PRINTED,
    )

    create_receipt(
        db=db,
        roll=roll,
        qty=300.0,
    )

    InventoryTransactionService.consume_roll(
        db=db,
        media_roll_id=roll.id,
        campaign_id=None,
        printer_id=None,
        warehouse_id=roll.warehouse_id,
        qty=100.0,
        wastage=0,
        remarks="First consumption",
        user="TEST_USER",
    )

    InventoryTransactionService.consume_roll(
        db=db,
        media_roll_id=roll.id,
        campaign_id=None,
        printer_id=None,
        warehouse_id=roll.warehouse_id,
        qty=50.0,
        wastage=0,
        remarks="Second consumption",
        user="TEST_USER",
    )

    transactions = (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.media_roll_id
            == roll.id
        )
        .order_by(
            InventoryTransaction.id.asc()
        )
        .all()
    )

    assert len(transactions) == 3

    assert transactions[0].qty_in == 300.0
    assert transactions[0].balance_qty == 300.0

    assert transactions[1].qty_out == 100.0
    assert transactions[1].balance_qty == 200.0

    assert transactions[2].qty_out == 50.0
    assert transactions[2].balance_qty == 150.0

    db.close()
