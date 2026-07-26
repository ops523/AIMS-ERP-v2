from sqlalchemy.orm import Session

from models.printer import Printer
from models.supplier import Supplier
from models.manufacturer import Manufacturer
from models.warehouse import Warehouse
from models.media_product import MediaProduct
from models.user import User


def seed_database(db: Session):

    # ------------------------
    # Printers
    # ------------------------

    if db.query(Printer).count() == 0:

        db.add_all([
            Printer(
                printer_code="PR001",
                printer_name="SMK Printing",
                city="Delhi",
                state="Delhi",
                print_capacity_day=7500,
                night_shift_capacity=15000,
                is_active=True,
            ),
            Printer(
                printer_code="PR002",
                printer_name="Beta Printers",
                city="Delhi",
                state="Delhi",
                print_capacity_day=15000,
                night_shift_capacity=30000,
                is_active=True,
            ),
        ])

    # ------------------------
    # Warehouses
    # ------------------------

    if db.query(Warehouse).count() == 0:

        db.add(
            Warehouse(
                code="WH001",
                name="Central Warehouse",
            )
        )

    # ------------------------
    # Manufacturers
    # ------------------------

    if db.query(Manufacturer).count() == 0:

        db.add(
            Manufacturer(
                code="MF001",
                name="Demo Manufacturer",
            )
        )

    # ------------------------
    # Suppliers
    # ------------------------

    if db.query(Supplier).count() == 0:

        db.add(
            Supplier(
                supplier_code="SUP001",
                supplier_name="Demo Supplier",
            )
        )

    # ------------------------
    # Media Products
    # ------------------------

    if db.query(MediaProduct).count() == 0:

        db.add(
            MediaProduct(
                code="MP001",
                name="Digital Wall Painting Media",
            )
        )

    db.commit()
