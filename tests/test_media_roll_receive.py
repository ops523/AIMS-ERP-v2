from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

from database import Base

from constants.status import MediaRollStatus

from models.supplier import Supplier
from models.manufacturer import Manufacturer
from models.media_product import MediaProduct
from models.warehouse import Warehouse
from models.document_sequence import DocumentSequence

from models.media_roll import MediaRoll
from models.inventory_transaction import (
    InventoryTransaction,
)
from models.media_roll_history import (
    MediaRollHistory,
)
from models.activity_log import ActivityLog

from services.media_roll_service import (
    MediaRollService,
)


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
        manufacturer_code="TEST-MF001",
        manufacturer_name="Test Manufacturer",
        country="India",
        website="",
        is_active=True,
    )

    supplier = Supplier(
        supplier_code="TEST-SUP001",
        supplier_name="Test Supplier",
        is_active=True,
    )

    warehouse = Warehouse(
        warehouse_code="TEST-WH001",
        warehouse_name="Test Warehouse",
        city="Delhi",
        state="Delhi",
        is_active=True,
    )

    db.add_all([
        manufacturer,
        supplier,
        warehouse,
    ])

    db.flush()

    product = MediaProduct(
        product_code="TEST-MP001",
        manufacturer_id=manufacturer.id,
        product_name="Test Media",
        width_ft=4.0,
        gsm=300,
        finish="Matte",
        standard_length_m=95,
        is_active=True,
    )

    sequence = DocumentSequence(
        document_type="MEDIA_ROLL",
        prefix="MR",
        last_number=0,
    )

    db.add_all([
        product,
        sequence,
    ])

    db.commit()

    db.refresh(manufacturer)
    db.refresh(supplier)
    db.refresh(warehouse)
    db.refresh(product)

    return {
        "manufacturer": manufacturer,
        "supplier": supplier,
        "warehouse": warehouse,
        "product": product,
    }


def build_media_roll(master):

    return MediaRoll(

        supplier_id=master["supplier"].id,

        manufacturer_id=master["manufacturer"].id,

        product_id=master["product"].id,

        warehouse_id=master["warehouse"].id,

        manufacturer_roll_no="TEST-ROLL-001",

        purchase_order="PO-TEST-001",

        invoice_number="INV-TEST-001",

        ordered_length_m=50.0,

        actual_length_m=50.0,

        width_ft=4.0,

        total_sqft=200.0,

        available_sqft=0.0,

        remarks="Automated test roll",

    )


def test_receive_roll_complete_transaction():

    db = create_test_db()

    master = create_master_data(db)

    roll = build_media_roll(master)

    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )

    assert result.success is True

    received_roll = result.data

    assert received_roll.id is not None

    assert received_roll.uuid is not None

    assert received_roll.asset_id is not None

    assert received_roll.asset_id.startswith("MR-")

    assert received_roll.roll_number == "MR-2026-000001"

    assert received_roll.qr_payload is not None

    assert received_roll.qr_payload.startswith(
        "ADW|MR|"
    )

    assert received_roll.qr_image_path is not None

    assert (
        received_roll.status
        == MediaRollStatus.AVAILABLE
    )

    assert (
        received_roll.available_sqft
        == 200.0
    )

    inventory = (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.media_roll_id
            == received_roll.id
        )
        .all()
    )

    assert len(inventory) == 1

    receipt = inventory[0]

    assert receipt.transaction_type == "RECEIPT"

    assert receipt.qty_in == 200.0

    assert receipt.qty_out == 0

    assert receipt.balance_qty == 200.0

    history = (
        db.query(MediaRollHistory)
        .filter(
            MediaRollHistory.media_roll_id
            == received_roll.id
        )
        .all()
    )

    assert len(history) >= 2

    activities = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.reference
            == received_roll.roll_number
        )
        .all()
    )

    assert len(activities) >= 1

    db.close()


def test_receive_roll_creates_qr_file():

    db = create_test_db()

    master = create_master_data(db)

    roll = build_media_roll(master)

    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )

    assert result.success is True

    received_roll = result.data

    from pathlib import Path

    qr_file = Path(
        received_roll.qr_image_path
    )

    assert qr_file.exists()

    assert qr_file.stat().st_size > 0

    db.close()
