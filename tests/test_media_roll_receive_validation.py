from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

from database import Base

from models.supplier import Supplier
from models.manufacturer import Manufacturer
from models.media_product import MediaProduct
from models.warehouse import Warehouse
from models.document_sequence import DocumentSequence

from models.media_roll import MediaRoll

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
# MASTER DATA
# =========================================================

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


# =========================================================
# BUILD MEDIA ROLL
# =========================================================

def build_media_roll(
    master,
    manufacturer_roll_no="TEST-ROLL-001",
):

    return MediaRoll(

        supplier_id=master["supplier"].id,

        manufacturer_id=master["manufacturer"].id,

        product_id=master["product"].id,

        warehouse_id=master["warehouse"].id,

        manufacturer_roll_no=(
            manufacturer_roll_no
        ),

        purchase_order="PO-TEST-001",

        invoice_number="INV-TEST-001",

        ordered_length_m=50.0,

        actual_length_m=50.0,

        width_ft=4.0,

        total_sqft=200.0,

        available_sqft=0.0,

        remarks="Automated validation test",

    )


# =========================================================
# TEST 1
# =========================================================
# Manufacturer Roll Number is mandatory.
# =========================================================

def test_missing_manufacturer_roll_number():

    db = create_test_db()

    master = create_master_data(db)

    roll = build_media_roll(
        master,
        manufacturer_roll_no="",
    )

    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )

    assert result.success is False

    assert any(
        "Manufacturer Roll Number is required."
        in error
        for error in result.errors
    )

    db.close()


# =========================================================
# TEST 2
# =========================================================
# Duplicate Manufacturer Roll Number must be rejected.
# =========================================================

def test_duplicate_manufacturer_roll_number():

    db = create_test_db()

    master = create_master_data(db)

    manufacturer_roll_no = (
        "DUPLICATE-ROLL-001"
    )


    # -----------------------------------------------------
    # First receipt
    # -----------------------------------------------------

    first_roll = build_media_roll(
        master,
        manufacturer_roll_no=(
            manufacturer_roll_no
        ),
    )

    first_result = MediaRollService.receive(
        db=db,
        media_roll=first_roll,
        user="TEST",
    )

    assert first_result.success is True


    # -----------------------------------------------------
    # Second receipt
    # -----------------------------------------------------

    second_roll = build_media_roll(
        master,
        manufacturer_roll_no=(
            manufacturer_roll_no
        ),
    )

    second_result = MediaRollService.receive(
        db=db,
        media_roll=second_roll,
        user="TEST",
    )

    assert second_result.success is False

    assert any(
        "has already been received."
        in error
        for error in second_result.errors
    )


    db.close()


# =========================================================
# TEST 3
# =========================================================
# Invalid actual length must be rejected.
# =========================================================

def test_invalid_actual_length():

    db = create_test_db()

    master = create_master_data(db)

    roll = build_media_roll(
        master,
        manufacturer_roll_no=(
            "INVALID-LENGTH-001"
        ),
    )

    roll.actual_length_m = 0


    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )


    assert result.success is False

    assert any(
        "Actual length must be greater than zero."
        in error
        for error in result.errors
    )


    db.close()


# =========================================================
# TEST 4
# =========================================================
# Invalid ordered length must be rejected.
# =========================================================

def test_invalid_ordered_length():

    db = create_test_db()

    master = create_master_data(db)

    roll = build_media_roll(
        master,
        manufacturer_roll_no=(
            "INVALID-ORDERED-LENGTH-001"
        ),
    )

    roll.ordered_length_m = 0


    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )


    assert result.success is False

    assert any(
        "Ordered length must be greater than zero."
        in error
        for error in result.errors
    )


    db.close()


# =========================================================
# TEST 5
# =========================================================
# Invalid width must be rejected.
# =========================================================

def test_invalid_width():

    db = create_test_db()

    master = create_master_data(db)

    roll = build_media_roll(
        master,
        manufacturer_roll_no=(
            "INVALID-WIDTH-001"
        ),
    )

    roll.width_ft = 0


    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )


    assert result.success is False

    assert any(
        "Width must be greater than zero."
        in error
        for error in result.errors
    )


    db.close()


# =========================================================
# TEST 6
# =========================================================
# Invalid total square feet must be rejected.
# =========================================================

def test_invalid_total_sqft():

    db = create_test_db()

    master = create_master_data(db)

    roll = build_media_roll(
        master,
        manufacturer_roll_no=(
            "INVALID-SQFT-001"
        ),
    )

    roll.total_sqft = 0


    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )


    assert result.success is False

    assert any(
        "Total square feet must be greater than zero."
        in error
        for error in result.errors
    )


    db.close()

    def test_matching_manufacturer_and_product_is_accepted():

    db = create_test_db()

    master = create_master_data(db)

    roll = build_media_roll(
        master,
        manufacturer_roll_no=(
            "MATCHING-MANUFACTURER-001"
        ),
    )

    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )

    assert result.success is True

    db.close()


    def test_mismatched_manufacturer_and_product_is_rejected():

    db = create_test_db()

    master = create_master_data(db)

    # Create a second manufacturer.
    second_manufacturer = Manufacturer(
        manufacturer_code="TEST-MF002",
        manufacturer_name="Second Manufacturer",
        country="India",
        website="",
        is_active=True,
    )

    db.add(second_manufacturer)
    db.flush()

    # Keep the product belonging to manufacturer 1,
    # but assign manufacturer 2 to the roll.
    roll = build_media_roll(
        master,
        manufacturer_roll_no=(
            "MISMATCH-MANUFACTURER-001"
        ),
    )

    roll.manufacturer_id = (
        second_manufacturer.id
    )

    db.commit()

    result = MediaRollService.receive(
        db=db,
        media_roll=roll,
        user="TEST",
    )

    assert result.success is False

    assert any(
        "does not match the Manufacturer"
        in error
        for error in result.errors
    )

    db.close()
