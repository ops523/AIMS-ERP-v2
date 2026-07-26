from sqlalchemy.orm import Session

from models.printer import Printer
from models.supplier import Supplier
from models.manufacturer import Manufacturer
from models.warehouse import Warehouse
from models.media_product import MediaProduct
from models.user import User


def seed_database(db: Session):

    # --------------------------------------------------
    # PRINTERS
    # --------------------------------------------------

    if db.query(Printer).count() == 0:

        db.add_all([
            Printer(
                printer_code="PR001",
                printer_name="SMK Printing",
                city="Mumbai",
                state="Mumbai",
                print_capacity_day=7500,
                night_shift_capacity=15000,
                is_active=True,
            ),
            Printer(
                printer_code="PR002",
                printer_name="Beta Printers",
                city="Mumbai",
                state="Mumbai",
                print_capacity_day=15000,
                night_shift_capacity=30000,
                is_active=True,
            ),
        ])

    # --------------------------------------------------
    # WAREHOUSE
    # --------------------------------------------------

    if db.query(Warehouse).count() == 0:

        db.add(
            Warehouse(
                warehouse_code="WH001",
                warehouse_name="Central Warehouse",
                city="Delhi",
                state="Delhi",
                is_active=True,
            )
        )

    # --------------------------------------------------
    # MANUFACTURER
    # --------------------------------------------------

    manufacturer = db.query(Manufacturer).first()

    if manufacturer is None:

        manufacturer = Manufacturer(
            manufacturer_code="MF001",
            manufacturer_name="Demo Manufacturer",
            country="India",
            website="",
            is_active=True,
        )

        db.add(manufacturer)

        db.commit()
        db.refresh(manufacturer)

    # --------------------------------------------------
    # SUPPLIER
    # --------------------------------------------------

    if db.query(Supplier).count() == 0:

        db.add(
            Supplier(
                supplier_code="SUP001",
                supplier_name="Demo Supplier",
                contact_person="",
                mobile="",
                email="",
                gst_number="",
                address="",
                city="Delhi",
                state="Delhi",
                pincode="110001",
                is_active=True,
            )
        )

    # --------------------------------------------------
    # MEDIA PRODUCT
    # --------------------------------------------------

    if db.query(MediaProduct).count() == 0:

        db.add(
            MediaProduct(
                product_code="MP001",
                manufacturer_id=manufacturer.id,
                product_name="Digital Wall Painting Media",
                width_ft=4.0,
                gsm=300,
                finish="Matte",
                standard_length_m=95,
                is_active=True,
            )
        )

    # --------------------------------------------------
    # ADMIN USER
    # --------------------------------------------------

    if db.query(User).count() == 0:

        db.add(
            User(
                username="admin",
                password_hash="admin",
                full_name="Administrator",
                role="Admin",
                is_active=True,
            )
        )

    db.commit()
