from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

from database import Base

from models.document_sequence import DocumentSequence
from models.media_roll import MediaRoll
from models.supplier import Supplier
from models.manufacturer import Manufacturer
from models.media_product import MediaProduct
from models.warehouse import Warehouse
from models.inventory_transaction import InventoryTransaction
from models.media_roll_history import MediaRollHistory
from models.activity_log import ActivityLog

from services.media_roll_service import MediaRollService
from services.activity_log_service import ActivityLogService


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


def create_master_data(db):

    manufacturer = Manufacturer(
        manufacturer_code="RB-MF001",
        manufacturer_name="Rollback Manufacturer",
        country="India",
        is_active=True,
    )

    supplier = Supplier(
        supplier_code="RB-SUP001",
        supplier_name="Rollback Supplier",
        is_active=True,
    )

    warehouse = Warehouse(
        warehouse_code="RB-WH001",
        warehouse_name="Rollback Warehouse",
        city="Delhi",
        state="Delhi",
        is_active=True,
    )

    db.add_all(
        [
            manufacturer,
            supplier,
            warehouse,
        ]
    )

    db.flush()

    product = MediaProduct(
        product_code="RB-MP001",
        manufacturer_id=manufacturer.id,
        product_name="Rollback Test Media",
        width_ft=4.0,
        gsm=300,
        finish="Matte",
        standard_length_m=50,
        is_active=True,
    )

    sequence = DocumentSequence(
        document_type="MEDIA_ROLL",
        prefix="MR",
        last_number=20,
    )

    db.add_all(
        [
            product,
            sequence,
        ]
    )

    db.commit()

    return {
        "manufacturer": manufacturer,
        "supplier": supplier,
        "warehouse": warehouse,
        "product": product,
        "sequence": sequence,
    }


def build_media_roll(master):

    return MediaRoll(

        supplier_id=master["supplier"].id,

        manufacturer_id=master["manufacturer"].id,

        product_id=master["product"].id,

        warehouse_id=master["warehouse"].id,

        manufacturer_roll_no="RB-ROLL-001",

        purchase_order="RB-PO-001",

        invoice_number="RB-INV-001",

        ordered_length_m=50.0,

        actual_length_m=50.0,

        width_ft=4.0,

        total_sqft=200.0,

        available_sqft=0.0,

        remarks="Rollback transaction test",

    )


def test_receive_roll_rolls_back_entire_transaction(
    monkeypatch,
):

    db = create_test_db()

    master = create_master_data(db)

    starting_sequence = (
        master["sequence"].last_number
    )

    roll = build_media_roll(master)

    def force_activity_failure(*args, **kwargs):

        raise RuntimeError(
            "TEST: forced activity log failure"
        )

    monkeypatch.setattr(
        ActivityLogService,
        "log",
        force_activity_failure,
    )

    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="ROLLBACK_TEST",
    )

    assert result.success is False

    # ---------------------------------------------------------
    # Media Roll must NOT exist
    # ---------------------------------------------------------

    roll_count = (
        db.query(MediaRoll)
        .count()
    )

    assert roll_count == 0

    # ---------------------------------------------------------
    # Inventory transaction must NOT exist
    # ---------------------------------------------------------

    inventory_count = (
        db.query(InventoryTransaction)
        .count()
    )

    assert inventory_count == 0

    # ---------------------------------------------------------
    # History must NOT exist
    # ---------------------------------------------------------

    history_count = (
        db.query(MediaRollHistory)
        .count()
    )

    assert history_count == 0

    # ---------------------------------------------------------
    # Activity log must NOT exist
    # ---------------------------------------------------------

    activity_count = (
        db.query(ActivityLog)
        .count()
    )

    assert activity_count == 0

    # ---------------------------------------------------------
    # Document sequence must roll back
    # ---------------------------------------------------------

    sequence = (
        db.query(DocumentSequence)
        .filter(
            DocumentSequence.document_type
            == "MEDIA_ROLL"
        )
        .first()
    )

    assert sequence is not None

    assert (
        sequence.last_number
        == starting_sequence
    )

    # ---------------------------------------------------------
    # No committed QR reference should exist
    # ---------------------------------------------------------

    committed_roll = (
        db.query(MediaRoll)
        .filter(
            MediaRoll.manufacturer_roll_no
            == "RB-ROLL-001"
        )
        .first()
    )

    assert committed_roll is None

    db.close()


def test_successful_receive_after_rollback_reuses_sequence():

    db = create_test_db()

    master = create_master_data(db)

    starting_sequence = (
        master["sequence"].last_number
    )

    roll = build_media_roll(master)

    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="ROLLBACK_TEST",
    )

    assert result.success is True

    received_roll = result.data

    assert received_roll.roll_number.endswith(
        f"-{starting_sequence + 1:06d}"
    )

    assert received_roll.status == "AVAILABLE"

    assert received_roll.available_sqft == 200.0

    db.close()
