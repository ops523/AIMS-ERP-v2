from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

from database import Base

from models.document_sequence import (
    DocumentSequence,
)

from models.media_roll import (
    MediaRoll,
)

from models.supplier import Supplier
from models.manufacturer import Manufacturer
from models.media_product import MediaProduct
from models.warehouse import Warehouse


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


def create_existing_roll(db, master):

    existing = MediaRoll(

        asset_id="MR-ROLLBACK-EXISTING",

        roll_number="MR-ROLLBACK-DUPLICATE",

        supplier_id=master["supplier"].id,

        manufacturer_id=master["manufacturer"].id,

        product_id=master["product"].id,

        warehouse_id=master["warehouse"].id,

        manufacturer_roll_no="EXISTING-001",

        ordered_length_m=50,

        actual_length_m=50,

        width_ft=4,

        total_sqft=200,

        available_sqft=200,

        status="AVAILABLE",

        is_active=True,
    )

    db.add(existing)

    db.commit()

    return existing
